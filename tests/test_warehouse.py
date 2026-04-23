"""
Teste pentru WarehouseEnvironment — layout, topologie și antrenament.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.warehouse_scenario import WarehouseEnvironment
from src.environment import CellType
from src.q_learning import QLearning
from src.trainer import Trainer
from src.constants import ENERGY_MAX


def test_warehouse_start_and_target():
    """Start-ul este la (0,0) și target-ul la (19,4)."""
    env = WarehouseEnvironment()
    assert env.start_pos == (0, 0), f"Start incorect: {env.start_pos} != (0,0)"
    assert env.target_pos == (19, 4), f"Target incorect: {env.target_pos} != (19,4)"
    print(f"✅ Start={env.start_pos}, Target={env.target_pos}")


def test_warehouse_grid_dimensions():
    """Grid-ul are exact 20 rânduri și 20 coloane."""
    env = WarehouseEnvironment()
    assert len(env.grid) == 20, f"Număr rânduri: {len(env.grid)} != 20"
    assert all(len(row) == 20 for row in env.grid), "Nu toate rândurile au 20 coloane"
    print("✅ Dimensiuni grid: 20×20")


def test_warehouse_bfs_optimal_path():
    """BFS de la start la target returnează exact 23 pași."""
    env = WarehouseEnvironment()
    bfs_dist = env.bfs(env.start_pos, env.target_pos)
    assert bfs_dist == 23, f"BFS optim: {bfs_dist} != 23"
    print(f"✅ BFS optim: {bfs_dist} pași")


def test_warehouse_has_start_cell():
    """Celula (0,0) este de tip START."""
    env = WarehouseEnvironment()
    assert env.grid[0][0] == CellType.START, (
        f"Celula (0,0) este {env.grid[0][0]}, așteptat START"
    )
    print("✅ Celula (0,0) = START")


def test_warehouse_has_target_cell():
    """Celula (19,4) este de tip TARGET."""
    env = WarehouseEnvironment()
    assert env.grid[19][4] == CellType.TARGET, (
        f"Celula (19,4) este {env.grid[19][4]}, așteptat TARGET"
    )
    print("✅ Celula (19,4) = TARGET")


def test_warehouse_obstacle_count():
    """Depozitul are cel puțin 100 de celule OBSTACLE (rafturi)."""
    env = WarehouseEnvironment()
    obstacle_count = sum(
        1 for row in env.grid for cell in row if cell == CellType.OBSTACLE
    )
    assert obstacle_count >= 100, f"Prea puține obstacole: {obstacle_count} < 100"
    print(f"✅ Obstacole (rafturi): {obstacle_count}")


def test_warehouse_food_cells():
    """Depozitul are cel puțin 4 stații de încărcare (FOOD)."""
    env = WarehouseEnvironment()
    food_count = sum(
        1 for row in env.grid for cell in row if cell == CellType.FOOD
    )
    assert food_count >= 4, f"Prea puține stații de încărcare: {food_count} < 4"
    print(f"✅ Stații de încărcare (FOOD): {food_count}")


def test_warehouse_danger_cells():
    """Depozitul are cel puțin 2 celule DANGER (zone stivuitor)."""
    env = WarehouseEnvironment()
    danger_count = sum(
        1 for row in env.grid for cell in row if cell == CellType.DANGER
    )
    assert danger_count >= 2, f"Prea puține zone de pericol: {danger_count} < 2"
    print(f"✅ Zone pericol (DANGER): {danger_count}")


def test_warehouse_mud_cells():
    """Depozitul are cel puțin 8 celule MUD (intersecții aglomerate)."""
    env = WarehouseEnvironment()
    mud_count = sum(
        1 for row in env.grid for cell in row if cell == CellType.MUD
    )
    assert mud_count >= 8, f"Prea puțin MUD: {mud_count} < 8"
    print(f"✅ Zone aglomerate (MUD): {mud_count}")


def test_warehouse_path_is_solvable():
    """BFS returnează un număr pozitiv (există drum start→target)."""
    env = WarehouseEnvironment()
    dist = env.bfs(env.start_pos, env.target_pos)
    assert dist is not None and dist > 0, (
        f"Nu există drum de la start la target! BFS={dist}"
    )
    print(f"✅ Drum solvabil: BFS = {dist} pași")


def test_warehouse_reset_preserves_layout():
    """reset() menține același layout fix (ignoră seed-ul)."""
    env = WarehouseEnvironment()
    grid_before = [row[:] for row in env.grid]
    start_before = env.start_pos
    target_before = env.target_pos

    env.reset(seed=99)  # seed ignorat pentru warehouse

    assert env.start_pos == start_before, "Start s-a schimbat după reset!"
    assert env.target_pos == target_before, "Target s-a schimbat după reset!"
    for r in range(env.rows):
        for c in range(env.cols):
            assert env.grid[r][c] == grid_before[r][c], (
                f"Celula ({r},{c}) s-a schimbat după reset!"
            )
    print("✅ reset(): layout fix păstrat")


def test_warehouse_invalid_size_raises():
    """WarehouseEnvironment ridică ValueError pentru dimensiuni != 20×20."""
    raised = False
    try:
        WarehouseEnvironment(rows=10, cols=10)
    except ValueError:
        raised = True
    assert raised, "Nu s-a ridicat ValueError pentru grid non-20×20"
    print("✅ ValueError ridicat corect pentru grid non-20×20")


def test_warehouse_get_stats():
    """get_warehouse_stats() returnează un dict cu câmpuri corecte."""
    env = WarehouseEnvironment()
    stats = env.get_warehouse_stats()

    required_keys = {
        "total_cells", "shelves", "aisles_empty", "charging_stations",
        "mud_zones", "danger_zones", "bfs_optimal_path", "start", "target"
    }
    assert required_keys.issubset(set(stats.keys())), (
        f"Câmpuri lipsă: {required_keys - set(stats.keys())}"
    )
    assert stats["total_cells"] == 400, f"total_cells={stats['total_cells']} != 400"
    assert stats["bfs_optimal_path"] == 23, f"BFS optimal={stats['bfs_optimal_path']} != 23"
    print(f"✅ get_warehouse_stats(): {stats}")


def test_warehouse_training_learns():
    """Antrenament 500 ep. pe WarehouseEnvironment: success rate îmbunătățit față de 0."""
    env = WarehouseEnvironment()
    q = QLearning(rows=20, cols=20)
    trainer = Trainer(env, q, energy=ENERGY_MAX)
    history = trainer.train(num_episodes=500, print_every=501)

    # Primele 50 ep. vs ultimele 50: success rate trebuie să crească
    first_50 = history[:50]
    last_50 = history[-50:]
    rate_first = sum(1 for r in first_50 if r.outcome == "target_reached") / 50
    rate_last = sum(1 for r in last_50 if r.outcome == "target_reached") / 50

    assert rate_last > rate_first, (
        f"Warehouse: success rate NU a crescut: {rate_first:.0%} → {rate_last:.0%}"
    )
    assert rate_last >= 0.10, (
        f"Warehouse: success rate final prea mic {rate_last:.0%} < 10% după 500 ep. — agentul nu a învățat nimic"
    )
    print(f"✅ Warehouse training: {rate_first:.0%} → {rate_last:.0%} (agent a învățat)")


if __name__ == "__main__":
    print("=== Teste WarehouseEnvironment ===\n")
    test_warehouse_start_and_target()
    test_warehouse_grid_dimensions()
    test_warehouse_bfs_optimal_path()
    test_warehouse_has_start_cell()
    test_warehouse_has_target_cell()
    test_warehouse_obstacle_count()
    test_warehouse_food_cells()
    test_warehouse_danger_cells()
    test_warehouse_mud_cells()
    test_warehouse_path_is_solvable()
    test_warehouse_reset_preserves_layout()
    test_warehouse_invalid_size_raises()
    test_warehouse_get_stats()
    test_warehouse_training_learns()
    print("\n✅ Toate testele warehouse au trecut!")
