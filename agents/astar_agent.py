"""Agenți A* clasici și risk-aware."""

import heapq

from agents.base_agent import BaseAgent
from environment.cell_types import CellType
from simulation.actions import ACTION_DELTAS, Action


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class AStarAgent(BaseAgent):
    name = "A*"

    def __init__(self, block_danger: bool = True):
        self.block_danger = block_danger
        self._planned_actions: list[Action] = []
        self.frontier_size = 0

    def reset(self):
        self._planned_actions = []
        self.frontier_size = 0

    def movement_cost(self, observation, position: tuple[int, int]) -> float:
        return 1.0

    def is_blocked(self, observation, position: tuple[int, int]) -> bool:
        row, col = position
        if not (0 <= row < observation["rows"] and 0 <= col < observation["cols"]):
            return True
        cell = CellType(observation["grid"][row][col])
        if cell == CellType.WALL:
            return True
        return self.block_danger and cell == CellType.DANGER

    def select_action(self, observation):
        if not self._planned_actions:
            self._planned_actions = self._plan(observation)
        if self._planned_actions:
            return self._planned_actions.pop(0)
        return Action.UP

    def _plan(self, observation) -> list[Action]:
        start = observation["position"]
        goal = observation["goal"]
        frontier = [(0.0, start)]
        came_from: dict[tuple[int, int], tuple[tuple[int, int], Action] | None] = {start: None}
        cost_so_far = {start: 0.0}

        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal:
                break
            for action, (dr, dc) in ACTION_DELTAS.items():
                next_pos = (current[0] + dr, current[1] + dc)
                if self.is_blocked(observation, next_pos):
                    continue
                new_cost = cost_so_far[current] + self.movement_cost(observation, next_pos)
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + manhattan(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = (current, action)
        self.frontier_size = len(cost_so_far)
        if goal not in came_from:
            return []
        actions: list[Action] = []
        current = goal
        while current != start:
            previous, action = came_from[current]
            actions.append(action)
            current = previous
        actions.reverse()
        return actions

    def explain(self) -> str:
        return "Planifică drumul cel mai scurt cu euristică Manhattan. Este rapid pe hărți noi, dar nu optimizează explicit expunerea la risc."


class RiskAwareAStarAgent(AStarAgent):
    name = "Risk-Aware A*"

    def __init__(self, risk_weight: float = 1.0, block_danger: bool = True):
        super().__init__(block_danger=block_danger)
        self.risk_weight = risk_weight

    def movement_cost(self, observation, position: tuple[int, int]) -> float:
        row, col = position
        risk_map = observation.get("risk_map") or []
        risk = risk_map[row][col] if risk_map else 0.0
        return 1.0 + self.risk_weight * risk

    def explain(self) -> str:
        return "Planifică folosind distanță plus cost de risc, preferând trasee mai sigure chiar dacă sunt mai lungi."
