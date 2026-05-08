"""Model de risc derivat din pozițiile celulelor periculoase."""

from dataclasses import dataclass

from environment.cell_types import CellType


@dataclass(frozen=True)
class RiskModel:
    danger_cost: float = 100.0
    distance_1_cost: float = 10.0
    distance_2_cost: float = 5.0
    distance_3_cost: float = 2.0

    def compute_risk_map(self, grid: list[list[CellType]]) -> list[list[float]]:
        rows = len(grid)
        cols = len(grid[0]) if rows else 0
        danger_positions = [
            (row, col)
            for row in range(rows)
            for col in range(cols)
            if CellType(grid[row][col]) == CellType.DANGER
        ]
        risk = [[0.0 for _ in range(cols)] for _ in range(rows)]

        for row in range(rows):
            for col in range(cols):
                if CellType(grid[row][col]) == CellType.DANGER:
                    risk[row][col] = self.danger_cost
                    continue
                if not danger_positions:
                    continue
                nearest = min(abs(row - dr) + abs(col - dc) for dr, dc in danger_positions)
                if nearest == 1:
                    risk[row][col] = self.distance_1_cost
                elif nearest == 2:
                    risk[row][col] = self.distance_2_cost
                elif nearest == 3:
                    risk[row][col] = self.distance_3_cost
        return risk

    def cell_risk(self, grid: list[list[CellType]], position: tuple[int, int]) -> float:
        row, col = position
        return self.compute_risk_map(grid)[row][col]
