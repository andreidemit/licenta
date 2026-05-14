"""Modele Pydantic pentru API-ul Safe Navigation Simulator."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class SafeNavigationRequest(BaseModel):
    algorithm: str = "astar"
    optimization_objective: Literal["balanced", "safety_first", "efficiency_first", "robustness_first"] = "balanced"
    experiment_profile: Literal[
        "known_static",
        "high_risk",
        "stochastic_execution",
        "same_map_learning",
        "transfer_learning",
        "training_cost",
    ] = "known_static"
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
    algorithms: list[str] = Field(
        default_factory=lambda: [
            "random",
            "rule_based",
            "astar",
            "risk_aware_astar",
            "tabular_q",
            "feature_q",
            "feature_risk_astar",
        ]
    )
    optimization_objective: Literal["balanced", "safety_first", "efficiency_first", "robustness_first"] = "balanced"
    experiment_profile: Literal[
        "known_static",
        "high_risk",
        "stochastic_execution",
        "same_map_learning",
        "transfer_learning",
        "training_cost",
    ] = "known_static"
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


class LlmAnalysisRequest(BaseModel):
    config: dict[str, Any] = Field(default_factory=dict)
    summary: dict[str, Any]
    recommendation: dict[str, Any]
    question: str | None = Field(default=None, max_length=1000)
    language: Literal["ro", "en"] = "ro"


class LlmAnalysisResponse(BaseModel):
    answer: str
    key_points: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    used_metrics: list[str] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None
    fallback: bool = False


class EpisodeExplainRequest(BaseModel):
    result: dict[str, Any]
    algorithm: str = ""
    config: dict[str, Any] = Field(default_factory=dict)
    language: Literal["ro", "en"] = "ro"


class MapExplainRequest(BaseModel):
    environment: dict[str, Any]
    config: dict[str, Any] = Field(default_factory=dict)
    language: Literal["ro", "en"] = "ro"


class LlmConfigRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=1000)
    current_config: dict[str, Any] = Field(default_factory=dict)
    language: Literal["ro", "en"] = "ro"


class LlmConfigResponse(BaseModel):
    config: dict[str, Any]
    rationale: str
    warnings: list[str] = Field(default_factory=list)
    applied_fields: list[str] = Field(default_factory=list)
    model: str | None = None
    provider: str | None = None
    fallback: bool = False
