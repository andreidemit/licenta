"""Test rapid pentru logica de bază (Pas 1)."""
from src.environment import Environment, CellType
from src.agent import Agent

# Test generare mediu
env = Environment(seed=42)
print(f"Grid: {env.rows}x{env.cols}")
print(f"Start: {env.start_pos}")
print(f"Tinta: {env.target_pos}")
print(f"BFS dist: {env.bfs(env.start_pos, env.target_pos)}")

# Contorizare tipuri celule
counts = {}
for r in range(env.rows):
    for c in range(env.cols):
        t = env.grid[r][c]
        counts[CellType(t).name] = counts.get(CellType(t).name, 0) + 1
print(f"Celule: {counts}")

# Test agent
agent = Agent(start_pos=env.start_pos)
print(f"Agent pos: {agent.position}, Energie: {agent.energy}, Nivel: {agent.get_energy_level()}")

# Test miscare
result = env.try_move(agent.position, 1)  # DOWN
reason = agent.apply_action_result(result)
print(f"Dupa DOWN: pos={agent.position}, energie={agent.energy}, reward={agent.total_reward}")

# Test 100 harti — toate au drum valid
valid = 0
for s in range(100):
    e = Environment(seed=s)
    if e.bfs(e.start_pos, e.target_pos) is not None:
        valid += 1
print(f"Harti valide: {valid}/100")

assert valid == 100, f"Nu toate hartile sunt valide! ({valid}/100)"
print("--- TOATE TESTELE OK ---")
