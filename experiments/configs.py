"""Configurații simple pentru experimentele de navigare sigură."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SafeNavigationConfig:
    scenario: str = "medium"
    rows: int = 15
    cols: int = 15
    wall_probability: float = 0.2
    danger_probability: float = 0.1
    movement_noise: float = 0.0
    max_steps: int = 300
    risk_weight: float = 1.0
    training_episodes: int = 500
    test_episodes: int = 100
    random_seed: int = 42

    def to_dict(self) -> dict:
        return self.__dict__.copy()
