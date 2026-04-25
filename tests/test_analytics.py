"""
Teste pentru modulul Analytics: CSV export și grafice Matplotlib.
"""

import sys
import os
import csv
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.analytics import Analytics
from src.trainer import EpisodeResult
from src.environment import Environment
from src.q_learning import QLearning
from src.trainer import Trainer


def _make_history(n=100):
    """Generează un istoric fictiv de episoade pentru teste."""
    results = []
    outcomes = ["target_reached", "energy_depleted", "danger", "timeout"]
    for i in range(n):
        outcome = outcomes[i % len(outcomes)]
        results.append(EpisodeResult(
            episode_id=i,
            total_steps=20 + i % 30,
            total_reward=float(-50 + i * 1.5),
            epsilon=max(0.01, 1.0 * (0.995 ** i)),
            outcome=outcome,
            coverage=float(0.1 + i * 0.005),
            energy_remaining=float(max(0, 80 - i * 0.3)),
        ))
    return results


def test_export_csv_creates_file():
    """export_csv() creează fișierul CSV."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(50)
        path = analytics.export_csv(history)

        assert os.path.exists(path), f"CSV nu a fost creat la {path}"
        assert os.path.getsize(path) > 0, "CSV-ul este gol"
        print(f"✅ export_csv(): fișier creat ({os.path.getsize(path)} bytes)")


def test_export_csv_correct_columns():
    """export_csv() produce CSV cu coloanele corecte."""
    expected_cols = {
        "episode_id", "steps", "total_reward", "epsilon",
        "outcome", "coverage_pct", "energy_remaining",
        "collisions", "food_collected", "mud_steps", "danger_entries",
        "energy_spent", "energy_gained", "action_up", "action_down",
        "action_left", "action_right", "action_stay", "mean_abs_td",
        "q_nonzero", "q_fill_pct"
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(20)
        path = analytics.export_csv(history)

        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            actual_cols = set(reader.fieldnames or [])

        assert expected_cols.issubset(actual_cols), (
            f"Coloane lipsă: {expected_cols - actual_cols}"
        )
        print(f"✅ export_csv(): coloane corecte: {sorted(actual_cols)}")


def test_export_csv_outcome_labels():
    """export_csv() mapează outcome-urile la labeluri corecte."""
    label_map = {
        "target_reached": "SUCCESS",
        "energy_depleted": "DEATH_ENERGY",
        "danger": "DEATH_TRAP",
        "timeout": "TIMEOUT",
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(40)
        path = analytics.export_csv(history)

        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        for row in rows:
            raw_outcome = history[int(row["episode_id"])].outcome
            expected_label = label_map[raw_outcome]
            assert row["outcome"] == expected_label, (
                f"Outcome '{raw_outcome}' mapat greșit: '{row['outcome']}' != '{expected_label}'"
            )
        print(f"✅ export_csv(): {len(rows)} outcome-uri mapate corect")


def test_export_csv_correct_row_count():
    """export_csv() produce exact N rânduri (N = len(history))."""
    n = 73
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="A", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(n)
        path = analytics.export_csv(history)

        with open(path, newline="") as f:
            reader = csv.DictReader(f)
            row_count = sum(1 for _ in reader)

        assert row_count == n, f"CSV are {row_count} rânduri, așteptat {n}"
        print(f"✅ export_csv(): {row_count} rânduri corecte")


def test_export_csv_extended_metrics_values():
    """export_csv() include valorile de observabilitate extinsă."""
    history = [
        EpisodeResult(
            episode_id=0,
            total_steps=7,
            total_reward=12.5,
            epsilon=0.5,
            outcome="target_reached",
            coverage=15.0,
            energy_remaining=83.0,
            collisions=2,
            food_collected=1,
            mud_steps=3,
            danger_entries=0,
            energy_spent=9.0,
            energy_gained=20.0,
            action_counts=[1, 2, 3, 0, 1],
            mean_abs_td=4.25,
            q_nonzero=17,
            q_fill_pct=8.5,
        )
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        path = analytics.export_csv(history)
        with open(path, newline="") as f:
            row = next(csv.DictReader(f))
        assert row["collisions"] == "2"
        assert row["food_collected"] == "1"
        assert row["action_left"] == "3"
        assert row["mean_abs_td"] == "4.2500"
        assert row["q_fill_pct"] == "8.50"
        print("✅ export_csv(): metrici extinse corecte")


def test_save_all_plots_creates_pngs():
    """save_all_plots() creează cele 3 fișiere PNG."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(100)
        paths = analytics.save_all_plots(history)

        assert len(paths) == 3, f"save_all_plots() a returnat {len(paths)} căi, așteptat 3"
        for p in paths:
            assert os.path.exists(p), f"Grafic lipsă: {p}"
            assert os.path.getsize(p) > 1000, f"Grafic prea mic (suspect gol): {p}"
            print(f"  ✓ {os.path.basename(p)} ({os.path.getsize(p)} bytes)")
        print("✅ save_all_plots(): 3 PNG-uri create")


