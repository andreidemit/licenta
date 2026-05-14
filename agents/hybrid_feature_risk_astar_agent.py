"""Strategie hibridă experimentală: features locale + planificare risk-aware."""

from __future__ import annotations

import random
from collections import defaultdict

from agents.astar_agent import RiskAwareAStarAgent
from agents.feature_q_learning_agent import FeatureBasedQLearningAgent
from simulation.actions import ALL_ACTIONS


class FeatureRiskAwareAStarAgent(RiskAwareAStarAgent):
    """Planifică cu A*, dar ajustează costurile locale din experiență.

    Agentul folosește harta de risc explicită ca Risk-Aware A*, iar în training
    acumulează penalizări pentru tipare locale care au produs coliziuni, risc
    sau intrări în pericol. Este marcat experimental deoarece nu este un nou
    algoritm RL complet, ci o punte extensibilă între learning și planning.
    """

    name = "Feature-Risk A*"
    requires_training = True

    def __init__(
        self,
        risk_weight: float = 1.0,
        learned_weight: float = 0.35,
        alpha: float = 0.2,
        epsilon: float = 0.25,
        epsilon_min: float = 0.02,
        epsilon_decay: float = 0.98,
        random_seed: int | None = None,
    ):
        super().__init__(risk_weight=risk_weight)
        self.learned_weight = learned_weight
        self.alpha = alpha
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.feature_encoder = FeatureBasedQLearningAgent(random_seed=random_seed)
        self.learned_costs = defaultdict(float)
        self._rng = random.Random(random_seed)

    def reset(self):
        self._planned_actions = []
        self.frontier_size = 0

    def state_key(self, observation):
        return self.feature_encoder.state_key(observation)

    def _state_key_for_position(self, observation, position: tuple[int, int]):
        shifted = dict(observation)
        shifted["position"] = position
        return self.state_key(shifted)

    def movement_cost(self, observation, position: tuple[int, int]) -> float:
        base_cost = super().movement_cost(observation, position)
        feature_key = self._state_key_for_position(observation, position)
        return base_cost + self.learned_weight * self.learned_costs[feature_key]

    def select_action(self, observation):
        if self._rng.random() < self.epsilon:
            self._planned_actions = []
            return self._rng.choice(ALL_ACTIONS)
        self._planned_actions = []
        return super().select_action(observation)

    def learn(self, transition):
        info = transition.info or {}
        observed_penalty = float(info.get("risk_cost", 0.0) or 0.0)
        if info.get("collision"):
            observed_penalty += 10.0
        if info.get("entered_danger"):
            observed_penalty += 100.0
        current = self.learned_costs[transition.state]
        self.learned_costs[transition.state] = current + self.alpha * (observed_penalty - current)

    def end_episode(self):
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def explain(self) -> str:
        return (
            "Strategie experimentală: folosește Risk-Aware A* pentru planificare, dar ajustează costurile "
            "cu penalizări locale învățate din experiență. Scopul este să testeze dacă tiparele locale pot "
            "îmbunătăți planificarea pe hărți generate."
        )
