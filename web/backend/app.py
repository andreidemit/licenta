"""FastAPI app pentru training/evaluare Q-Learning."""

import glob
import json
import os
import re
import uuid
from dataclasses import asdict
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse

from src.environment import Environment
from src.serialization import serialize_environment
from src.simulation_service import (
    SimulationConfig,
    build_static_environment,
    evaluate_qtable_on_environment,
)
from src.warehouse_scenario import WarehouseEnvironment
from web.backend.job_store import JobStore, stream_job
from web.backend.models import EnvironmentPayload, EvaluateRequest, TrainRequest


app = FastAPI(title="API Laborator Q-Learning", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
jobs = JobStore()
RUNS_ROOT = Path("data/runs").resolve()
ENVIRONMENTS_ROOT = Path("data/environments").resolve()


def artifact_items(job_id: str, artifacts: dict[str, str]) -> list[dict[str, object]]:
    items = []
    for key, value in sorted(artifacts.items()):
        path = Path(value)
        exists = path.exists()
        items.append({
            "key": key,
            "path": value,
            "exists": exists,
            "size_bytes": path.stat().st_size if exists and path.is_file() else None,
            "download_url": f"/api/runs/{job_id}/artifacts/{key}/download",
        })
    return items


def safe_artifact_path(job_id: str, artifact_key: str) -> Path:
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Rularea nu a fost găsită")
    path_value = job.snapshot()["artifacts"].get(artifact_key)
    if path_value is None:
        raise HTTPException(status_code=404, detail="Artefactul nu a fost găsit")
    path = Path(path_value).resolve()
    try:
        path.relative_to(RUNS_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Calea artefactului este în afara data/runs") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Fișierul artefactului nu a fost găsit")
    return path


def environment_id(value: str | None) -> str:
    candidate = value or f"personalizat_{uuid.uuid4().hex[:8]}"
    candidate = re.sub(r"[^a-zA-Z0-9_.-]+", "_", candidate).strip("._-")
    return candidate or f"personalizat_{uuid.uuid4().hex[:8]}"


def environment_path(environment_id_value: str) -> Path:
    path = (ENVIRONMENTS_ROOT / f"{environment_id(environment_id_value)}.json").resolve()
    try:
        path.relative_to(ENVIRONMENTS_ROOT)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="ID de mediu invalid") from exc
    return path


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/scenarios")
def scenarios():
    return {
        "scenarios": [
            {"id": "A", "name": "Navigare cu energie infinită"},
            {"id": "B", "name": "Supraviețuire cu energie limitată"},
            {"id": "C", "name": "Mediu dinamic"},
            {"id": "WAREHOUSE", "name": "Depozit industrial"},
        ]
    }


@app.get("/api/environments/preview")
def environment_preview(scenario: str = "B", rows: int = 20, cols: int = 20, seed: int = 42):
    if scenario == "WAREHOUSE":
        env = WarehouseEnvironment()
        return serialize_environment(env, environment_id="warehouse", name="Depozit")
    try:
        env = Environment(rows=rows, cols=cols, seed=seed)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_environment(env, environment_id=f"{scenario}_{rows}_{cols}_{seed}")


@app.get("/api/evaluation-scenarios")
def evaluation_scenarios():
    presets = [
        {
            "id": "control_seed_42",
            "name": "Hartă de control",
            "description": "Hartă procedurală 20×20 cu seed 42. Este utilă ca reper față de o rulare de antrenare standard.",
            "environment": serialize_environment(
                Environment(rows=20, cols=20, seed=42),
                environment_id="control_seed_42",
                name="Hartă de control",
            ),
        },
        {
            "id": "new_seed_77",
            "name": "Hartă nouă",
            "description": "Mediu procedural diferit, cu obstacole și resurse în alte poziții. Testează robustețea politicii tabulare.",
            "environment": serialize_environment(
                Environment(rows=20, cols=20, seed=77),
                environment_id="new_seed_77",
                name="Hartă nouă",
            ),
        },
        {
            "id": "dense_seed_123",
            "name": "Hartă dificilă",
            "description": "Mediu procedural cu alt seed, bun pentru a observa dacă agentul se blochează sau găsește o rută utilă.",
            "environment": serialize_environment(
                Environment(rows=20, cols=20, seed=123),
                environment_id="dense_seed_123",
                name="Hartă dificilă",
            ),
        },
        {
            "id": "warehouse_fixed",
            "name": "Depozit industrial",
            "description": "Scenariu fix de depozit 20×20. Are structură mai apropiată de un mediu construit manual.",
            "environment": serialize_environment(
                WarehouseEnvironment(),
                environment_id="warehouse_fixed",
                name="Depozit industrial",
            ),
        },
    ]
    return {"scenarios": presets}