def test_save_all_plots_short_history():
    """save_all_plots() funcționează și pentru istorice mai scurte decât fereastra default."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(10)
        paths = analytics.save_all_plots(history)

        assert len(paths) == 3, f"save_all_plots() a returnat {len(paths)} căi, așteptat 3"
        for p in paths:
            assert os.path.exists(p), f"Grafic lipsă pentru istoric scurt: {p}"
            assert os.path.getsize(p) > 1000, f"Grafic prea mic pentru istoric scurt: {p}"
        print("✅ save_all_plots(): funcționează și pentru istorice scurte")


def test_plot_convergence_creates_png():
    """plot_convergence() creează fișierul PNG."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="C", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(100)
        path = analytics.plot_convergence(history)

        assert os.path.exists(path), f"PNG convergence lipsă: {path}"
        assert "convergence" in path, f"Calea nu conține 'convergence': {path}"
        print(f"✅ plot_convergence(): {os.path.basename(path)}")


def test_plot_epsilon_decay_creates_png():
    """plot_epsilon_decay() creează fișierul PNG."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="A", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(100)
        path = analytics.plot_epsilon_decay(history)

        assert os.path.exists(path), f"PNG epsilon lipsă: {path}"
        assert "epsilon" in path, f"Calea nu conține 'epsilon': {path}"
        print(f"✅ plot_epsilon_decay(): {os.path.basename(path)}")


def test_plot_success_rate_creates_png():
    """plot_success_rate() creează fișierul PNG."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=10, seed=42, out_dir=tmpdir)
        history = _make_history(100)
        path = analytics.plot_success_rate(history)

        assert os.path.exists(path), f"PNG success lipsă: {path}"
        assert "success" in path, f"Calea nu conține 'success': {path}"
        print(f"✅ plot_success_rate(): {os.path.basename(path)}")


def test_plot_alpha_comparison_creates_png():
    """plot_alpha_comparison() creează graficul comparativ pentru multiple alpha."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="C", grid_size=10, seed=42, out_dir=tmpdir)
        histories = {
            0.05: _make_history(100),
            0.10: _make_history(100),
            0.20: _make_history(100),
        }
        path = analytics.plot_alpha_comparison(histories)

        assert os.path.exists(path), f"PNG alpha comparison lipsă: {path}"
        assert os.path.getsize(path) > 1000, "PNG alpha comparison prea mic"
        print(f"✅ plot_alpha_comparison(): {os.path.basename(path)}")


def _trained_small_run(tmpdir):
    env = Environment(rows=10, cols=10, seed=7)
    q = QLearning(rows=10, cols=10)
    trainer = Trainer(env, q)
    history = trainer.train(num_episodes=5, print_every=0)
    agent, outcome, trajectory = trainer.run_greedy_trajectory()
    analytics = Analytics(scenario="B", grid_size=10, seed=7, out_dir=tmpdir)
    summary = {
        "outcome": outcome,
        "steps": agent.total_steps,
        "reward": agent.total_reward,
        "energy_remaining": agent.energy,
        "bfs_distance": env.bfs(env.start_pos, env.target_pos),
    }
    return analytics, env, q, history, trajectory, summary


def test_export_run_manifest_creates_json():
    """export_run_manifest() salvează metadata reproductibilă."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics, env, q, history, _, summary = _trained_small_run(tmpdir)
        path = analytics.export_run_manifest(
            history,
            env,
            q,
            artifacts={"results_csv": "dummy.csv"},
            greedy_summary=summary,
            energy=100,
        )
        assert os.path.exists(path), f"Manifest lipsă: {path}"
        assert os.path.getsize(path) > 100, "Manifest suspect gol"
        print(f"✅ manifest JSON: {os.path.basename(path)}")


