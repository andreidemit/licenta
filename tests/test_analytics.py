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
        "outcome", "coverage_pct", "energy_remaining"
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
    test_save_all_plots_creates_pngs()
    test_save_all_plots_short_history()
    test_plot_convergence_creates_png()
    test_plot_epsilon_decay_creates_png()
    test_plot_success_rate_creates_png()
    test_plot_alpha_comparison_creates_png()
    test_filename_convention()
    print("\n✅ Toate testele analytics au trecut!")
