"""Agent euristic simplu care evită riscul imediat."""

import random

from agents.base_agent import BaseAgent
from environment.cell_types import CellType
from simulation.actions import ACTION_DELTAS, ALL_ACTIONS


class RuleBasedAgent(BaseAgent):
    name = "Rule-Based"

    def __init__(self, random_seed: int | None = None):
        self._rng = random.Random(random_seed)

    def select_action(self, observation):
        row, col = observation["position"]
        goal = observation["goal"]
        grid = observation["grid"]
        rows = observation["rows"]
        cols = observation["cols"]
        candidates = []
        for action in ALL_ACTIONS:
            dr, dc = ACTION_DELTAS[action]
            nr, nc = row + dr, col + dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue
            cell = CellType(grid[nr][nc])
            if cell in (CellType.WALL, CellType.DANGER):
                continue
            distance = abs(nr - goal[0]) + abs(nc - goal[1])
            candidates.append((distance, action))
        if candidates:
            best_distance = min(distance for distance, _ in candidates)
            best_actions = [action for distance, action in candidates if distance == best_distance]
            return self._rng.choice(best_actions)
        return self._rng.choice(ALL_ACTIONS)

    def explain(self) -> str:
        return "Evită pereții și pericolele imediate, apoi alege mișcarea care reduce distanța Manhattan față de obiectiv."
