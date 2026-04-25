"""
Servicii reutilizabile pentru CLI și UI web.

Acest modul păstrează motorul RL în Python, dar îl expune prin funcții
serializabile care pot fi folosite de FastAPI.
"""

import os
from dataclasses import dataclass, field
from typing import Callable, Optional

from src.analytics import Analytics
from src.constants import ENERGY_MAX, SCENARIO_C_SWITCH_EPISODE
from src.environment import Environment
from src.q_learning import QLearning
from src.serialization import (
    serialize_environment,
    serialize_episode_result,
    serialize_live_info,
    serialize_q_stats,
)
from src.static_environment import StaticEnvironment
from src.trainer import Trainer
from src.warehouse_scenario import WarehouseEnvironment


ENERGY_INFINITE = 999999


@dataclass
class SimulationConfig:
    scenario: str = "B"
    rows: int = 20
    cols: int = 20
    seed: int = 42
    episodes: int = 2000
    energy: Optional[int] = None
    alpha: float = 0.1
    gamma: float = 0.95
    max_steps: Optional[int] = None
    out_dir: str = "data/runs"


@dataclass
class TrainingBundle:
    run_id: str
    config: SimulationConfig
    environment: object
    q_learner: QLearning
    trainer: Trainer
    history: list = field(default_factory=list)
    artifacts: dict = field(default_factory=dict)


def build_environment(config: SimulationConfig):
    if config.scenario == "WAREHOUSE":
        return WarehouseEnvironment()
    return Environment(rows=config.rows, cols=config.cols, seed=config.seed)


def build_static_environment(payload: dict):
    return StaticEnvironment(
        grid=payload["grid"],
        start_pos=payload["start"],
        target_pos=payload["target"],
        name=payload.get("name", "personalizat"),
    )


def initial_energy(config: SimulationConfig):
    if config.energy is not None:
        return config.energy
    if config.scenario == "A":
        return ENERGY_INFINITE
    return ENERGY_MAX


def create_training_bundle(run_id: str, config: SimulationConfig) -> TrainingBundle:
    env = build_environment(config)
    q = QLearning(
        rows=env.rows,
        cols=env.cols,
        alpha=config.alpha,
        gamma=config.gamma,
    )
    trainer = Trainer(env, q, energy=initial_energy(config))
    if config.max_steps is not None:
        trainer.max_steps = config.max_steps
    return TrainingBundle(
        run_id=run_id,
        config=config,
        environment=env,
        q_learner=q,
        trainer=trainer,
    )


def train_bundle(bundle: TrainingBundle,
                 on_event: Optional[Callable[[dict], None]] = None) -> TrainingBundle:
    """Rulează training și emite evenimente JSON-friendly."""
    config = bundle.config

    def render_callback(env, agent, info):
        if on_event is None:
            return
        on_event({
            "type": "step",
            "run_id": bundle.run_id,
            "environment": serialize_environment(env),
            "agent": {
                "position": list(agent.position),
                "energy": agent.energy,
                "energy_percent": agent.energy_percent,
                "steps": agent.total_steps,
                "reward": agent.total_reward,
                "alive": agent.is_alive,
                "reached_target": agent.reached_target,
            },
            "q": serialize_q_stats(bundle.q_learner),
            "info": serialize_live_info(info),
        })

    history = bundle.trainer.train(
        num_episodes=config.episodes,
        print_every=0,
        render_callback=render_callback if on_event else None,
        scenario_c_switch=SCENARIO_C_SWITCH_EPISODE if config.scenario == "C" else None,
    )
    bundle.history = history
    if on_event is not None:
        on_event({
            "type": "training_complete",
            "run_id": bundle.run_id,
            "history_tail": [serialize_episode_result(ep) for ep in history[-20:]],
            "q": serialize_q_stats(bundle.q_learner),
        })
    return bundle


def export_bundle(bundle: TrainingBundle) -> dict:
    """Exportă artefactele standard pentru o rulare web."""
    run_dir = os.path.join(bundle.config.out_dir, bundle.run_id)
    os.makedirs(run_dir, exist_ok=True)
    analytics = Analytics(
        scenario=bundle.config.scenario,
        grid_size=bundle.environment.rows,
        seed=0 if bundle.config.scenario == "WAREHOUSE" else bundle.config.seed,
        out_dir=run_dir,
    )
    csv_path = analytics.export_csv(bundle.history)
    plots = analytics.save_all_plots(bundle.history)
    qtable_path = os.path.join(run_dir, "qtable.npy")
    bundle.q_learner.save(qtable_path)
    agent, outcome, trajectory = bundle.trainer.run_greedy_trajectory()
    trajectory_csv, trajectory_json = analytics.export_greedy_trajectory(
        trajectory,
        summary={
            "outcome": outcome,
            "steps": agent.total_steps,
            "reward": agent.total_reward,
            "energy_remaining": agent.energy,
            "bfs_distance": bundle.environment.bfs(
                bundle.environment.start_pos,
                bundle.environment.target_pos,
            ),
        },
    )
    visuals = analytics.save_visual_artifacts(
        bundle.environment,
        bundle.q_learner,
        trajectory=trajectory,
    )
    artifacts = {
        "results_csv": csv_path,
        "convergence_png": plots[0],
        "epsilon_png": plots[1],
        "success_png": plots[2],
        "qtable_path": qtable_path,
        "greedy_trajectory_csv": trajectory_csv,
        "greedy_trajectory_json": trajectory_json,
        **visuals,
    }
    manifest_path = analytics.export_run_manifest(
        bundle.history,
        bundle.environment,
        bundle.q_learner,
        artifacts=artifacts,
        greedy_summary={
            "outcome": outcome,
            "steps": agent.total_steps,
            "reward": agent.total_reward,
            "energy_remaining": agent.energy,
        },
        energy=initial_energy(bundle.config),
    )
    artifacts["manifest_json"] = manifest_path
    bundle.artifacts = artifacts
    return artifacts


def evaluate_qtable_on_environment(qtable_path: str, environment_payload: dict,
                                   energy: int = ENERGY_MAX) -> dict:
    env = build_static_environment(environment_payload)
    q = QLearning(rows=env.rows, cols=env.cols)
    q.load(qtable_path)
    trainer = Trainer(env, q, energy=energy)
    agent, outcome, trajectory = trainer.run_greedy_trajectory()
    bfs_distance = env.bfs(env.start_pos, env.target_pos)
    return {
        "environment": serialize_environment(env, environment_payload.get("id"), environment_payload.get("name")),
        "outcome": outcome,
        "steps": agent.total_steps,
        "reward": agent.total_reward,
        "energy_remaining": agent.energy,
        "bfs_distance": bfs_distance,
        "bfs_overhead": agent.total_steps - bfs_distance if bfs_distance is not None else None,
        "trajectory": trajectory,
    }
