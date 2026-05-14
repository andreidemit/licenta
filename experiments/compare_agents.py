"""Rulare Monte Carlo pentru comparația strategiilor de navigare."""

from collections.abc import Callable

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
from experiments.recommendation import build_recommendation
from simulation.metrics import aggregate_results
from simulation.simulator import Simulator


EXPERIMENT_PROFILES = {
    "known_static": {
        "id": "known_static",
        "label": "Hartă cunoscută, mediu static",
        "description": "Cazul ideal pentru planificare: hartă complet cunoscută, costuri explicite și acțiuni deterministe.",
        "assumption": "Agentul are model complet al mediului înainte de decizie.",
        "expected_takeaway": "A* este alegerea naturală când mediul este cunoscut și static.",
        "favored_algorithms": ["astar", "risk_aware_astar"],
        "protocol": "Evaluare Monte Carlo clasică pe hărți generate, cunoscute integral agentului.",
        "agent_lifecycle": "per_map",
    },
    "high_risk": {
        "id": "high_risk",
        "label": "Risc ridicat",
        "description": "Crește importanța expunerii la risc față de lungimea traseului.",
        "assumption": "Siguranța este obiectiv explicit, nu doar un efect secundar.",
        "expected_takeaway": "A* conștient de risc este preferabil când traseul scurt traversează zone periculoase.",
        "favored_algorithms": ["risk_aware_astar"],
        "protocol": "Evaluare Monte Carlo cu pondere de risc mai mare în recompensă și cost.",
        "agent_lifecycle": "per_map",
    },
    "stochastic_execution": {
        "id": "stochastic_execution",
        "label": "Execuție incertă",
        "description": "Acțiunile pot devia lateral, deci planul optim nu este executat perfect.",
        "assumption": "Agentul trebuie evaluat prin robustețe la zgomot, coliziuni și risc acumulat.",
        "expected_takeaway": "Planificarea rămâne puternică, dar comparația trebuie citită prin robustețe, nu doar pași.",
        "favored_algorithms": ["risk_aware_astar", "feature_q", "feature_risk_astar"],
        "protocol": "Evaluare Monte Carlo cu tranziții stocastice controlate de movement_noise.",
        "agent_lifecycle": "per_map",
    },
    "same_map_learning": {
        "id": "same_map_learning",
        "label": "Învățare pe aceeași hartă",
        "description": "Agenții Q sunt antrenați pe aceeași hartă pe care sunt evaluați.",
        "assumption": "Mediul se repetă și agentul poate acumula experiență înainte de test.",
        "expected_takeaway": "Q-learning tabular devine relevant când coordonatele învățate rămân valabile.",
        "favored_algorithms": ["tabular_q", "feature_q"],
        "protocol": "Training pe seed-ul hărții evaluate, apoi evaluare greedy pe aceeași hartă.",
        "agent_lifecycle": "per_map",
    },
    "transfer_learning": {
        "id": "transfer_learning",
        "label": "Transfer pe hărți noi",
        "description": "Separă seed-urile de training de seed-urile de evaluare.",
        "assumption": "Agentul trebuie să transfere tipare învățate pe hărți nevăzute.",
        "expected_takeaway": "Q-learning pe trăsături este mai potrivit pentru transfer decât Q-learning tabular.",
        "favored_algorithms": ["feature_q", "feature_risk_astar"],
        "protocol": "Training pe hărți dedicate, evaluare pe alte hărți; A* rămâne baseline cu hartă cunoscută.",
        "agent_lifecycle": "shared_across_maps",
    },
    "training_cost": {
        "id": "training_cost",
        "label": "Cost training vs decizie",
        "description": "Distinge costul de antrenare de timpul de decizie într-un episod evaluat.",
        "assumption": "Learning-ul plătește cost înainte de evaluare, planning-ul plătește la fiecare hartă.",
        "expected_takeaway": "A* este foarte puternic fără training; learning-ul merită când politica este reutilizată.",
        "favored_algorithms": ["astar", "risk_aware_astar", "feature_q", "feature_risk_astar"],
        "protocol": "Evaluare Monte Carlo standard cu metadate explicite despre episoadele de training.",
        "agent_lifecycle": "per_map",
    },
}


