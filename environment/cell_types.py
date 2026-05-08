"""Tipurile de celule folosite de GridWorld."""

from enum import IntEnum


class CellType(IntEnum):
    EMPTY = 0
    WALL = 1
    DANGER = 2
    START = 3
    GOAL = 4


CELL_LABELS = {
    CellType.EMPTY: "EMPTY",
    CellType.WALL: "WALL",
    CellType.DANGER: "DANGER",
    CellType.START: "START",
    CellType.GOAL: "GOAL",
}
