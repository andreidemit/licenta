"""FastAPI app pentru Safe Navigation Simulator."""

import json
import logging
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agents import (
    AStarAgent,
    FeatureBasedQLearningAgent,
    FeatureRiskAwareAStarAgent,
    RandomAgent,
    RiskAwareAStarAgent,
    RuleBasedAgent,
    TabularQLearningAgent,
)
from environment.grid_world import RewardConfig
from environment.map_generator import MapGenerator, SCENARIOS
from experiments.compare_agents import create_agent, run_monte_carlo_experiment, run_training
from simulation.simulator import Simulator
from web.backend.job_store import MonteCarloJobStore, stream_monte_carlo_job
from web.backend.llm_analysis import (
    disabled_response,
    explain_with_llm,
    stream_explain_with_llm,
)
from web.backend.llm_client import LlmClient, LlmClientError
from web.backend.llm_configurator import (
    LlmConfigValidationError,
    configure_with_llm,
    disabled_config_response,
)
from web.backend.llm_episode_analysis import (
    disabled_episode_response,
    explain_episode,
)
from web.backend.llm_map_analysis import disabled_map_response, explain_map
from web.backend.logging_config import configure_logging, log_event
from web.backend.models import (
    EpisodeExplainRequest,
    LlmAnalysisRequest,
    LlmAnalysisResponse,
    LlmConfigRequest,
    LlmConfigResponse,
    MapExplainRequest,
    MonteCarloRequest,
    SafeNavigationRequest,
)
from web.backend.settings import settings


configure_logging()
logger = logging.getLogger(__name__)
app = FastAPI(title="Safe Navigation Simulator API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.allow_cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)
monte_carlo_jobs = MonteCarloJobStore()


def llm_client() -> LlmClient:
    return LlmClient(
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        provider=settings.llm_provider,
        timeout_seconds=settings.llm_timeout_seconds,
        max_output_tokens=settings.llm_max_output_tokens,
    )


@app.on_event("startup")
def log_startup():
    log_event(
        logger,
        "backend_startup",
        app_env=settings.app_env,
        cors_origins=settings.cors_origins,
        application_insights_enabled=bool(settings.applicationinsights_connection_string),
        llm_enabled=settings.llm_enabled,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
    )


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
    "feature_risk_astar": "Feature-Risk A* experimental",
}