# Notă de interpretare: în profilele cu ``agent_lifecycle == "per_map"``,
# un agent care necesită training (ex. ``tabular_q``) este re-creat și
# re-antrenat pentru fiecare hartă de evaluare. Politicile învățate NU se
# transferă între hărți — fiecare măsurătoare reflectă o sesiune de învățare
# izolată, iar variabilitatea raportată include și variabilitatea cauzată de
# inițializările diferite. Singurul profil în care un agent este antrenat o
# dată și apoi evaluat pe hărți distincte este ``transfer_learning``, care
# folosește ``_run_transfer_experiment``.


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
    if key in ("feature_risk_astar", "feature-risk-a*", "feature risk astar", "hybrid"):
        return FeatureRiskAwareAStarAgent(risk_weight=risk_weight, random_seed=seed)
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


def _emit(progress_callback, event_type: str, **payload) -> None:
    if progress_callback is not None:
        progress_callback({"type": event_type, **payload})


def _progress_payload(completed: int, total: int, **extra) -> dict:
    return {
        "completed": completed,
        "total": total,
        **extra,
    }


def _result_config(profile, scenario, number_of_maps, episodes_per_map, training_episodes,
                   movement_noise, risk_weight, optimization_objective, values):
    return {
        "scenario": scenario,
        "experiment_profile": profile["id"],
        "number_of_maps": number_of_maps,
        "episodes_per_map": episodes_per_map,
        "training_episodes": training_episodes,
        "movement_noise": movement_noise,
        "risk_weight": risk_weight,
        "optimization_objective": optimization_objective,
        **values,
    }


