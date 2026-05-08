"""Structuri de date pentru tranziții și rezultate de episod."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Transition:
    state: Any
    action: int
    reward: float
    next_state: Any
    done: bool
    info: dict = field(default_factory=dict)


@dataclass(slots=True)
class EpisodeResult:
    algorithm: str
    success: bool
    total_reward: float
    steps: int
    collisions: int
    danger_entries: int
    total_risk_exposure: float
    path: list[tuple[int, int]]
    reached_goal: bool
    timeout: bool
    events: list[dict]
    computation_time_ms: float = 0.0

    @property
    def path_length(self) -> int:
        return max(0, len(self.path) - 1)

    @property
    def total_cost(self) -> float:
        return -self.total_reward + self.total_risk_exposure

    def to_dict(self) -> dict:
        return {
            "algorithm": self.algorithm,
            "success": self.success,
            "total_reward": self.total_reward,
            "steps": self.steps,
            "collisions": self.collisions,
            "danger_entries": self.danger_entries,
            "total_risk_exposure": self.total_risk_exposure,
            "path": [list(pos) for pos in self.path],
            "path_length": self.path_length,
            "reached_goal": self.reached_goal,
            "timeout": self.timeout,
            "events": self.events,
            "computation_time_ms": self.computation_time_ms,
            "total_cost": self.total_cost,
        }
