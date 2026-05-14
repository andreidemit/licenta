"""CLI minimal pentru comparații Monte Carlo."""

import argparse
import json

from experiments.compare_agents import run_monte_carlo_experiment


def main():
    parser = argparse.ArgumentParser(description="Monte Carlo Safe Navigation")
    parser.add_argument("--scenario", default="medium", choices=["easy", "medium", "hard", "custom"])
    parser.add_argument("--maps", type=int, default=5)
    parser.add_argument("--episodes-per-map", type=int, default=2)
    parser.add_argument("--training-episodes", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--objective",
        default="balanced",
        choices=["balanced", "safety_first", "efficiency_first", "robustness_first"],
        help="Obiectivul folosit pentru recomandarea strategiei.",
    )
    args = parser.parse_args()
    result = run_monte_carlo_experiment(
        agents=["random", "rule_based", "astar", "risk_aware_astar", "tabular_q", "feature_q", "feature_risk_astar"],
        scenario=args.scenario,
        number_of_maps=args.maps,
        episodes_per_map=args.episodes_per_map,
        training_episodes=args.training_episodes,
        random_seed=args.seed,
        optimization_objective=args.objective,
    )
    print(json.dumps({"summary": result["summary"], "recommendation": result["recommendation"]}, indent=2))


if __name__ == "__main__":
    main()