def run_training(agent, env, max_steps: int, episodes: int, progress_callback=None, context: dict | None = None):
    simulator = Simulator(env, agent, max_steps=max_steps)
    history = []
    checkpoint = max(1, episodes // 10) if episodes else 1
    for episode_index in range(episodes):
        history.append(simulator.run_episode(training=True))
        if (episode_index + 1 == episodes) or ((episode_index + 1) % checkpoint == 0):
            _emit(
                progress_callback,
                "training_progress",
                agent=agent.name,
                episode=episode_index + 1,
                total_episodes=episodes,
                **(context or {}),
            )
    return history


def _set_greedy_policy(agent):
    if hasattr(agent, "epsilon"):
        agent.epsilon = 0.0


def _generate_env(generator, values, seed, movement_noise, risk_weight):
    return generator.generate(
        rows=values["rows"],
        cols=values["cols"],
        wall_probability=values["wall_probability"],
        danger_probability=values["danger_probability"],
        random_seed=seed,
        movement_noise=movement_noise,
        reward_config=RewardConfig(risk_weight=risk_weight),
    )


def _run_transfer_experiment(
    agents,
    generator,
    values,
    number_of_maps: int,
    episodes_per_map: int,
    training_episodes: int,
    movement_noise: float,
    risk_weight: float,
    max_steps: int,
    random_seed: int,
    progress_callback=None,
    total_evaluation_episodes: int | None = None,
    partial_summary_every: int = 1,
):
    results = []
    training_maps = max(1, min(number_of_maps, 4))
    episodes_per_training_map = max(1, training_episodes // training_maps) if training_episodes > 0 else 0
    completed_evaluations = 0
    total_evaluations = total_evaluation_episodes or (len(agents) * number_of_maps * episodes_per_map)

    for agent_index, agent_spec in enumerate(agents):
        train_seed = random_seed + 50_000
        agent_seed = random_seed + agent_index * 997
        if isinstance(agent_spec, str):
            agent = create_agent(agent_spec, values["rows"], values["cols"], risk_weight, agent_seed)
        elif isinstance(agent_spec, Callable):
            agent = agent_spec()
        else:
            agent = agent_spec

        _emit(
            progress_callback,
            "agent_started",
            agent=agent.name,
            agent_index=agent_index,
            agent_count=len(agents),
            phase="training" if getattr(agent, "requires_training", False) else "evaluation",
            progress=_progress_payload(completed_evaluations, total_evaluations),
        )

        if getattr(agent, "requires_training", False) and episodes_per_training_map > 0:
            for train_index in range(training_maps):
                train_env = _generate_env(
                    generator,
                    values,
                    train_seed + train_index * 997,
                    movement_noise,
                    risk_weight,
                )
                _emit(
                    progress_callback,
                    "training_started",
                    agent=agent.name,
                    training_map_index=train_index,
                    training_map_count=training_maps,
                    map_seed=train_seed + train_index * 997,
                    total_episodes=episodes_per_training_map,
                    progress=_progress_payload(completed_evaluations, total_evaluations),
                )
                run_training(
                    agent,
                    train_env,
                    max_steps=max_steps,
                    episodes=episodes_per_training_map,
                    progress_callback=progress_callback,
                    context={
                        "training_map_index": train_index,
                        "training_map_count": training_maps,
                        "map_seed": train_seed + train_index * 997,
                        "progress": _progress_payload(completed_evaluations, total_evaluations),
                    },
                )
            _set_greedy_policy(agent)

        for map_index in range(number_of_maps):
            seed = random_seed + map_index * 997
            eval_env_preview = _generate_env(generator, values, seed, movement_noise, risk_weight)
            _emit(
                progress_callback,
                "map_started",
                map_index=map_index,
                map_count=number_of_maps,
                map_seed=seed,
                agent=agent.name,
                environment=eval_env_preview.to_payload(include_risk=True),
                progress=_progress_payload(completed_evaluations, total_evaluations),
            )
            for _ in range(episodes_per_map):
                eval_env = _generate_env(generator, values, seed, movement_noise, risk_weight)
                _emit(
                    progress_callback,
                    "episode_started",
                    agent=agent.name,
                    map_index=map_index,
                    map_count=number_of_maps,
                    map_seed=seed,
                    episode_index=completed_evaluations,
                    progress=_progress_payload(completed_evaluations, total_evaluations),
                )
                episode = Simulator(eval_env, agent, max_steps=max_steps).run_episode(training=False)
                episode.map_seed = seed
                results.append(episode)
                completed_evaluations += 1
                progress = _progress_payload(
                    completed_evaluations,
                    total_evaluations,
                    map_index=map_index,
                    map_count=number_of_maps,
                    agent=agent.name,
                    map_seed=seed,
                )
                _emit(
                    progress_callback,
                    "episode_finished",
                    progress=progress,
                    episode=episode.to_dict(),
                )
                if completed_evaluations % partial_summary_every == 0 or completed_evaluations == total_evaluations:
                    _emit(
                        progress_callback,
                        "partial_summary",
                        progress=progress,
                        summary=aggregate_results(results),
                    )

    return results


def run_monte_carlo_experiment(
    agents,
    experiment_profile: str = "known_static",
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
    optimization_objective: str = "balanced",
    progress_callback=None,
):
    """Rulează agenți pe hărți generate aleator și returnează metrici agregate."""
    generator = MapGenerator()
    values = _scenario_values(scenario, rows, cols, wall_probability, danger_probability)
    profile = EXPERIMENT_PROFILES.get(experiment_profile, EXPERIMENT_PROFILES["known_static"])
    results = []
    total_evaluation_episodes = len(agents) * number_of_maps * episodes_per_map
    partial_summary_every = max(1, total_evaluation_episodes // 10)
    config_payload = _result_config(
        profile,
        scenario,
        number_of_maps,
        episodes_per_map,
        training_episodes,
        movement_noise,
        risk_weight,
        optimization_objective,
        values,
    )

    _emit(
        progress_callback,
        "job_started",
        config=config_payload,
        profile=profile,
        totals={
            "agents": len(agents),
            "maps": number_of_maps,
            "episodes_per_map": episodes_per_map,
            "evaluation_episodes": total_evaluation_episodes,
            "training_episodes_per_q_agent": training_episodes,
        },
        progress=_progress_payload(0, total_evaluation_episodes),
    )

    if profile["id"] == "transfer_learning":
        results = _run_transfer_experiment(
            agents=agents,
            generator=generator,
            values=values,
            number_of_maps=number_of_maps,
            episodes_per_map=episodes_per_map,
            training_episodes=training_episodes,
            movement_noise=movement_noise,
            risk_weight=risk_weight,
            max_steps=max_steps,
            random_seed=random_seed,
            progress_callback=progress_callback,
            total_evaluation_episodes=total_evaluation_episodes,
            partial_summary_every=partial_summary_every,
        )
        summary = aggregate_results(results)
        return {
            "config": config_payload,
            "profile": profile,
            "summary": summary,
            "recommendation": build_recommendation(summary, optimization_objective),
            "episodes": [result.to_dict() for result in results],
        }

    completed_evaluations = 0
    for map_index in range(number_of_maps):
        seed = random_seed + map_index * 997
        base_env = generator.generate(
            rows=values["rows"],
            cols=values["cols"],
            wall_probability=values["wall_probability"],
            danger_probability=values["danger_probability"],
            random_seed=seed,
            movement_noise=movement_noise,
            reward_config=RewardConfig(risk_weight=risk_weight),
        )
        _emit(
            progress_callback,
            "map_started",
            map_index=map_index,
            map_count=number_of_maps,
            map_seed=seed,
            environment=base_env.to_payload(include_risk=True),
            progress=_progress_payload(completed_evaluations, total_evaluation_episodes),
        )
        for agent_spec in agents:
            if isinstance(agent_spec, str):
                agent = create_agent(agent_spec, base_env.rows, base_env.cols, risk_weight, seed)
            elif isinstance(agent_spec, Callable):
                agent = agent_spec()
            else:
                agent = agent_spec

            _emit(
                progress_callback,
                "agent_started",
                agent=agent.name,
                map_index=map_index,
                map_count=number_of_maps,
                map_seed=seed,
                phase="training" if getattr(agent, "requires_training", False) and training_episodes > 0 else "evaluation",
                progress=_progress_payload(completed_evaluations, total_evaluation_episodes),
            )
            if getattr(agent, "requires_training", False) and training_episodes > 0:
                train_env = generator.generate(
                    rows=values["rows"],
                    cols=values["cols"],
                    wall_probability=values["wall_probability"],
                    danger_probability=values["danger_probability"],
                    random_seed=seed,
                    movement_noise=movement_noise,
                    reward_config=RewardConfig(risk_weight=risk_weight),
                )
                _emit(
                    progress_callback,
                    "training_started",
                    agent=agent.name,
                    map_index=map_index,
                    map_count=number_of_maps,
                    map_seed=seed,
                    total_episodes=training_episodes,
                    progress=_progress_payload(completed_evaluations, total_evaluation_episodes),
                )
                run_training(
                    agent,
                    train_env,
                    max_steps=max_steps,
                    episodes=training_episodes,
                    progress_callback=progress_callback,
                    context={
                        "map_index": map_index,
                        "map_count": number_of_maps,
                        "map_seed": seed,
                        "progress": _progress_payload(completed_evaluations, total_evaluation_episodes),
                    },
                )
                _set_greedy_policy(agent)

            for episode_on_map in range(episodes_per_map):
                eval_env = generator.generate(
                    rows=values["rows"],
                    cols=values["cols"],
                    wall_probability=values["wall_probability"],
                    danger_probability=values["danger_probability"],
                    random_seed=seed,
                    movement_noise=movement_noise,
                    reward_config=RewardConfig(risk_weight=risk_weight),
                )
                _emit(
                    progress_callback,
                    "episode_started",
                    agent=agent.name,
                    map_index=map_index,
                    map_count=number_of_maps,
                    map_seed=seed,
                    episode_on_map=episode_on_map,
                    progress=_progress_payload(completed_evaluations, total_evaluation_episodes),
                )
                episode = Simulator(eval_env, agent, max_steps=max_steps).run_episode(training=False)
                episode.map_seed = seed
                results.append(episode)
                completed_evaluations += 1
                progress = _progress_payload(
                    completed_evaluations,
                    total_evaluation_episodes,
                    map_index=map_index,
                    map_count=number_of_maps,
                    agent=agent.name,
                    map_seed=seed,
                )
                _emit(
                    progress_callback,
                    "episode_finished",
                    progress=progress,
                    episode=episode.to_dict(),
                )
                if completed_evaluations % partial_summary_every == 0 or completed_evaluations == total_evaluation_episodes:
                    _emit(
                        progress_callback,
                        "partial_summary",
                        progress=progress,
                        summary=aggregate_results(results),
                    )

    summary = aggregate_results(results)
    return {
        "config": config_payload,
        "profile": profile,
        "summary": summary,
        "recommendation": build_recommendation(summary, optimization_objective),
        "episodes": [result.to_dict() for result in results],
    }