def test_static_visual_artifacts_create_pngs():
    """save_visual_artifacts() creează harta, policy și heatmap-urile."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics, env, q, _, trajectory, _ = _trained_small_run(tmpdir)
        paths = analytics.save_visual_artifacts(env, q, trajectory=trajectory)
        expected = {
            "map_png", "policy_png", "q_heatmap_png",
            "visit_heatmap_png", "td_heatmap_png", "greedy_path_png",
        }
        assert expected.issubset(paths.keys()), f"Artefacte lipsă: {expected - set(paths.keys())}"
        for path in paths.values():
            assert os.path.exists(path), f"PNG lipsă: {path}"
            assert os.path.getsize(path) > 1000, f"PNG prea mic: {path}"
        print("✅ save_visual_artifacts(): PNG-uri create")


def test_export_greedy_trajectory_creates_files():
    """export_greedy_trajectory() creează CSV + JSON."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics, _, _, _, trajectory, summary = _trained_small_run(tmpdir)
        csv_path, json_path = analytics.export_greedy_trajectory(trajectory, summary=summary)
        assert os.path.exists(csv_path), f"CSV traseu lipsă: {csv_path}"
        assert os.path.exists(json_path), f"JSON traseu lipsă: {json_path}"
        with open(csv_path, newline="") as f:
            fieldnames = set(csv.DictReader(f).fieldnames or [])
        assert {"step", "row", "col", "energy", "action_name", "terminal_reason"}.issubset(fieldnames)
        print("✅ export_greedy_trajectory(): CSV + JSON create")


def test_plot_scenario_comparison_creates_png():
    """plot_scenario_comparison() creează dashboard comparativ."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="ALL", grid_size=10, seed=42, out_dir=tmpdir)
        path = analytics.plot_scenario_comparison({
            "A": _make_history(20),
            "B": _make_history(20),
        })
        assert os.path.exists(path), f"PNG scenario comparison lipsă: {path}"
        assert os.path.getsize(path) > 1000, "PNG scenario comparison prea mic"
        print(f"✅ scenario comparison: {os.path.basename(path)}")


def test_filename_convention():
    """Fișierele generate respectă convenția de denumire."""
    with tempfile.TemporaryDirectory() as tmpdir:
        analytics = Analytics(scenario="B", grid_size=20, seed=42, out_dir=tmpdir)
        history = _make_history(50)
        csv_path = analytics.export_csv(history)

        filename = os.path.basename(csv_path)
        assert "B" in filename, f"Scenariul lipsă din filename: {filename}"
        assert "20" in filename, f"Grid size lipsă din filename: {filename}"
        assert "42" in filename, f"Seed lipsă din filename: {filename}"
        assert filename.endswith(".csv"), f"Extensie greșită: {filename}"
        print(f"✅ Convenție filename: {filename}")


if __name__ == "__main__":
    print("=== Teste Analytics (CSV + Grafice) ===\n")
    test_export_csv_creates_file()
    test_export_csv_correct_columns()
    test_export_csv_outcome_labels()
    test_export_csv_correct_row_count()
    test_export_csv_extended_metrics_values()
    test_save_all_plots_creates_pngs()
    test_save_all_plots_short_history()
    test_plot_convergence_creates_png()
    test_plot_epsilon_decay_creates_png()
    test_plot_success_rate_creates_png()
    test_plot_alpha_comparison_creates_png()
    test_export_run_manifest_creates_json()
    test_static_visual_artifacts_create_pngs()
    test_export_greedy_trajectory_creates_files()
    test_plot_scenario_comparison_creates_png()
    test_filename_convention()
    print("\n✅ Toate testele analytics au trecut!")
