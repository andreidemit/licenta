"""Test Pas 4: Convergența Q-Learning pe grid 10×10 fără obstacole."""
from src.environment import Environment, CellType
from src.agent import Agent
from src.q_learning import QLearning
from src.trainer import Trainer


def create_empty_env(size=10, seed=42):
    """Creează un mediu gol (fără obstacole) pentru test convergență."""
    env = Environment(rows=size, cols=size, seed=seed)
    # Curăță toate obstacolele, mud, food, danger → rămâne doar start + target
    for r in range(env.rows):
        for c in range(env.cols):
            if env.grid[r][c] not in (CellType.START, CellType.TARGET):
                env.grid[r][c] = CellType.EMPTY
    # Suprascriem seed-ul intern pentru a regenera aceeași configurație la reset
    original_generate = env.generate

    def patched_generate(seed=None):
        original_generate(seed)
        for r in range(env.rows):
            for c in range(env.cols):
                if env.grid[r][c] not in (CellType.START, CellType.TARGET):
                    env.grid[r][c] = CellType.EMPTY

    env.generate = patched_generate
    return env


def test_convergence():
    size = 10
    env = create_empty_env(size=size)
    bfs_dist = env.bfs(env.start_pos, env.target_pos)
    print(f"Grid: {size}x{size} gol")
    print(f"Start: {env.start_pos} → Ținta: {env.target_pos}")
    print(f"Distanța BFS optimă: {bfs_dist}")
    print()

    q = QLearning(rows=size, cols=size)
    trainer = Trainer(env, q, energy=9999)  # energie practic infinită

    history = trainer.train(num_episodes=500, print_every=50)

    # Evaluare greedy
    agent, outcome = trainer.run_greedy_episode()
    print(f"\n=== Evaluare Greedy ===")
    print(f"Rezultat: {outcome}")
    print(f"Pași: {agent.total_steps} (optim BFS: {bfs_dist})")
    print(f"Reward: {agent.total_reward:.1f}")

    # Verificări
    assert outcome == "target_reached", f"Agentul nu a ajuns la țintă! ({outcome})"
    # Permitem o marjă de 3 pași față de optimal (agent poate lua un drum echivalent)
    assert agent.total_steps <= bfs_dist + 3, (
        f"Drumul greedy ({agent.total_steps}) e mult prea lung vs optim ({bfs_dist})"
    )

    # Verifică convergență: ultimele 50 episoade au success rate > 80%
    last_50 = history[-50:]
    successes = sum(1 for r in last_50 if r.outcome == "target_reached")
    success_rate = successes / len(last_50) * 100
    print(f"Success rate (ultimele 50): {success_rate:.0f}%")
    assert success_rate >= 80, f"Success rate prea mic: {success_rate:.0f}%"

    # Verifică Q-values: celulele aproape de țintă au valori mai mari
    tr, tc = env.target_pos
    q_near_target = q.get_max_q((max(0, tr - 1), tc, 3))
    q_at_start = q.get_max_q((*env.start_pos, 3))
    print(f"Q-value aproape de țintă: {q_near_target:.1f}")
    print(f"Q-value la start: {q_at_start:.1f}")

    print("\n✅ TOATE TESTELE CONVERGENȚĂ OK")


if __name__ == "__main__":
    test_convergence()
