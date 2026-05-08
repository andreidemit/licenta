"""Mediu GridWorld pentru navigare sigură în hărți necunoscute."""

import random
from dataclasses import dataclass, field

from environment.cell_types import CellType
from environment.risk_model import RiskModel
from simulation.actions import ACTION_DELTAS, ALL_ACTIONS, Action, coerce_action


@dataclass(frozen=True)
class RewardConfig:
    goal: float = 100.0
    danger: float = -100.0
    wall: float = -10.0
    step: float = -1.0
    closer: float = 2.0
    farther: float = -2.0
    risk_weight: float = 0.0


@dataclass
class GridWorld:
    grid: list[list[CellType | int]]
    start_pos: tuple[int, int]
    goal_pos: tuple[int, int]
    reward_config: RewardConfig = field(default_factory=RewardConfig)
    risk_model: RiskModel = field(default_factory=RiskModel)
    movement_noise: float = 0.0
    random_seed: int | None = None

    def __post_init__(self):
        if not self.grid or not self.grid[0]:
            raise ValueError("GridWorld necesită un grid ne-gol.")
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        if any(len(row) != self.cols for row in self.grid):
            raise ValueError("Toate rândurile gridului trebuie să aibă aceeași lungime.")
        self.grid = [[CellType(cell) for cell in row] for row in self.grid]
        self._rng = random.Random(self.random_seed)
        self.agent_pos = self.start_pos
        self.total_risk_exposure = 0.0
        self.risk_map = self.risk_model.compute_risk_map(self.grid)
        self._place_markers()

    def _place_markers(self):
        sr, sc = self.start_pos
        gr, gc = self.goal_pos
        self.grid[sr][sc] = CellType.START
        self.grid[gr][gc] = CellType.GOAL

    def reset(self):
        self.agent_pos = self.start_pos
        self.total_risk_exposure = 0.0
        return self.get_observation()

    def get_observation(self) -> dict:
        return {
            "position": self.agent_pos,
            "start": self.start_pos,
            "goal": self.goal_pos,
            "grid": self.grid,
            "rows": self.rows,
            "cols": self.cols,
            "risk_map": self.risk_map,
            "distance_to_goal": self.distance_to_goal(self.agent_pos),
        }

    def in_bounds(self, position: tuple[int, int]) -> bool:
        row, col = position
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_cell(self, position: tuple[int, int]) -> CellType:
        if not self.in_bounds(position):
            return CellType.WALL
        row, col = position
        return CellType(self.grid[row][col])

    def is_wall(self, position: tuple[int, int]) -> bool:
        return self.get_cell(position) == CellType.WALL

    def is_danger(self, position: tuple[int, int]) -> bool:
        return self.get_cell(position) == CellType.DANGER

    def is_goal(self, position: tuple[int, int]) -> bool:
        return position == self.goal_pos or self.get_cell(position) == CellType.GOAL

    def is_traversable(self, position: tuple[int, int], avoid_danger: bool = True) -> bool:
        if not self.in_bounds(position) or self.is_wall(position):
            return False
        if avoid_danger and self.is_danger(position):
            return False
        return True

    def neighbors(self, position: tuple[int, int], avoid_danger: bool = True):
        row, col = position
        for action, (dr, dc) in ACTION_DELTAS.items():
            next_pos = (row + dr, col + dc)
            if self.is_traversable(next_pos, avoid_danger=avoid_danger):
                yield action, next_pos

    def distance_to_goal(self, position: tuple[int, int]) -> int:
        row, col = position
        gr, gc = self.goal_pos
        return abs(row - gr) + abs(col - gc)

    def risk_at(self, position: tuple[int, int]) -> float:
        if not self.in_bounds(position):
            return self.risk_model.danger_cost
        row, col = position
        return float(self.risk_map[row][col])

    def _apply_movement_noise(self, action: Action) -> Action:
        if self.movement_noise <= 0 or self._rng.random() >= self.movement_noise:
            return action
        lateral = {
            Action.UP: (Action.LEFT, Action.RIGHT),
            Action.DOWN: (Action.LEFT, Action.RIGHT),
            Action.LEFT: (Action.UP, Action.DOWN),
            Action.RIGHT: (Action.UP, Action.DOWN),
        }
        return self._rng.choice(lateral.get(action, ALL_ACTIONS))

    def step(self, action):
        requested_action = coerce_action(action)
        executed_action = self._apply_movement_noise(requested_action)
        previous = self.agent_pos
        old_distance = self.distance_to_goal(previous)
        dr, dc = ACTION_DELTAS[executed_action]
        candidate = (previous[0] + dr, previous[1] + dc)

        collision = not self.in_bounds(candidate) or self.is_wall(candidate)
        entered_danger = False
        reached_goal = False
        done = False
        event_type = "step"
        new_pos = previous

        if collision:
            reward = self.reward_config.wall
            event_type = "collision"
        else:
            new_pos = candidate
            self.agent_pos = new_pos
            entered_danger = self.is_danger(new_pos)
            reached_goal = self.is_goal(new_pos)
            if reached_goal:
                reward = self.reward_config.goal
                done = True
                event_type = "goal"
            elif entered_danger:
                reward = self.reward_config.danger
                done = True
                event_type = "danger"
            else:
                reward = self.reward_config.step
                new_distance = self.distance_to_goal(new_pos)
                if new_distance < old_distance:
                    reward += self.reward_config.closer
                elif new_distance > old_distance:
                    reward += self.reward_config.farther

        risk_cost = self.risk_at(new_pos)
        self.total_risk_exposure += risk_cost
        reward -= self.reward_config.risk_weight * risk_cost

        info = {
            "reached_goal": reached_goal,
            "collision": collision,
            "entered_danger": entered_danger,
            "current_position": new_pos,
            "previous_position": previous,
            "risk_cost": risk_cost,
            "total_risk_exposure": self.total_risk_exposure,
            "distance_to_goal": self.distance_to_goal(new_pos),
            "event_type": event_type,
            "requested_action": int(requested_action),
            "executed_action": int(executed_action),
        }
        return self.get_observation(), reward, done, info

    def to_payload(self, include_risk: bool = True) -> dict:
        payload = {
            "rows": self.rows,
            "cols": self.cols,
            "start": list(self.start_pos),
            "goal": list(self.goal_pos),
            "grid": [[int(cell) for cell in row] for row in self.grid],
        }
        if include_risk:
            payload["risk_map"] = self.risk_map
        return payload
