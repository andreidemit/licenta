"""Job manager in-process pentru training web."""

import json
import os
import threading
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from src.simulation_service import (
    SimulationConfig,
    create_training_bundle,
    export_bundle,
    train_bundle,
)


TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TrainingJob:
    def __init__(self, config: SimulationConfig, job_id: str | None = None):
        self.id = job_id or uuid.uuid4().hex[:12]
        self.config = config
        self.status = "queued"
        self.progress = 0.0
        self.message = "În așteptare"
        self.error = None
        self.events: list[dict[str, Any]] = []
        self.artifacts: dict[str, str] = {}
        self.bundle = None
        self.created_at = utc_now()
        self.updated_at = self.created_at
        self._lock = threading.RLock()

    def append_event(self, event: dict[str, Any]) -> None:
        with self._lock:
            self.events.append(event)
            if event.get("type") == "step":
                live = event.get("info", {}).get("live", {})
                max_steps = live.get("max_steps") or 1
                step = live.get("step") or 0
                episode = event.get("info", {}).get("Episod", 0)
                episode_progress = min(1.0, (step + 1) / max_steps)
                self.progress = min(
                    0.99,
                    (episode + episode_progress) / max(1, self.config.episodes),
                )
                self.message = f"Episod {episode + 1}/{self.config.episodes}"
            elif event.get("type") == "training_complete":
                self.progress = 1.0
                self.message = "Antrenare finalizată"
            self.updated_at = utc_now()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "id": self.id,
                "status": self.status,
                "scenario": self.config.scenario,
                "progress": self.progress,
                "message": self.message,
                "artifacts": self.artifacts,
                "error": self.error,
                "latest_event": self.events[-1] if self.events else None,
                "config": asdict(self.config),
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }

    @classmethod
    def from_snapshot(cls, snapshot: dict[str, Any]) -> "TrainingJob":
        job = cls(
            SimulationConfig(**snapshot.get("config", {})),
            job_id=snapshot["id"],
        )
        job.status = snapshot.get("status", "completed")
        job.progress = float(snapshot.get("progress", 1.0))
        job.message = snapshot.get("message", "")
        job.error = snapshot.get("error")
        job.artifacts = dict(snapshot.get("artifacts", {}))
        job.created_at = snapshot.get("created_at", utc_now())
        job.updated_at = snapshot.get("updated_at", job.created_at)
        if job.status not in TERMINAL_STATUSES:
            job.status = "failed"
            job.error = "Backend-ul a fost repornit cât timp acest job era activ."
            job.message = "Întrerupt de repornirea backend-ului"
            job.updated_at = utc_now()
        return job


class JobStore:
    def __init__(self, index_path: str = os.path.join("data", "runs", "index.json")):
        self.index_path = index_path
        self.jobs: dict[str, TrainingJob] = {}
        self._lock = threading.RLock()
        self._load_index()

    def create(self, config: SimulationConfig) -> TrainingJob:
        job = TrainingJob(config)
        with self._lock:
            self.jobs[job.id] = job
            self._save_index_locked()
        thread = threading.Thread(target=self._run_job, args=(job,), daemon=True)
        thread.start()
        return job

    def list(self):
        with self._lock:
            return sorted(
                [job.snapshot() for job in self.jobs.values()],
                key=lambda item: item.get("created_at", ""),
                reverse=True,
            )

    def get(self, job_id: str) -> TrainingJob | None:
        with self._lock:
            return self.jobs.get(job_id)

    def _run_job(self, job: TrainingJob) -> None:
        try:
            job.status = "running"
            job.message = "Antrenare pornită"
            job.updated_at = utc_now()
            bundle = create_training_bundle(job.id, job.config)
            job.bundle = bundle
            train_bundle(bundle, on_event=job.append_event)
            job.artifacts = export_bundle(bundle)
            job.status = "completed"
            job.progress = 1.0
            job.message = "Finalizat"
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            job.message = "Eșuat"
            job.append_event({"type": "error", "message": str(exc)})
        finally:
            job.updated_at = utc_now()
            with self._lock:
                self._save_index_locked()

    def _load_index(self) -> None:
        if not os.path.exists(self.index_path):
            return
        with open(self.index_path, "r", encoding="utf-8") as file:
            payload = json.load(file)
        for snapshot in payload.get("runs", []):
            try:
                job = TrainingJob.from_snapshot(snapshot)
            except (KeyError, TypeError, ValueError):
                continue
            self.jobs[job.id] = job

    def _save_index_locked(self) -> None:
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        payload = {"runs": [job.snapshot() for job in self.jobs.values()]}
        tmp_path = f"{self.index_path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.index_path)


def sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


def stream_job(job: TrainingJob):
    index = 0
    while True:
        with job._lock:
            events = job.events[index:]
            index = len(job.events)
            status = job.status
            snapshot = job.snapshot()
        for event in events:
            yield sse_event(event)
        yield sse_event({"type": "job_status", **snapshot})
        if status in TERMINAL_STATUSES:
            break
        time.sleep(0.5)
