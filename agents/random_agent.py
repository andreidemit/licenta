"""Baseline aleator."""

import random

from agents.base_agent import BaseAgent
from simulation.actions import ALL_ACTIONS


class RandomAgent(BaseAgent):
    name = "Random"

    def __init__(self, random_seed: int | None = None):
        self._rng = random.Random(random_seed)

    def select_action(self, observation):
        return self._rng.choice(ALL_ACTIONS)

    def explain(self) -> str:
        return "Alege aleator o acțiune validă din spațiul comun. Este baseline-ul minim pentru comparații."
