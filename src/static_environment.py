"""
Mediu static încărcat din JSON pentru evaluări web pe hărți personalizate.
"""

from src.environment import Environment, CellType


class StaticEnvironment(Environment):
    """Mediu cu layout fix primit dintr-un payload JSON."""

    def __init__(self, grid, start_pos, target_pos, name="personalizat"):
        self.name = name
        self._source_grid = [
            [CellType(cell) for cell in row]
            for row in grid
        ]
        self._source_start = tuple(start_pos)
        self._source_target = tuple(target_pos)
        rows = len(self._source_grid)
        cols = len(self._source_grid[0]) if rows else 0
        if rows == 0 or cols == 0:
            raise ValueError("StaticEnvironment necesită un grid ne-gol.")
        if any(len(row) != cols for row in self._source_grid):
            raise ValueError("Toate rândurile gridului static trebuie să aibă aceeași lungime.")
        super().__init__(rows=rows, cols=cols, seed=None)

    def generate(self, seed=None):
        """Construiește harta din layout-ul fix."""
        self.grid = [row[:] for row in self._source_grid]
        self.start_pos = self._source_start
        self.target_pos = self._source_target
        self.grid[self.start_pos[0]][self.start_pos[1]] = CellType.START
        self.grid[self.target_pos[0]][self.target_pos[1]] = CellType.TARGET
        if not self._validate_path():
            raise ValueError("Harta statică nu are drum valid start→target.")

    def reset(self, seed=None):
        """Resetează la același layout static."""
        self.generate(seed=None)
