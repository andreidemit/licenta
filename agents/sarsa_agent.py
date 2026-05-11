"""Agent SARSA tabular (on-policy TD) pe poziții absolute."""

import random

import numpy as np

from agents.base_agent import BaseAgent
from simulation.actions import ALL_ACTIONS


class SarsaAgent(BaseAgent):
    """
    SARSA (State-Action-Reward-State-Action) — algoritm on-policy TD(0).

    Diferența față de Q-Learning:
      Q-Learning: Q(s,a) ← Q(s,a) + α * [r + γ * max_a' Q(s',a') - Q(s,a)]
      SARSA:      Q(s,a) ← Q(s,a) + α * [r + γ * Q(s', a') - Q(s,a)]

    unde a' este acțiunea efectiv aleasă în s' conform politicii epsilon-greedy
    (nu maximul). Aceasta face SARSA mai conservator: evită acțiuni riscante
    chiar dacă ar putea aduce recompensă maximă, deoarece actualizarea reflectă
    comportamentul real al politicii, nu cel ideal.
    """

    name = "SARSA tabular"
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
        # Acțiunea deja aleasă pentru starea următoare (pentru consistența SARSA)
        self._pending_action: int | None = None

    def reset(self):
        self._pending_action = None

    def state_key(self, observation):
        return observation["position"]

    def _epsilon_greedy(self, row: int, col: int) -> int:
        if self._rng.random() < self.epsilon:
            return self._rng.choice(ALL_ACTIONS)
        q_values = self.q_table[row, col]
        max_q = float(np.max(q_values))
        best = [a for a, q in enumerate(q_values) if q == max_q]
        return self._rng.choice(best)

    def select_action(self, observation):
        """
        Returnează acțiunea pentru starea curentă.

        Dacă există o acțiune pre-aleasă în learn() (mecanismul SARSA),
        o returnează pe aceea pentru a garanta că actualizarea Bellman
        și execuția folosesc aceeași acțiune a'.
        """
        if self._pending_action is not None:
            action = self._pending_action
            self._pending_action = None
            return action
        row, col = self.state_key(observation)
        return self._epsilon_greedy(row, col)

    def learn(self, transition):
        """
        Actualizare SARSA:
          Q(s,a) ← Q(s,a) + α * [r + γ * Q(s', a') - Q(s,a)]

        a' se alege cu epsilon-greedy din s' și se stochează ca _pending_action
        pentru a fi returnat de select_action() la pasul următor.
        """
        row, col = transition.state
        nr, nc = transition.next_state
        action = int(transition.action)

        current_q = self.q_table[row, col, action]

        if transition.done:
            target = transition.reward
        else:
            # Alege a' conform politicii curente și salvează-l pentru pasul următor
            next_action = self._epsilon_greedy(nr, nc)
            self._pending_action = next_action
            target = transition.reward + self.gamma * self.q_table[nr, nc, next_action]

        self.q_table[row, col, action] += self.alpha * (target - current_q)

    def end_episode(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        self._pending_action = None

    def explain(self) -> str:
        return (
            "SARSA (on-policy) actualizează Q(s,a) cu acțiunea efectiv aleasă în starea "
            "următoare, nu cu maximul. Aceasta îl face mai conservator față de Q-Learning: "
            "preferă trasee sigure chiar dacă Q-Learning ar alege ceva mai agresiv."
        )
