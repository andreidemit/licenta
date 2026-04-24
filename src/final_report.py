"""
Rulare standardizată pentru pachetul final de rezultate.

Generează un set reproductibil de experimente pentru scenariile A, B, C și,
opțional, WAREHOUSE, apoi salvează un sumar JSON + CSV în directorul `data/`.
"""

import argparse
import csv
import json
import os

from src.analytics import Analytics
from src.constants import DEFAULT_EPISODES, ENERGY_MAX, SCENARIO_C_SWITCH_EPISODE
from src.environment import Environment
from src.q_learning import QLearning
from src.trainer import Trainer
from src.warehouse_scenario import WarehouseEnvironment


ENERGY_INFINITE = 999999


def _success_rate(history, last_n=100) -> float:
    recent = history[-min(last_n, len(history)):]
    if not recent:
        return 0.0
    successes = sum(1 for ep in recent if ep.outcome == "target_reached")
    return successes / len(recent) * 100


def _average_reward(history, last_n=100) -> float:
    recent = history[-min(last_n, len(history)):]
    if not recent:
        return 0.0
    return sum(ep.total_reward for ep in recent) / len(recent)


def _write_summary_files(summaries, out_dir, grid_size, seed, num_episodes):
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(out_dir, f"final_summary_{grid_size}_{seed}_{num_episodes}")
    json_path = f"{base}.json"
    csv_path = f"{base}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

    fieldnames = [
        "scenario",
        "episodes",
        "grid_size",
        "seed",
        "success_rate_last_100",
        "avg_reward_last_100",
        "greedy_outcome",
        "greedy_steps",
        "greedy_reward",
        "greedy_energy",
        "q_nonzero",
        "q_total",
        "results_csv",
        "convergence_png",
        "epsilon_png",
        "success_png",
        "qtable_path",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            writer.writerow(summary)

    return csv_path, json_path


def _run_standard_scenario(scenario, seed, grid_size, num_episodes, out_dir, save_qtables):
    if scenario == "WAREHOUSE":
        env = WarehouseEnvironment()
        q = QLearning(rows=20, cols=20)
        trainer = Trainer(env, q, energy=ENERGY_MAX)
        history = trainer.train(
            num_episodes=num_episodes,
            print_every=max(1, num_episodes // 10),
        )
        analytics = Analytics(scenario="WAREHOUSE", grid_size=20, seed=0, out_dir=out_dir)
        qtable_path = os.path.join(out_dir, "qtable_WAREHOUSE_20_0.npy") if save_qtables else ""
        scenario_seed = 0
        scenario_grid = 20
    else:
        energy = ENERGY_INFINITE if scenario == "A" else ENERGY_MAX
        env = Environment(rows=grid_size, cols=grid_size, seed=seed)
        q = QLearning(rows=grid_size, cols=grid_size)
        trainer = Trainer(env, q, energy=energy)
        history = trainer.train(
            num_episodes=num_episodes,
            print_every=max(1, num_episodes // 20),
            scenario_c_switch=SCENARIO_C_SWITCH_EPISODE if scenario == "C" else None,
        )
        analytics = Analytics(scenario=scenario, grid_size=grid_size, seed=seed, out_dir=out_dir)
        qtable_path = os.path.join(out_dir, f"qtable_{scenario}_{grid_size}_{seed}.npy") if save_qtables else ""
        scenario_seed = seed
        scenario_grid = grid_size

    if qtable_path:
        q.save(qtable_path)

    results_csv = analytics.export_csv(history)
    convergence_png, epsilon_png, success_png = analytics.save_all_plots(history)
    greedy_agent, greedy_outcome = trainer.run_greedy_episode()

    summary = {
        "scenario": scenario,
        "episodes": num_episodes,
        "grid_size": scenario_grid,
        "seed": scenario_seed,
        "success_rate_last_100": f"{_success_rate(history):.2f}",
        "avg_reward_last_100": f"{_average_reward(history):.2f}",
        "greedy_outcome": greedy_outcome,
        "greedy_steps": greedy_agent.total_steps,
        "greedy_reward": f"{greedy_agent.total_reward:.2f}",
        "greedy_energy": f"{greedy_agent.energy:.1f}",
        "q_nonzero": q.get_nonzero_count(),
        "q_total": q.get_state_count() * q.num_actions,
        "results_csv": results_csv,
        "convergence_png": convergence_png,
        "epsilon_png": epsilon_png,
        "success_png": success_png,
        "qtable_path": qtable_path,
    }
    return summary


def run_final_report(seed=42, grid_size=20, num_episodes=DEFAULT_EPISODES,
                     include_warehouse=True, out_dir="data", save_qtables=False):
    """
    Rulează pachetul standard de experimente și salvează sumarul final.
    """
    scenarios = ["A", "B", "C"]
    if include_warehouse:
        scenarios.append("WAREHOUSE")

    summaries = []
    for scenario in scenarios:
        print(f"\n=== Pachet final — Scenariul {scenario} ===")
        summaries.append(
            _run_standard_scenario(
                scenario=scenario,
                seed=seed,
                grid_size=grid_size,
                num_episodes=num_episodes,
                out_dir=out_dir,
                save_qtables=save_qtables,
            )
        )

    csv_path, json_path = _write_summary_files(
        summaries=summaries,
        out_dir=out_dir,
        grid_size=grid_size,
        seed=seed,
        num_episodes=num_episodes,
    )
    print(f"\nSumar CSV: {csv_path}")
    print(f"Sumar JSON: {json_path}")
    return summaries, csv_path, json_path


def main():
    parser = argparse.ArgumentParser(description="Pachet final de experimente pentru lucrarea de licență")
    parser.add_argument("--grid", type=int, default=20, help="Dimensiune grid pentru scenariile A/B/C")
    parser.add_argument("--seed", type=int, default=42, help="Seed pentru scenariile A/B/C")
    parser.add_argument("--episodes", type=int, default=DEFAULT_EPISODES, help="Număr episoade per scenariu")
    parser.add_argument("--out-dir", default="data", help="Directorul unde se salvează artefactele")
    parser.add_argument("--skip-warehouse", action="store_true", help="Omite scenariul WAREHOUSE din pachet")
    parser.add_argument("--save-qtables", action="store_true", help="Salvează și Q-table-urile standardizate")
    args = parser.parse_args()

    run_final_report(
        seed=args.seed,
        grid_size=args.grid,
        num_episodes=args.episodes,
        include_warehouse=not args.skip_warehouse,
        out_dir=args.out_dir,
        save_qtables=args.save_qtables,
    )


if __name__ == "__main__":
    main()