@app.get("/api/environments")
def list_environments():
    ENVIRONMENTS_ROOT.mkdir(parents=True, exist_ok=True)
    environments = []
    for path in sorted(ENVIRONMENTS_ROOT.glob("*.json")):
        try:
            with open(path, "r", encoding="utf-8") as file:
                payload = json.load(file)
            env = build_static_environment(payload)
        except (OSError, json.JSONDecodeError, ValueError, KeyError):
            continue
        environments.append({
            "id": payload.get("id") or path.stem,
            "name": payload.get("name", path.stem),
            "rows": env.rows,
            "cols": env.cols,
            "bfs_distance": env.bfs(env.start_pos, env.target_pos),
            "path": str(path),
        })
    return {"environments": environments}


@app.get("/api/environments/{custom_environment_id}")
def get_environment(custom_environment_id: str):
    path = environment_path(custom_environment_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Mediul nu a fost găsit")
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    env = build_static_environment(payload)
    return serialize_environment(
        env,
        environment_id=payload.get("id") or path.stem,
        name=payload.get("name", path.stem),
    )


@app.post("/api/environments/validate")
def validate_environment(environment: EnvironmentPayload):
    try:
        env = build_static_environment(environment.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "valid": True,
        "environment": serialize_environment(
            env,
            environment_id=environment.id,
            name=environment.name,
        ),
    }


@app.post("/api/environments")
def save_environment(environment: EnvironmentPayload):
    try:
        env = build_static_environment(environment.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ENVIRONMENTS_ROOT.mkdir(parents=True, exist_ok=True)
    payload = environment.model_dump()
    payload["id"] = environment_id(environment.id or environment.name)
    path = environment_path(payload["id"])
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, ensure_ascii=False)
    return {
        "saved": True,
        "path": str(path),
        "environment": serialize_environment(
            env,
            environment_id=payload["id"],
            name=payload.get("name"),
        ),
    }


@app.post("/api/train")
def start_training(request: TrainRequest):
    config = SimulationConfig(**request.model_dump())
    job = jobs.create(config)
    return job.snapshot()


@app.get("/api/runs")
def list_runs():
    return {"runs": jobs.list()}


@app.get("/api/runs/{job_id}")
def get_run(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Rularea nu a fost găsită")
    return job.snapshot()


@app.get("/api/runs/{job_id}/artifacts")
def get_run_artifacts(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Rularea nu a fost găsită")
    artifacts = job.snapshot()["artifacts"]
    return {
        "artifacts": artifacts,
        "items": artifact_items(job_id, artifacts),
    }


@app.get("/api/runs/{job_id}/artifacts/{artifact_key}/download")
def download_run_artifact(job_id: str, artifact_key: str):
    path = safe_artifact_path(job_id, artifact_key)
    return FileResponse(path, filename=path.name)


@app.get("/api/qtables")
def list_qtables():
    paths = sorted(glob.glob(os.path.join("data", "runs", "*", "qtable.npy")))
    return {
        "qtables": [
            {
                "path": path,
                "run_id": os.path.basename(os.path.dirname(path)),
                "download_url": f"/api/runs/{os.path.basename(os.path.dirname(path))}/artifacts/qtable_path/download",
            }
            for path in paths
        ]
    }


@app.get("/api/stream/{job_id}")
def stream_run(job_id: str):
    job = jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Rularea nu a fost găsită")
    return StreamingResponse(stream_job(job), media_type="text/event-stream")


@app.post("/api/evaluate")
def evaluate(request: EvaluateRequest):
    try:
        results = [
            evaluate_qtable_on_environment(
                qtable_path=request.qtable_path,
                environment_payload=environment.model_dump(),
                energy=request.energy,
            )
            for environment in request.environments
        ]
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"results": results}


@app.get("/api/config/defaults")
def defaults():
    return asdict(SimulationConfig())
