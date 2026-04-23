"""
Teste pentru save/load Q-Table (persistență).
"""

import sys
import os
import tempfile
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.q_learning import QLearning
from src.environment import Environment
from src.trainer import Trainer
from src.constants import ENERGY_MAX


SEED = 42
GRID = 10


def _train_q(num_episodes=200):
    env = Environment(rows=GRID, cols=GRID, seed=SEED)
    q = QLearning(rows=GRID, cols=GRID)
    trainer = Trainer(env, q, energy=ENERGY_MAX)
    trainer.train(num_episodes=num_episodes, print_every=num_episodes + 1)
    return q, env


def test_save_creates_file():
    """save() creează fișierul .npy."""
    q, _ = _train_q()
    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        path = f.name

    try:
        q.save(path)
        assert os.path.exists(path), f"Fișierul {path} nu a fost creat"
        assert os.path.getsize(path) > 0, "Fișierul salvat este gol"
        print(f"✅ save(): fișier creat ({os.path.getsize(path)} bytes)")
    finally:
        os.unlink(path)


def test_save_creates_directory():
    """save() creează directorul intermediar dacă nu există."""
    q, _ = _train_q()
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "subdir", "qtable.npy")
        q.save(path)
        assert os.path.exists(path), f"Fișierul nu a fost creat la {path}"
        print(f"✅ save(): director creat automat")


def test_load_roundtrip():
    """save() + load() produce Q-table identic."""
    q_original, _ = _train_q(200)

    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        path = f.name

    try:
        q_original.save(path)

        q_loaded = QLearning(rows=GRID, cols=GRID)
        q_loaded.load(path)

        np.testing.assert_array_equal(
            q_original.q_table,
            q_loaded.q_table,
            err_msg="Q-table-ul încărcat diferă de cel original!"
        )
        print("✅ load(): Q-table identic după roundtrip save/load")
    finally:
        os.unlink(path)


def test_load_resets_epsilon_to_min():
    """load() resetează epsilon la epsilon_min (gata de exploatare)."""
    q, _ = _train_q(50)  # epsilon > epsilon_min după 50 ep.

    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        path = f.name

    try:
        epsilon_before_save = q.epsilon
        q.save(path)

        q_loaded = QLearning(rows=GRID, cols=GRID)
        q_loaded.load(path)

        assert q_loaded.epsilon == q_loaded.epsilon_min, (
            f"Epsilon după load = {q_loaded.epsilon}, "
            f"expected epsilon_min = {q_loaded.epsilon_min}"
        )
        print(f"✅ load(): epsilon resetat la {q_loaded.epsilon_min} "
              f"(era {epsilon_before_save:.4f} înainte de save)")
    finally:
        os.unlink(path)


def test_load_wrong_shape_raises():
    """load() ridică ValueError dacă shape-ul nu coincide."""
    q_small = QLearning(rows=5, cols=5)  # shape (5,5,4,5)
    q_big = QLearning(rows=GRID, cols=GRID)   # shape (10,10,4,5)

    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        path = f.name

    try:
        q_small.save(path)

        raised = False
        try:
            q_big.load(path)
        except ValueError:
            raised = True

        assert raised, "load() nu a ridicat ValueError la shape incompatibil!"
        print("✅ load(): ValueError ridicat corect pentru shape incompatibil")
    finally:
        os.unlink(path)


def test_greedy_identical_after_load():
    """Agentul greedy produce același outcome înainte și după load."""
    q, env = _train_q(300)

    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        path = f.name

    try:
        trainer_orig = Trainer(env, q, energy=ENERGY_MAX)
        _, outcome_orig = trainer_orig.run_greedy_episode()

        q.save(path)

        q_loaded = QLearning(rows=GRID, cols=GRID)
        q_loaded.load(path)

        env.reset(seed=SEED)
        trainer_loaded = Trainer(env, q_loaded, energy=ENERGY_MAX)
        _, outcome_loaded = trainer_loaded.run_greedy_episode()

        assert outcome_orig == outcome_loaded, (
            f"Outcome greedy diferit după load: {outcome_orig} vs {outcome_loaded}"
        )
        print(f"✅ load(): outcome greedy identic: {outcome_orig}")
    finally:
        os.unlink(path)


def test_nonzero_count_preserved():
    """Numărul de intrări nenule este identic după load."""
    q, _ = _train_q(200)

    with tempfile.NamedTemporaryFile(suffix=".npy", delete=False) as f:
        path = f.name

    try:
        nonzero_before = q.get_nonzero_count()
        q.save(path)

        q_loaded = QLearning(rows=GRID, cols=GRID)
        q_loaded.load(path)

        nonzero_after = q_loaded.get_nonzero_count()
        assert nonzero_before == nonzero_after, (
            f"Intrări nenule: {nonzero_before} vs {nonzero_after} după load"
        )
        print(f"✅ load(): {nonzero_before} intrări nenule conservate")
    finally:
        os.unlink(path)


if __name__ == "__main__":
    print("=== Teste Persistență Q-Table ===\n")
    test_save_creates_file()
    test_save_creates_directory()
    test_load_roundtrip()
    test_load_resets_epsilon_to_min()
    test_load_wrong_shape_raises()
    test_greedy_identical_after_load()
    test_nonzero_count_preserved()
    print("\n✅ Toate testele de persistență au trecut!")
