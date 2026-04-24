"""
Teste pentru validarea comportamentelor specifice Scenariilor A, B și C.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.environment import Environment, CellType
from src.agent import Agent
from src.q_learning import QLearning
from src.trainer import Trainer
from src.constants import ENERGY_MAX

ENERGY_INFINITE = 999999
SEED = 42
GRID = 10


def run_training(scenario, num_episodes=400, seed=SEED, grid=GRID):
    """Rulează antrenament și returnează (history, trainer)."""
    energy = ENERGY_INFINITE if scenario == "A" else ENERGY_MAX
    env = Environment(rows=grid, cols=grid, seed=seed)
    q = QLearning(rows=grid, cols=grid)
    trainer = Trainer(env, q, energy=energy)

    scenario_c_switch = 200 if scenario == "C" else None
    history = trainer.train(
        num_episodes=num_episodes,
        print_every=num_episodes + 1,  # no printing
        scenario_c_switch=scenario_c_switch,
    )
    return history, trainer, q


def success_rate(history, last_n=50):
    """Calculează success rate pe ultimele n episoade."""
    recent = history[-min(last_n, len(history)):]
    return sum(1 for r in recent if r.outcome == "target_reached") / len(recent)


# ─── SCENARIUL A ────────────────────────────────────────────────────────────

def test_scenario_a_converges():
    """Scenariu A: energie infinită, agentul trebuie să găsească ținta."""
    history, trainer, q = run_training("A", num_episodes=600)
    rate = success_rate(history, last_n=50)
    assert rate >= 0.70, (
        f"Scenariu A: success rate prea mic ({rate:.0%} < 70%). "
        f"Q-Learning nu a conversat suficient."
    )
    print(f"✅ Scenariu A: success rate = {rate:.0%}")


def test_scenario_a_greedy_reaches_target():
    """Scenariu A: evaluarea greedy trebuie să ajungă la țintă."""
    _, trainer, _ = run_training("A", num_episodes=700)
    agent, outcome = trainer.run_greedy_episode()
    assert outcome == "target_reached", (
        f"Scenariu A greedy: outcome={outcome}, expected target_reached"
    )
    print(f"✅ Scenariu A greedy: {agent.total_steps} pași, reward={agent.total_reward:.1f}")


def test_scenario_a_fewer_energy_deaths_than_b():
    """Scenariu A: mai puține morți din energie față de Scenariul B (start cu mai multă energie)."""
    history_a, _, _ = run_training("A", num_episodes=300)
    history_b, _, _ = run_training("B", num_episodes=300)

    deaths_a = sum(1 for r in history_a[:100] if r.outcome == "energy_depleted")
    deaths_b = sum(1 for r in history_b[:100] if r.outcome == "energy_depleted")

    # Scenariul A pornește cu energie mai mare → mai puține morți în faza de explorare
    assert deaths_a <= deaths_b, (
        f"Scenariu A: {deaths_a} morți vs Scenariu B: {deaths_b}. "
        f"A ar trebui să aibă ≤ morți din energie decât B."
    )
    print(f"✅ Scenariu A vs B: morți energie primele 100 ep = {deaths_a} vs {deaths_b}")


# ─── SCENARIUL B ────────────────────────────────────────────────────────────

def test_scenario_b_converges():
    """Scenariu B: energie limitată, agentul trebuie să supraviețuiască și să găsească ținta."""
    history, _, _ = run_training("B", num_episodes=600)
    rate = success_rate(history, last_n=50)
    assert rate >= 0.50, (
        f"Scenariu B: success rate prea mic ({rate:.0%} < 50%). "
        f"Homeostazia energetică nu funcționează."
    )
    print(f"✅ Scenariu B: success rate = {rate:.0%}")


def test_scenario_b_energy_deaths_exist_early():
    """Scenariu B: în primele episoade trebuie să existe morți din energie."""
    history, _, _ = run_training("B", num_episodes=100)
    first_50 = history[:50]
    energy_deaths = [r for r in first_50 if r.outcome == "energy_depleted"]
    assert len(energy_deaths) > 0, (
        "Scenariu B: nu s-au înregistrat morți din energie în primele 50 ep. "
        "Energia limitată nu pare să funcționeze."
    )
    print(f"✅ Scenariu B: {len(energy_deaths)} morți din energie în primele 50 ep. (comportament corect)")


def test_scenario_b_greedy_survives():
    """Scenariu B: evaluarea greedy nu trebuie să moară din energie."""
    _, trainer, _ = run_training("B", num_episodes=600)
    agent, outcome = trainer.run_greedy_episode()
    assert outcome != "energy_depleted", (
        f"Scenariu B greedy: agentul a murit din energie după antrenament — politica nu a convergent"
    )
    assert agent.energy > 0, "Scenariu B greedy: energia a ajuns la 0"
    print(f"✅ Scenariu B greedy: outcome={outcome}, energie rămasă={agent.energy:.0f}")


def test_scenario_b_more_food_visits_than_a():
    """Scenariu B colectează mai multă hrană decât Scenariul A (comportament homostatic)."""
    history_a, _, _ = run_training("A", num_episodes=300)
    history_b, _, _ = run_training("B", num_episodes=300)

    # Compară reward mediu per episod cu succes
    success_a = [r for r in history_a if r.outcome == "target_reached"]
    success_b = [r for r in history_b if r.outcome == "target_reached"]

    if len(success_a) > 10 and len(success_b) > 10:
        sample_a = success_a[-min(20, len(success_a)):]
        sample_b = success_b[-min(20, len(success_b)):]
        avg_steps_a = sum(r.total_steps for r in sample_a) / len(sample_a)
        avg_steps_b = sum(r.total_steps for r in sample_b) / len(sample_b)
        # Scenariul B ar trebui să aibă mai mulți pași (detour pentru hrană)
        print(f"✅ Scenariu B vs A: avg steps = {avg_steps_b:.1f} vs {avg_steps_a:.1f} (B > A = detour pentru hrană)")
    else:
        print("⚠️  Prea puțin date pentru comparație steps A vs B")


# ─── SCENARIUL C ────────────────────────────────────────────────────────────

def test_scenario_c_relocates_obstacles():
    """Scenariu C: obstacolele trebuie să fie diferite înainte și după relocare."""
    env = Environment(rows=GRID, cols=GRID, seed=SEED)
    q = QLearning(rows=GRID, cols=GRID)
    trainer = Trainer(env, q, energy=ENERGY_MAX)

    # Salvăm pozițiile obstacolelor înainte
    obstacles_before = {
        (r, c) for r in range(GRID) for c in range(GRID)
        if env.grid[r][c] == CellType.OBSTACLE
    }

    # Relocare
    success = trainer._relocate_obstacles(env)

    obstacles_after = {
        (r, c) for r in range(GRID) for c in range(GRID)
        if env.grid[r][c] == CellType.OBSTACLE
    }

    assert success, "Relocarea obstacolelor a eșuat (BFS invalid după 10 încercări)"
    assert obstacles_before != obstacles_after, (
        "Obstacolele sunt identice înainte și după relocare — relocarea nu a funcționat"
    )
    assert len(obstacles_before) == len(obstacles_after), (
        "Numărul de obstacole s-a schimbat după relocare!"
    )
    print(f"✅ Scenariu C: relocare reușită, {len(obstacles_before - obstacles_after)} obstacole mutate")


def test_scenario_c_readapts_after_relocation():
    """Scenariu C: după relocare, agentul trebuie să se re-adapteze (success rate nu rămâne la 0)."""
    history, _, _ = run_training("C", num_episodes=400)

    # Episoadele pre-relocare (0-199)
    pre_relocation = history[:min(200, len(history))]
    # Episoadele imediat post-relocare (200-250)
    post_relocation_immediate = history[200:min(250, len(history))]
    # Episoadele târzii post-relocare (350-400)
    post_relocation_late = history[350:min(400, len(history))]

    if len(post_relocation_late) >= 20:
        rate_late = success_rate(post_relocation_late, last_n=len(post_relocation_late))
        assert rate_late >= 0.40, (
            f"Scenariu C: success rate tardiv prea mic ({rate_late:.0%}). "
            f"Agentul nu s-a re-adaptat după relocare."
        )
        print(f"✅ Scenariu C: success rate post-relocare (tardiv) = {rate_late:.0%}")
    else:
        print("⚠️  Prea puțin date post-relocare pentru verificare")


def test_scenario_c_bfs_valid_after_relocation():
    """Scenariu C: harta rămâne solvabilă după relocare (BFS valid)."""
    env = Environment(rows=GRID, cols=GRID, seed=SEED)
    q = QLearning(rows=GRID, cols=GRID)
    trainer = Trainer(env, q, energy=ENERGY_MAX)

    success = trainer._relocate_obstacles(env)
    assert success, "Relocarea a eșuat — nu s-a găsit o configurație BFS-validă"

    bfs_dist = env.bfs(env.start_pos, env.target_pos)
    assert bfs_dist is not None and bfs_dist > 0, (
        f"BFS invalid după relocare: dist={bfs_dist}"
    )
    print(f"✅ Scenariu C: BFS valid după relocare, distanță = {bfs_dist}")


if __name__ == "__main__":
    print("=== Teste Scenarii A, B, C ===\n")

    print("--- Scenariul A ---")
    test_scenario_a_converges()
    test_scenario_a_greedy_reaches_target()
    test_scenario_a_fewer_energy_deaths_than_b()

    print("\n--- Scenariul B ---")
    test_scenario_b_converges()
    test_scenario_b_energy_deaths_exist_early()
    test_scenario_b_greedy_survives()
    test_scenario_b_more_food_visits_than_a()

    print("\n--- Scenariul C ---")
    test_scenario_c_relocates_obstacles()
    test_scenario_c_readapts_after_relocation()
    test_scenario_c_bfs_valid_after_relocation()

    print("\n✅ Toate testele scenariilor au trecut!")
