"""Generator procedural de hărți GridWorld cu validare BFS."""

import random
from collections import deque
from dataclasses import dataclass

from environment.cell_types import CellType
from environment.grid_world import GridWorld, RewardConfig
from environment.risk_model import RiskModel
from simulation.actions import ACTION_DELTAS


@dataclass(frozen=True)
class ScenarioConfig:
    rows: int
    cols: int
    wall_probability: float
    danger_probability: float


SCENARIOS = {
    "easy": ScenarioConfig(rows=10, cols=10, wall_probability=0.10, danger_probability=0.05),
    "medium": ScenarioConfig(rows=15, cols=15, wall_probability=0.20, danger_probability=0.10),
    "hard": ScenarioConfig(rows=20, cols=20, wall_probability=0.25, danger_probability=0.15),
}


class MapGenerator:
    def __init__(self, risk_model: RiskModel | None = None):
        self.risk_model = risk_model or RiskModel()

    def generate(
        self,
        rows: int,
        cols: int,
        wall_probability: float,
        danger_probability: float,
        random_seed: int | None = None,
        start_pos: tuple[int, int] | None = None,
        goal_pos: tuple[int, int] | None = None,
        movement_noise: float = 0.0,
        reward_config: RewardConfig | None = None,
        max_attempts: int = 1000,
    ) -> GridWorld:
        for attempt in range(max_attempts):
            seed = None if random_seed is None else random_seed + attempt
            rng = random.Random(seed)
            start = start_pos or (0, 0)
            goal = goal_pos or (rows - 1, cols - 1)
            grid = [[CellType.EMPTY for _ in range(cols)] for _ in range(rows)]
            for row in range(rows):
                for col in range(cols):
                    if (row, col) in (start, goal):
                        continue
                    sample = rng.random()
                    if sample < wall_probability:
                        grid[row][col] = CellType.WALL
                    elif sample < wall_probability + danger_probability:
                        grid[row][col] = CellType.DANGER
            grid[start[0]][start[1]] = CellType.START
            grid[goal[0]][goal[1]] = CellType.GOAL
            if self.is_solvable(grid, start, goal):
                return GridWorld(
                    grid=grid,
                    start_pos=start,
                    goal_pos=goal,
                    reward_config=reward_config or RewardConfig(),
                    risk_model=self.risk_model,
                    movement_noise=movement_noise,
                    random_seed=seed,
                )
        raise RuntimeError("Nu s-a putut genera o hartă rezolvabilă.")

    def from_scenario(
        self,
        scenario: str,
        random_seed: int | None = None,
        movement_noise: float = 0.0,
        reward_config: RewardConfig | None = None,
    ) -> GridWorld:
        if scenario not in SCENARIOS:
            raise ValueError(f"Scenariu necunoscut: {scenario}")
        config = SCENARIOS[scenario]
        return self.generate(
            rows=config.rows,
            cols=config.cols,
            wall_probability=config.wall_probability,
            danger_probability=config.danger_probability,
            random_seed=random_seed,
            movement_noise=movement_noise,
            reward_config=reward_config,
        )

    def is_solvable(
        self,
        grid: list[list[CellType]],
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> bool:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        queue = deque([start])
        visited = {start}
        while queue:
            row, col = queue.popleft()
            if (row, col) == goal:
                return True
            for dr, dc in ACTION_DELTAS.values():
                nr, nc = row + dr, col + dc
                if not (0 <= nr < rows and 0 <= nc < cols) or (nr, nc) in visited:
                    continue
                cell = CellType(grid[nr][nc])
                if cell in (CellType.WALL, CellType.DANGER):
                    continue
                visited.add((nr, nc))
                queue.append((nr, nc))
        return False
