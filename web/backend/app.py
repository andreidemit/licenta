"""FastAPI app pentru training/evaluare Q-Learning."""

import json
import logging
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
from agents import (
    AStarAgent,
    FeatureBasedQLearningAgent,
    RandomAgent,
    RiskAwareAStarAgent,
    RuleBasedAgent,
    SarsaAgent,
    TabularQLearningAgent,
)
from environment.grid_world import RewardConfig
from environment.map_generator import MapGenerator, SCENARIOS
from experiments.compare_agents import create_agent, run_monte_carlo_experiment, run_training
from simulation.simulator import Simulator
from web.backend.job_store import JobStore, stream_job
from web.backend.logging_config import configure_logging, log_event
from web.backend.models import (
    EnvironmentPayload,
    EvaluateRequest,
    MonteCarloRequest,
    SafeNavigationRequest,
    TrainRequest,
)
from web.backend.settings import settings


configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="API Laborator Q-Learning", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.allow_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
RUNS_ROOT = settings.runs_root
ENVIRONMENTS_ROOT = settings.environments_root
jobs = JobStore(index_path=RUNS_ROOT / "index.json")


@app.on_event("startup")
def log_startup():
    log_event(
        logger,
        "backend_startup",
        app_env=settings.app_env,
        data_root=str(settings.data_root),
        runs_root=str(RUNS_ROOT),
        environments_root=str(ENVIRONMENTS_ROOT),
        cors_origins=settings.cors_origins,
        application_insights_enabled=bool(settings.applicationinsights_connection_string),
    )


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
        log_event(logger, "artifact_download_missing_key", run_id=job_id, artifact_key=artifact_key)
        raise HTTPException(status_code=404, detail="Artefactul nu a fost găsit")
    path = Path(path_value).resolve()
    try:
        path.relative_to(RUNS_ROOT)
    except ValueError as exc:
        log_event(
            logger,
            "artifact_download_rejected_path",
            run_id=job_id,
            artifact_key=artifact_key,
            path=str(path),
        )
        raise HTTPException(status_code=400, detail="Calea artefactului este în afara directorului de rulări") from exc
    if not path.is_file():
        log_event(
            logger,
            "artifact_download_missing_file",
            run_id=job_id,
            artifact_key=artifact_key,
            path=str(path),
        )
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


ALGORITHM_LABELS = {
    "random": "Aleator",
    "rule_based": "Bazat pe reguli",
    "astar": "A*",
    "risk_aware_astar": "A* conștient de risc",
    "tabular_q": "Q-Learning tabular",
    "feature_q": "Q-Learning pe trăsături",
    "sarsa": "SARSA tabular",
}


ALGORITHM_EXPLANATIONS = {
    "random": RandomAgent().explain(),
    "rule_based": RuleBasedAgent().explain(),
    "astar": AStarAgent().explain(),
    "risk_aware_astar": RiskAwareAStarAgent().explain(),
    "tabular_q": TabularQLearningAgent(rows=5, cols=5).explain(),
    "feature_q": FeatureBasedQLearningAgent().explain(),
    "sarsa": SarsaAgent(rows=5, cols=5).explain(),
}


def _safe_world_from_request(request: SafeNavigationRequest):
    generator = MapGenerator()
    preset = SCENARIOS.get(request.scenario)
    rows = request.rows if request.scenario == "custom" else (preset.rows if preset else request.rows)
    cols = request.cols if request.scenario == "custom" else (preset.cols if preset else request.cols)
    wall_probability = (
        request.wall_probability
        if request.scenario == "custom"
        else (preset.wall_probability if preset else request.wall_probability)
    )
    danger_probability = (
        request.danger_probability
        if request.scenario == "custom"
        else (preset.danger_probability if preset else request.danger_probability)
    )
    return generator.generate(
        rows=rows,
        cols=cols,
        wall_probability=wall_probability,
        danger_probability=danger_probability,
        random_seed=request.random_seed,
        movement_noise=request.movement_noise,
        reward_config=RewardConfig(risk_weight=request.risk_weight),
    )


@app.get("/api/safe-navigation/status")
def safe_navigation_status():
    return {
        "status": "ok",
        "algorithms": [
            {
                "id": key,
                "name": ALGORITHM_LABELS[key],
                "explanation": ALGORITHM_EXPLANATIONS[key],
            }
            for key in ALGORITHM_LABELS
        ],
        "scenarios": [
            {"id": key, **config.__dict__}
            for key, config in SCENARIOS.items()
        ],
        "defaults": SafeNavigationRequest().model_dump(),
    }


@app.get("/api/safe-navigation/algorithms")
def safe_navigation_algorithms():
    return {
        "algorithms": [
            {"id": key, "name": ALGORITHM_LABELS[key], "explanation": value}
            for key, value in ALGORITHM_EXPLANATIONS.items()
        ],
        "scenarios": [
            {"id": key, **config.__dict__}
            for key, config in SCENARIOS.items()
        ],
    }


@app.post("/api/safe-navigation/preview")
def safe_navigation_preview(request: SafeNavigationRequest):
    try:
        env = _safe_world_from_request(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"environment": env.to_payload(), "algorithm_explanation": ALGORITHM_EXPLANATIONS.get(request.algorithm, "")}


@app.post("/api/safe-navigation/episode")
def safe_navigation_episode(request: SafeNavigationRequest):
    try:
        env = _safe_world_from_request(request)
        agent = create_agent(request.algorithm, env.rows, env.cols, request.risk_weight, request.random_seed)
        training_history = []
        if getattr(agent, "requires_training", False) and request.training_episodes > 0:
            training_history = run_training(agent, env, max_steps=request.max_steps, episodes=request.training_episodes)
        result = Simulator(env, agent, max_steps=request.max_steps).run_episode(training=False)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "environment": env.to_payload(),
        "result": result.to_dict(),
        "training_history": [item.to_dict() for item in training_history[-50:]],
        "algorithm_explanation": agent.explain(),
    }


@app.post("/api/safe-navigation/monte-carlo")
def safe_navigation_monte_carlo(request: MonteCarloRequest):
    try:
        result = run_monte_carlo_experiment(
            agents=request.algorithms,
            scenario=request.scenario,
            number_of_maps=request.number_of_maps,
            episodes_per_map=request.episodes_per_map,
            training_episodes=request.training_episodes,
            rows=request.rows if request.scenario == "custom" else None,
            cols=request.cols if request.scenario == "custom" else None,
            wall_probability=request.wall_probability if request.scenario == "custom" else None,
            danger_probability=request.danger_probability if request.scenario == "custom" else None,
            movement_noise=request.movement_noise,
            risk_weight=request.risk_weight,
            max_steps=request.max_steps,
            random_seed=request.random_seed,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


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
    config = SimulationConfig(**request.model_dump(), out_dir=str(RUNS_ROOT))
    job = jobs.create(config)
    log_event(
        logger,
        "training_job_created",
        run_id=job.id,
        scenario=config.scenario,
        rows=config.rows,
        cols=config.cols,
        episodes=config.episodes,
        out_dir=config.out_dir,
    )
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
    paths = sorted(RUNS_ROOT.glob("*/qtable.npy"))
    return {
        "qtables": [
            {
                "path": str(path),
                "run_id": path.parent.name,
                "download_url": f"/api/runs/{path.parent.name}/artifacts/qtable_path/download",
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
        log_event(
            logger,
            "evaluation_failed",
            qtable_path=request.qtable_path,
            environment_count=len(request.environments),
            error=str(exc),
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"results": results}


@app.get("/api/config/defaults")
def defaults():
    return asdict(SimulationConfig())
