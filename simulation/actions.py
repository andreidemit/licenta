"""Definiția centralizată a acțiunilor pentru toți agenții."""

from enum import IntEnum


class Action(IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


ACTION_DELTAS = {
    Action.UP: (-1, 0),
    Action.DOWN: (1, 0),
    Action.LEFT: (0, -1),
    Action.RIGHT: (0, 1),
}

ALL_ACTIONS = tuple(Action)

ACTION_NAMES = {
    Action.UP: "UP",
    Action.DOWN: "DOWN",
    Action.LEFT: "LEFT",
    Action.RIGHT: "RIGHT",
}


def coerce_action(action) -> Action:
    """Acceptă fie Action, fie int și returnează Action."""
    return action if isinstance(action, Action) else Action(int(action))
