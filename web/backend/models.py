"""Modele Pydantic pentru API-ul web."""

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from src.constants import MIN_MANHATTAN_DISTANCE


class TrainRequest(BaseModel):
    scenario: Literal["A", "B", "C", "WAREHOUSE"] = "B"
    rows: int = Field(default=20, ge=5, le=50)
    cols: int = Field(default=20, ge=5, le=50)
    seed: int = 42
    episodes: int = Field(default=2000, ge=1, le=100000)
    energy: int | None = Field(default=None, ge=1)
    alpha: float = Field(default=0.1, gt=0, le=1)
    gamma: float = Field(default=0.95, ge=0, le=1)
    max_steps: int | None = Field(default=None, ge=1, le=10000)

    @model_validator(mode="after")
    def validate_grid_can_place_start_and_target(self):
        if self.scenario != "WAREHOUSE" and self.rows + self.cols - 2 < MIN_MANHATTAN_DISTANCE:
            raise ValueError(
                "gridul este prea mic pentru distanța Manhattan minimă configurată "
                f"({MIN_MANHATTAN_DISTANCE})"
            )
        return self


class EnvironmentPayload(BaseModel):
    id: str | None = None
    name: str = "personalizat"
    rows: int = Field(ge=1, le=100)
    cols: int = Field(ge=1, le=100)
    start: list[int]
    target: list[int]
    grid: list[list[int]]

    @model_validator(mode="after")
    def validate_shape(self):
        if len(self.grid) != self.rows:
            raise ValueError("rows trebuie să corespundă înălțimii gridului")
        if any(len(row) != self.cols for row in self.grid):
            raise ValueError("cols trebuie să corespundă lățimii fiecărui rând")
        for label, position in (("pornirea", self.start), ("ținta", self.target)):
            if len(position) != 2:
                raise ValueError(f"{label} trebuie să conțină [rând, coloană]")
            row, col = position
            if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
                raise ValueError(f"{label} trebuie să fie în interiorul gridului")
        return self


class EvaluateRequest(BaseModel):
    qtable_path: str
    environments: list[EnvironmentPayload]
    energy: int = Field(default=100, ge=1)


class JobSummary(BaseModel):
    id: str
    status: str
    scenario: str
    progress: float = 0.0
    message: str = ""
    artifacts: dict[str, str] = Field(default_factory=dict)
    error: str | None = None
    latest_event: dict[str, Any] | None = None


class SafeNavigationRequest(BaseModel):
    algorithm: str = "astar"
    scenario: Literal["easy", "medium", "hard", "custom"] = "medium"
    rows: int = Field(default=15, ge=5, le=50)
    cols: int = Field(default=15, ge=5, le=50)
    wall_probability: float = Field(default=0.2, ge=0, le=0.6)
    danger_probability: float = Field(default=0.1, ge=0, le=0.4)
    movement_noise: float = Field(default=0.0, ge=0, le=1)
    risk_weight: float = Field(default=1.0, ge=0, le=10)
    max_steps: int = Field(default=300, ge=1, le=5000)
    training_episodes: int = Field(default=100, ge=0, le=10000)
    random_seed: int = 42


class MonteCarloRequest(BaseModel):
    algorithms: list[str] = Field(default_factory=lambda: ["astar", "risk_aware_astar"])
    scenario: Literal["easy", "medium", "hard", "custom"] = "medium"
    number_of_maps: int = Field(default=5, ge=1, le=100)
    episodes_per_map: int = Field(default=2, ge=1, le=100)
    training_episodes: int = Field(default=100, ge=0, le=10000)
    rows: int = Field(default=15, ge=5, le=50)
    cols: int = Field(default=15, ge=5, le=50)
    wall_probability: float = Field(default=0.2, ge=0, le=0.6)
    danger_probability: float = Field(default=0.1, ge=0, le=0.4)
    movement_noise: float = Field(default=0.0, ge=0, le=1)
    risk_weight: float = Field(default=1.0, ge=0, le=10)
    max_steps: int = Field(default=300, ge=1, le=5000)
    random_seed: int = 42
