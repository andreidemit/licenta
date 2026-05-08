"""Teste pentru helper-ele comune de tranziție."""

from src.environment import CellType
from src.transitions import build_step_feedback, is_collision


def test_collision_detection_requires_no_position_change_and_negative_reward():
    result = {
        "new_pos": (2, 2),
        "reward": -5,
        "energy_cost": 1,
        "energy_gain": 0,
        "cell_type": CellType.OBSTACLE,
    }

    assert is_collision(0, result, (2, 2))
    assert not is_collision(4, result, (2, 2))
    assert not is_collision(0, {**result, "new_pos": (1, 2)}, (2, 2))
    assert not is_collision(0, {**result, "reward": 15}, (2, 2))


def test_step_feedback_matches_renderer_contract():
    result = {
        "new_pos": (3, 4),
        "reward": 15,
        "energy_cost": 1,
        "energy_gain": 20,
        "cell_type": CellType.FOOD,
    }

    feedback = build_step_feedback(
        action=3,
        result=result,
        previous_pos=(3, 3),
        terminal_reason=None,
    )

    assert feedback == {
        "action": 3,
        "reward": 15,
        "energy_cost": 1,
        "energy_gain": 20,
        "energy_delta": 19,
        "previous_pos": (3, 3),
        "new_pos": (3, 4),
        "cell_type": "FOOD",
        "terminal_reason": None,
        "is_collision": False,
    }
