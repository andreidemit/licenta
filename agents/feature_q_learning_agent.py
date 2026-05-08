"""Agent Q-Learning pe features locale, reutilizabile între hărți."""

import random
from collections import defaultdict

import numpy as np

from agents.base_agent import BaseAgent
from environment.cell_types import CellType
from simulation.actions import ACTION_DELTAS, ALL_ACTIONS


class FeatureBasedQLearningAgent(BaseAgent):
    name = "Feature-Based Q-Learning"
    requires_training = True

    def __init__(
        self,
        alpha: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.02,
        epsilon_decay: float = 0.995,
        random_seed: int | None = None,
    ):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_values = defaultdict(lambda: np.zeros(len(ALL_ACTIONS), dtype=float))
        self._rng = random.Random(random_seed)

    def reset(self):
        pass

    def state_key(self, observation):
        row, col = observation["position"]
        goal_row, goal_col = observation["goal"]
        grid = observation["grid"]
        rows = observation["rows"]
        cols = observation["cols"]
        walls = []
        dangers = []
        for action in ALL_ACTIONS:
            dr, dc = ACTION_DELTAS[action]
            nr, nc = row + dr, col + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                walls.append(1)
                dangers.append(0)
                continue
            cell = CellType(grid[nr][nc])
            walls.append(1 if cell == CellType.WALL else 0)
            dangers.append(1 if cell == CellType.DANGER else 0)
        goal_vertical = -1 if goal_row < row else 1 if goal_row > row else 0
        goal_horizontal = -1 if goal_col < col else 1 if goal_col > col else 0
        distance = abs(goal_row - row) + abs(goal_col - col)
        distance_bucket = 0 if distance <= 2 else 1 if distance <= 5 else 2
        return tuple(walls + dangers + [goal_vertical, goal_horizontal, distance_bucket])

    def select_action(self, observation):
        state = self.state_key(observation)
        if self._rng.random() < self.epsilon:
            return self._rng.choice(ALL_ACTIONS)
        q_values = self.q_values[state]
        max_q = np.max(q_values)
        best = np.flatnonzero(q_values == max_q)
        return ALL_ACTIONS[int(self._rng.choice(list(best)))]

    def learn(self, transition):
        action = int(transition.action)
        current_q = self.q_values[transition.state][action]
        target = transition.reward
        if not transition.done:
            target += self.gamma * float(np.max(self.q_values[transition.next_state]))
        self.q_values[transition.state][action] += self.alpha * (target - current_q)

    def end_episode(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def explain(self) -> str:
        return "Învață din pereți/pericole locale și direcția obiectivului, astfel încât politica poate transfera mai bine pe hărți nevăzute."
