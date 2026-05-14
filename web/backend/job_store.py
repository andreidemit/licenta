"""Job manager in-process pentru rulările Monte Carlo safe-navigation."""

import json
import logging
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any


TERMINAL_STATUSES = {"completed", "failed", "cancelled"}
logger = logging.getLogger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


class MonteCarloJob:
    """Job live în memorie pentru comparații Monte Carlo safe-navigation."""

    def __init__(self, config: dict[str, Any], job_id: str | None = None):
        self.id = job_id or uuid.uuid4().hex[:12]
        self.config = config
        self.status = "queued"
        self.progress = 0.0
        self.message = "În așteptare"
        self.error = None
        self.events: list[dict[str, Any]] = []
        self.result: dict[str, Any] | None = None
        self.created_at = utc_now()
        self.updated_at = self.created_at
        self._lock = threading.RLock()

    def append_event(self, event: dict[str, Any]) -> None:
        with self._lock:
            self.events.append(event)
            event_type = event.get("type")
            progress = event.get("progress")
            if event_type == "job_finished":
                self.progress = 1.0
                self.message = "Finalizat"
            elif isinstance(progress, dict):
                total = progress.get("total") or 0
                completed = progress.get("completed") or 0
                self.progress = min(0.99, completed / total) if total else self.progress
            if event_type == "job_started":
                self.message = "Monte Carlo pornit"
            elif event_type == "map_started":
                self.message = f"Hartă {event.get('map_index', 0) + 1}/{event.get('map_count', '?')}"
            elif event_type == "agent_started":
                self.message = f"Agent {event.get('agent', 'necunoscut')}"
            elif event_type == "training_progress":
                self.message = (
                    f"Antrenare {event.get('agent', 'Q')}: "
                    f"{event.get('episode', 0)}/{event.get('total_episodes', 0)}"
                )
            elif event_type == "episode_finished":
                self.message = (
                    f"Evaluare {progress.get('completed', 0)}/{progress.get('total', 0)}"
                    if isinstance(progress, dict)
                    else "Episod evaluat"
                )
            elif event_type == "partial_summary":
                self.message = "Dashboard live actualizat"
            elif event_type == "job_failed":
                self.message = "Eșuat"
                self.error = str(event.get("message") or "Eroare necunoscută")
            self.updated_at = utc_now()

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            payload = {
                "id": self.id,
                "status": self.status,
                "progress": self.progress,
                "message": self.message,
                "error": self.error,
                "latest_event": self.events[-1] if self.events else None,
                "config": self.config,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
            }
            if self.result is not None:
                payload["result"] = self.result
            return payload


class MonteCarloJobStore:
    def __init__(self):
        self.jobs: dict[str, MonteCarloJob] = {}
        self._lock = threading.RLock()

    def create(self, config: dict[str, Any], runner) -> MonteCarloJob:
        job = MonteCarloJob(config)
        with self._lock:
            self.jobs[job.id] = job
        thread = threading.Thread(target=self._run_job, args=(job, runner), daemon=True)
        thread.start()
        return job

    def get(self, job_id: str) -> MonteCarloJob | None:
        with self._lock:
            return self.jobs.get(job_id)

    def _run_job(self, job: MonteCarloJob, runner) -> None:
        try:
            with job._lock:
                job.status = "running"
                job.message = "Monte Carlo pornit"
                job.updated_at = utc_now()
            result = runner(job.append_event)
            with job._lock:
                job.result = result
                job.status = "completed"
                job.progress = 1.0
                job.message = "Finalizat"
                job.updated_at = utc_now()
            job.append_event({
                "type": "job_finished",
                "progress": {
                    "completed": result.get("summary", {}).get("episode_count", 0),
                    "total": result.get("summary", {}).get("episode_count", 0),
                },
                "result": result,
            })
        except Exception as exc:
            with job._lock:
                job.status = "failed"
                job.error = str(exc)
                job.message = "Eșuat"
                job.updated_at = utc_now()
            job.append_event({"type": "job_failed", "message": str(exc)})
            logger.exception("monte_carlo_job_failed job_id=%s", job.id)


def stream_monte_carlo_job(job: MonteCarloJob):
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
