"""Rulare Monte Carlo pentru comparația strategiilor de navigare."""

from collections.abc import Callable

from agents import (
    AStarAgent,
    FeatureBasedQLearningAgent,
    RandomAgent,
    RiskAwareAStarAgent,
    RuleBasedAgent,
    TabularQLearningAgent,
)
from environment.grid_world import RewardConfig
from environment.map_generator import MapGenerator, SCENARIOS
from simulation.metrics import aggregate_results
from simulation.simulator import Simulator


def create_agent(algorithm: str, rows: int, cols: int, risk_weight: float = 1.0, seed: int | None = None):
    key = algorithm.lower()
    if key == "random":
        return RandomAgent(random_seed=seed)
    if key in ("rule_based", "rule-based"):
        return RuleBasedAgent(random_seed=seed)
    if key in ("astar", "a*"):
        return AStarAgent()
    if key in ("risk_aware_astar", "risk-aware-a*", "risk_aware_a*", "risk-aware astar"):
        return RiskAwareAStarAgent(risk_weight=risk_weight)
    if key in ("tabular_q", "tabular-q-learning", "tabular q-learning"):
        return TabularQLearningAgent(rows=rows, cols=cols, random_seed=seed)
    if key in ("feature_q", "feature-based-q-learning", "feature q-learning"):
        return FeatureBasedQLearningAgent(random_seed=seed)
    raise ValueError(f"Algoritm necunoscut: {algorithm}")


def _scenario_values(scenario: str, rows: int | None, cols: int | None,
                     wall_probability: float | None, danger_probability: float | None):
    preset = SCENARIOS.get(scenario)
    return {
        "rows": rows or (preset.rows if preset else 15),
        "cols": cols or (preset.cols if preset else 15),
        "wall_probability": wall_probability if wall_probability is not None else (preset.wall_probability if preset else 0.2),
        "danger_probability": danger_probability if danger_probability is not None else (preset.danger_probability if preset else 0.1),
    }


def run_training(agent, env, max_steps: int, episodes: int):
    simulator = Simulator(env, agent, max_steps=max_steps)
    history = []
    for _ in range(episodes):
        history.append(simulator.run_episode(training=True))
    return history


def run_monte_carlo_experiment(
    agents,
    scenario: str = "medium",
    number_of_maps: int = 10,
    episodes_per_map: int = 3,
    training_episodes: int = 100,
    rows: int | None = None,
    cols: int | None = None,
    wall_probability: float | None = None,
    danger_probability: float | None = None,
    movement_noise: float = 0.0,
    risk_weight: float = 1.0,
    max_steps: int = 300,
    random_seed: int = 42,
):
    """Rulează agenți pe hărți generate aleator și returnează metrici agregate."""
    generator = MapGenerator()
    values = _scenario_values(scenario, rows, cols, wall_probability, danger_probability)
    results = []

    for map_index in range(number_of_maps):
        seed = random_seed + map_index * 997
        base_env = generator.generate(
            rows=values["rows"],
            cols=values["cols"],
            wall_probability=values["wall_probability"],
            danger_probability=values["danger_probability"],
            random_seed=seed,
            movement_noise=movement_noise,
            reward_config=RewardConfig(risk_weight=0.0),
        )
        for agent_spec in agents:
            if isinstance(agent_spec, str):
                agent = create_agent(agent_spec, base_env.rows, base_env.cols, risk_weight, seed)
            elif isinstance(agent_spec, Callable):
                agent = agent_spec()
            else:
                agent = agent_spec

            if getattr(agent, "requires_training", False) and training_episodes > 0:
                train_env = generator.generate(
                    rows=values["rows"],
                    cols=values["cols"],
                    wall_probability=values["wall_probability"],
                    danger_probability=values["danger_probability"],
                    random_seed=seed,
                    movement_noise=movement_noise,
                    reward_config=RewardConfig(risk_weight=0.0),
                )
                run_training(agent, train_env, max_steps=max_steps, episodes=training_episodes)

            for _ in range(episodes_per_map):
                eval_env = generator.generate(
                    rows=values["rows"],
                    cols=values["cols"],
                    wall_probability=values["wall_probability"],
                    danger_probability=values["danger_probability"],
                    random_seed=seed,
                    movement_noise=movement_noise,
                    reward_config=RewardConfig(risk_weight=0.0),
                )
                results.append(Simulator(eval_env, agent, max_steps=max_steps).run_episode(training=False))

    return {
        "config": {
            "scenario": scenario,
            "number_of_maps": number_of_maps,
            "episodes_per_map": episodes_per_map,
            "training_episodes": training_episodes,
            "movement_noise": movement_noise,
            "risk_weight": risk_weight,
            **values,
        },
        "summary": aggregate_results(results),
        "episodes": [result.to_dict() for result in results],
    }
