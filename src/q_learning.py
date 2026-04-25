"""
Modulul Q-Learning: Q-Table, politica Epsilon-Greedy, actualizarea Bellman.
"""

import random
import numpy as np

from src.constants import (
    NUM_ACTIONS,
    ALPHA, GAMMA,
    EPSILON_START, EPSILON_MIN, EPSILON_DECAY,
)


class QLearning:
    """
    Implementare Q-Learning tabular.

    Q-Table: numpy array cu dimensiunile (rows, cols, energy_levels, num_actions).
    Starea = (row, col, energy_level) — un tuplu de 3 întregi.
    """

    def __init__(self, rows, cols, energy_levels=4, num_actions=NUM_ACTIONS,
                 alpha=ALPHA, gamma=GAMMA,
                 epsilon=EPSILON_START, epsilon_min=EPSILON_MIN,
                 epsilon_decay=EPSILON_DECAY):
        self.rows = rows
        self.cols = cols
        self.energy_levels = energy_levels
        self.num_actions = num_actions

        # Hiperparametri
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        # Q-Table inițializată cu zero
        self.q_table = np.zeros((rows, cols, energy_levels, num_actions))

        # --- Instrumentare pentru vizualizare învățare ---
        # Contor vizite per (row, col) — acumulat pe toate episoadele
        self.visit_counts = np.zeros((rows, cols), dtype=np.int64)
        # Magnitudine TD-error decăzută per (row, col) — pentru heatmap "unde se învață"
        self.td_error_map = np.zeros((rows, cols), dtype=np.float64)
        self._td_decay = 0.97  # factor de decădere per pas
        # Ultimul pas de actualizare: (row, col, energy_level, action, td_error)
        self.last_update = None
        # Ring buffer pentru sparkline-uri (mean |TD| pe ultimii N pași)
        self._td_history_size = 200
        self._td_history = np.zeros(self._td_history_size, dtype=np.float64)
        self._td_history_idx = 0
        self._td_history_filled = 0

    # ------------------------------------------------------------------
    # Selecție acțiune — Epsilon-Greedy
    # ------------------------------------------------------------------

    def choose_action(self, state):
        """
        Selectează o acțiune folosind politica Epsilon-Greedy.

        Args:
            state: tuplu (row, col, energy_level)

        Returns:
            int — indexul acțiunii (0-4)
        """
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        else:
            r, c, e = state
            q_values = self.q_table[r, c, e]
            # Dacă mai multe acțiuni au aceeași valoare maximă, alege aleatoriu dintre ele
            max_q = np.max(q_values)
            best_actions = np.where(q_values == max_q)[0]
            return int(np.random.choice(best_actions))

    # ------------------------------------------------------------------
    # Actualizare Q-Value — Ecuația Bellman
    # ------------------------------------------------------------------

    def update(self, state, action, reward, next_state, done):
        """
        Actualizează Q-Table conform ecuației Bellman:
        Q(S,A) ← Q(S,A) + α * [R + γ * max Q(S',a') - Q(S,A)]

        Args:
            state: (row, col, energy_level)
            action: int (0-4)
            reward: float
            next_state: (row, col, energy_level)
            done: bool — episod terminat
        """
        r, c, e = state
        nr, nc, ne = next_state

        current_q = self.q_table[r, c, e, action]

        if done:
            target = reward
        else:
            target = reward + self.gamma * np.max(self.q_table[nr, nc, ne])

        td_error = target - current_q
        self.q_table[r, c, e, action] += self.alpha * td_error

        # --- Instrumentare ---
        self.visit_counts[r, c] += 1
        # Decădere globală + injectare în celula curentă (mărimea TD-error)
        self.td_error_map *= self._td_decay
        self.td_error_map[r, c] += abs(td_error)
        self.last_update = (r, c, e, action, float(td_error))
        self._td_history[self._td_history_idx] = abs(td_error)
        self._td_history_idx = (self._td_history_idx + 1) % self._td_history_size
        if self._td_history_filled < self._td_history_size:
            self._td_history_filled += 1

    # ------------------------------------------------------------------
    # Decay Epsilon
    # ------------------------------------------------------------------

    def decay_epsilon(self):
        """Reduce epsilon (explorare → exploatare) după fiecare episod."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    # ------------------------------------------------------------------
    # Utilități
    # ------------------------------------------------------------------

    def get_best_action(self, state):
        """Returnează acțiunea cu Q-value maxim pentru o stare dată (fără explorare)."""
        r, c, e = state
        return int(np.argmax(self.q_table[r, c, e]))

    def get_q_values(self, state):
        """Returnează vectorul Q-values pentru o stare dată."""
        r, c, e = state
        return self.q_table[r, c, e].copy()

    def get_max_q(self, state):
        """Returnează valoarea Q maximă pentru o stare dată."""
        r, c, e = state
        return float(np.max(self.q_table[r, c, e]))

    def get_state_count(self):
        """Returnează numărul total de stări din Q-Table."""
        return self.rows * self.cols * self.energy_levels

    def get_nonzero_count(self):
        """Returnează numărul de intrări nenule din Q-Table."""
        return int(np.count_nonzero(self.q_table))

    # ------------------------------------------------------------------
    # Instrumentare — getteri pentru vizualizare
    # ------------------------------------------------------------------

    def get_visit_counts(self):
        """Returnează matricea (rows, cols) cu numărul de vizite per celulă."""
        return self.visit_counts

    def get_td_error_map(self):
        """Returnează harta TD-error decăzută per celulă."""
        return self.td_error_map

    def get_last_update(self):
        """Returnează (row, col, energy_level, action, td_error) sau None."""
        return self.last_update

    def get_recent_mean_td(self):
        """Media |TD-error| pe fereastra recentă."""
        if self._td_history_filled == 0:
            return 0.0
        return float(np.mean(self._td_history[:self._td_history_filled]))

    def get_knowledge_stats(self):
        """Returnează un dict cu metrici sintetice de cunoaștere."""
        nonzero = int(np.count_nonzero(self.q_table))
        total = self.q_table.size
        visited_cells = int(np.count_nonzero(self.visit_counts))
        total_cells = self.visit_counts.size
        mean_abs_q = float(np.mean(np.abs(self.q_table))) if nonzero > 0 else 0.0
        return {
            "nonzero": nonzero,
            "total": total,
            "fill_pct": (nonzero / total * 100) if total else 0.0,
            "visited_cells": visited_cells,
            "total_cells": total_cells,
            "coverage_pct": (visited_cells / total_cells * 100) if total_cells else 0.0,
            "mean_abs_q": mean_abs_q,
            "mean_recent_td": self.get_recent_mean_td(),
        }

    # ------------------------------------------------------------------
    # Persistență Q-Table
    # ------------------------------------------------------------------

    def save(self, filepath: str) -> None:
        """Salvează Q-Table pe disc ca fișier .npy."""
        import os
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        np.save(filepath, self.q_table)

    def load(self, filepath: str) -> None:
        """
        Încarcă Q-Table din fișier .npy.
        Resetează epsilon la EPSILON_MIN (tabelul e deja antrenat).
        """
        loaded = np.load(filepath)
        if loaded.shape != self.q_table.shape:
            raise ValueError(
                f"Shape incompatibil: fișierul are {loaded.shape}, "
                f"Q-Table curentă are {self.q_table.shape}"
            )
        self.q_table = loaded
        self.epsilon = self.epsilon_min
        # Resetăm instrumentarea — datele de runtime nu sunt persistate
        self.visit_counts = np.zeros((self.rows, self.cols), dtype=np.int64)
        self.td_error_map = np.zeros((self.rows, self.cols), dtype=np.float64)
        self.last_update = None
        self._td_history = np.zeros(self._td_history_size, dtype=np.float64)
        self._td_history_idx = 0
        self._td_history_filled = 0
