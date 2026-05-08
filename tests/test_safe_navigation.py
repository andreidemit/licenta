"""Validări pentru noul cadru de simulare safe navigation."""

from agents import AStarAgent, RiskAwareAStarAgent, TabularQLearningAgent
from environment.cell_types import CellType
from environment.grid_world import GridWorld
from environment.map_generator import MapGenerator
from simulation.actions import Action
from simulation.metrics import aggregate_results
from simulation.simulator import Simulator


def test_grid_world_step_reports_collision_and_goal():
    grid = [
        [CellType.START, CellType.WALL, CellType.EMPTY],
        [CellType.EMPTY, CellType.EMPTY, CellType.GOAL],
    ]
    env = GridWorld(grid=grid, start_pos=(0, 0), goal_pos=(1, 2))
    _, reward, done, info = env.step(Action.RIGHT)
    assert reward == -10
    assert not done
    assert info["collision"]
    _, _, done, info = env.step(Action.DOWN)
    assert not done
    _, _, done, info = env.step(Action.RIGHT)
    assert not done
    _, reward, done, info = env.step(Action.RIGHT)
    assert done
    assert reward == 100
    assert info["reached_goal"]


def test_map_generator_produces_solvable_maps():
    generator = MapGenerator()
    env = generator.generate(10, 10, 0.1, 0.05, random_seed=7)
    assert generator.is_solvable(env.grid, env.start_pos, env.goal_pos)


def test_astar_reaches_goal_when_path_exists():
    env = MapGenerator().generate(8, 8, 0.05, 0.0, random_seed=3)
    result = Simulator(env, AStarAgent(), max_steps=100).run_episode()
    assert result.success
    assert result.collisions == 0


def test_risk_aware_astar_reduces_risk_when_alternative_exists():
    grid = [[CellType.EMPTY for _ in range(5)] for _ in range(5)]
    grid[2][0] = CellType.START
    grid[2][4] = CellType.GOAL
    grid[1][2] = CellType.DANGER
    direct_env = GridWorld(grid=[row[:] for row in grid], start_pos=(2, 0), goal_pos=(2, 4))
    safe_env = GridWorld(grid=[row[:] for row in grid], start_pos=(2, 0), goal_pos=(2, 4))

    direct = Simulator(direct_env, AStarAgent(), max_steps=40).run_episode()
    safe = Simulator(safe_env, RiskAwareAStarAgent(risk_weight=2.0), max_steps=40).run_episode()

    assert direct.success and safe.success
    assert safe.total_risk_exposure < direct.total_risk_exposure
    assert safe.steps >= direct.steps


def test_tabular_q_learning_can_learn_simple_map():
    grid = [[CellType.EMPTY for _ in range(4)] for _ in range(4)]
    grid[0][0] = CellType.START
    grid[3][3] = CellType.GOAL
    env = GridWorld(grid=grid, start_pos=(0, 0), goal_pos=(3, 3), random_seed=1)
    agent = TabularQLearningAgent(rows=4, cols=4, epsilon=0.5, epsilon_decay=0.98, random_seed=1)
    simulator = Simulator(env, agent, max_steps=30)
    for _ in range(250):
        simulator.run_episode(training=True)
    agent.epsilon = 0.0
    result = simulator.run_episode(training=False)
    assert result.success


def test_metrics_aggregation_computes_average_values():
    env = MapGenerator().generate(6, 6, 0.0, 0.0, random_seed=1)
    result_a = Simulator(env, AStarAgent(), max_steps=30).run_episode()
    env2 = MapGenerator().generate(6, 6, 0.0, 0.0, random_seed=1)
    result_b = Simulator(env2, AStarAgent(), max_steps=30).run_episode()
    summary = aggregate_results([result_a, result_b])
    row = summary["agents"][0]
    assert row["algorithm"] == "A*"
    assert row["episodes"] == 2
    assert row["success_rate"] == 1.0
    assert row["average_steps"] == result_a.steps
