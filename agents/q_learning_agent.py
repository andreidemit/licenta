"""Agent Q-Learning tabular pe poziții absolute."""

import random

import numpy as np

from agents.base_agent import BaseAgent
from simulation.actions import ALL_ACTIONS


class TabularQLearningAgent(BaseAgent):
    name = "Tabular Q-Learning"
    requires_training = True

    def __init__(
        self,
        rows: int,
        cols: int,
        alpha: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        random_seed: int | None = None,
    ):
        self.rows = rows
        self.cols = cols
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = np.zeros((rows, cols, len(ALL_ACTIONS)), dtype=float)
        self._rng = random.Random(random_seed)

    def reset(self):
        pass

    def state_key(self, observation):
        return observation["position"]

    def select_action(self, observation):
        row, col = self.state_key(observation)
        if self._rng.random() < self.epsilon:
            return self._rng.choice(ALL_ACTIONS)
        q_values = self.q_table[row, col]
        max_q = np.max(q_values)
        best = np.flatnonzero(q_values == max_q)
        return ALL_ACTIONS[int(self._rng.choice(list(best)))]

    def learn(self, transition):
        row, col = transition.state
        nr, nc = transition.next_state
        action = int(transition.action)
        current_q = self.q_table[row, col, action]
        target = transition.reward
        if not transition.done:
            target += self.gamma * float(np.max(self.q_table[nr, nc]))
        self.q_table[row, col, action] += self.alpha * (target - current_q)

    def end_episode(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def explain(self) -> str:
        return "Învață valori Q pentru coordonate absolute. Merge bine pe harta de training, dar de obicei generalizează slab pe hărți noi."