ALGORITHM_EXPLANATIONS = {
    "random": RandomAgent().explain(),
    "rule_based": RuleBasedAgent().explain(),
    "astar": AStarAgent().explain(),
    "risk_aware_astar": RiskAwareAStarAgent().explain(),
    "tabular_q": TabularQLearningAgent(rows=5, cols=5).explain(),
    "feature_q": FeatureBasedQLearningAgent().explain(),
    "feature_risk_astar": FeatureRiskAwareAStarAgent().explain(),
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
        result = run_monte_carlo_request(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


def run_monte_carlo_request(request: MonteCarloRequest, progress_callback=None):
    return run_monte_carlo_experiment(
        agents=request.algorithms,
        scenario=request.scenario,
        experiment_profile=request.experiment_profile,
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
        optimization_objective=request.optimization_objective,
        progress_callback=progress_callback,
    )


@app.post("/api/safe-navigation/monte-carlo/jobs")
def start_safe_navigation_monte_carlo_job(request: MonteCarloRequest):
    config = request.model_dump()
    job = monte_carlo_jobs.create(
        config,
        lambda progress_callback: run_monte_carlo_request(request, progress_callback=progress_callback),
    )
    log_event(
        logger,
        "monte_carlo_job_created",
        run_id=job.id,
        scenario=request.scenario,
        profile=request.experiment_profile,
        maps=request.number_of_maps,
        episodes_per_map=request.episodes_per_map,
        algorithms=request.algorithms,
    )
    return job.snapshot()


@app.get("/api/safe-navigation/monte-carlo/jobs/{job_id}")
def get_safe_navigation_monte_carlo_job(job_id: str):
    job = monte_carlo_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Rularea Monte Carlo nu a fost găsită")
    return job.snapshot()


@app.get("/api/safe-navigation/monte-carlo/jobs/{job_id}/stream")
def stream_safe_navigation_monte_carlo_job(job_id: str):
    job = monte_carlo_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Rularea Monte Carlo nu a fost găsită")
    return StreamingResponse(stream_monte_carlo_job(job), media_type="text/event-stream")


@app.get("/api/safe-navigation/analysis/status")
def safe_navigation_analysis_status():
    if not settings.llm_enabled:
        return {
            "enabled": False,
            "available": False,
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "base_url": settings.llm_base_url,
            "message": "Analistul AI este dezactivat. Setează LLM_ENABLED=true pentru activare.",
        }
    try:
        health = llm_client().health()
    except LlmClientError as exc:
        return {
            "enabled": True,
            "available": False,
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "base_url": settings.llm_base_url,
            "message": f"LLM indisponibil: {exc}",
        }
    return {
        "enabled": True,
        "available": health["available"],
        "provider": health["provider"],
        "model": health["model"],
        "base_url": health["base_url"],
        "models": health["models"],
        "message": health["message"],
    }


@app.post("/api/safe-navigation/analysis/explain", response_model=LlmAnalysisResponse)
def safe_navigation_analysis_explain(request: LlmAnalysisRequest):
    if not settings.llm_enabled:
        return disabled_response(model=settings.llm_model, provider=settings.llm_provider)
    try:
        return explain_with_llm(
            request,
            client=llm_client(),
            max_input_chars=settings.llm_max_input_chars,
        )
    except LlmClientError as exc:
        raise HTTPException(status_code=503, detail=f"Analistul AI nu este disponibil: {exc}") from exc


def _sse_stream_text(text: str, delay: float = 0.025):
    """Emite text token cu token ca Server-Sent Events (folosit doar pentru fallback)."""
    words = text.split()
    for i, word in enumerate(words):
        token = word + (" " if i < len(words) - 1 else "")
        yield f"data: {json.dumps({'token': token})}\n\n"
        if delay > 0:
            time.sleep(delay)
    yield f"data: {json.dumps({'done': True})}\n\n"


def _sse_stream_llm(request: LlmAnalysisRequest):
    """Iterează tokenii LLM reali și îi emite ca SSE."""
    try:
        for token in stream_explain_with_llm(
            request,
            client=llm_client(),
            max_input_chars=settings.llm_max_input_chars,
        ):
            yield f"data: {json.dumps({'token': token})}\n\n"
    except LlmClientError as exc:
        yield f"data: {json.dumps({'error': f'Analistul AI nu este disponibil: {exc}'})}\n\n"
        return
    except Exception as exc:  # pragma: no cover - defensiv
        yield f"data: {json.dumps({'error': str(exc)})}\n\n"
        return
    yield f"data: {json.dumps({'done': True})}\n\n"


@app.post("/api/safe-navigation/analysis/explain/stream")
def safe_navigation_analysis_explain_stream(request: LlmAnalysisRequest):
    if not settings.llm_enabled:
        fallback = disabled_response(model=settings.llm_model, provider=settings.llm_provider)
        return StreamingResponse(
            _sse_stream_text(fallback.answer, delay=0.0),
            media_type="text/event-stream",
        )
    return StreamingResponse(_sse_stream_llm(request), media_type="text/event-stream")


@app.post("/api/safe-navigation/episode/explain", response_model=LlmAnalysisResponse)
def safe_navigation_episode_explain(request: EpisodeExplainRequest):
    if not settings.llm_enabled:
        return disabled_episode_response(model=settings.llm_model, provider=settings.llm_provider)
    try:
        return explain_episode(
            result=request.result,
            algorithm=request.algorithm,
            config=request.config,
            client=llm_client(),
            language=request.language,
        )
    except LlmClientError as exc:
        raise HTTPException(status_code=503, detail=f"Analistul AI nu este disponibil: {exc}") from exc


@app.post("/api/safe-navigation/map/explain", response_model=LlmAnalysisResponse)
def safe_navigation_map_explain(request: MapExplainRequest):
    if not settings.llm_enabled:
        return disabled_map_response(model=settings.llm_model, provider=settings.llm_provider)
    try:
        return explain_map(
            environment=request.environment,
            config=request.config,
            client=llm_client(),
            language=request.language,
        )
    except LlmClientError as exc:
        raise HTTPException(status_code=503, detail=f"Analistul AI nu este disponibil: {exc}") from exc


@app.post("/api/safe-navigation/analysis/configure", response_model=LlmConfigResponse)
def safe_navigation_analysis_configure(request: LlmConfigRequest):
    if not settings.llm_enabled:
        return disabled_config_response(
            model=settings.llm_model,
            provider=settings.llm_provider,
            current_config=request.current_config,
        )
    try:
        return configure_with_llm(request, client=llm_client())
    except LlmConfigValidationError as exc:
        raise HTTPException(status_code=422, detail=f"Configurația propusă de LLM nu este validă: {exc}") from exc
    except LlmClientError as exc:
        raise HTTPException(status_code=503, detail=f"Asistentul de configurare AI nu este disponibil: {exc}") from exc
