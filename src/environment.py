"""
Mediul de simulare: grid 2D cu tipuri de celule, generare procedurală și validare topologică.
"""

import random
from collections import deque
from enum import IntEnum

from src.constants import (
    GRID_ROWS, GRID_COLS,
    OBSTACLE_DENSITY, MUD_DENSITY, FOOD_DENSITY, DANGER_DENSITY,
    MIN_MANHATTAN_DISTANCE,
    ENERGY_COST_NORMAL, ENERGY_COST_MUD,
    ENERGY_GAIN_FOOD,
    ACTION_DELTAS,
)


class CellType(IntEnum):
    """Tipurile de celule din grid."""
    EMPTY = 0
    OBSTACLE = 1
    MUD = 2
    FOOD = 3
    DANGER = 4
    TARGET = 5
    START = 6


class Environment:
    """
    Mediul 2D (grid NxM) în care agentul operează.

    Responsabilități:
    - Generare procedurală a hărții (cu seed)
    - Validare topologică (BFS — drum garantat start→țintă)
    - Procesarea acțiunilor agentului și returnarea feedback-ului
    """

    def __init__(self, rows=GRID_ROWS, cols=GRID_COLS, seed=None):
        self.rows = rows
        self.cols = cols
        self.seed = seed

        self.grid = None
        self.start_pos = None
        self.target_pos = None

        self.generate(seed)

    # ------------------------------------------------------------------
    # Generare procedurală
    # ------------------------------------------------------------------

    def generate(self, seed=None):
        """Generează o hartă validă (cu drum garantat start→țintă)."""
        if seed is not None:
            self.seed = seed
        if self.rows + self.cols - 2 < MIN_MANHATTAN_DISTANCE:
            raise ValueError(
                "Gridul este prea mic pentru distanța minimă start→țintă "
                f"({MIN_MANHATTAN_DISTANCE})."
            )

        for attempt in range(1000):
            current_seed = (self.seed or 0) + attempt
            self._build_map(current_seed)
            if self._validate_path():
                return
        raise RuntimeError("Nu s-a putut genera o hartă validă după 1000 încercări.")

    def _build_map(self, seed):
        """Construiește matricea grid cu plasare aleatorie a elementelor."""
        rng = random.Random(seed)

        # Inițializare cu celule goale
        self.grid = [[CellType.EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

        # Plasare start și țintă cu distanță minimă Manhattan
        while True:
            sr, sc = rng.randint(0, self.rows - 1), rng.randint(0, self.cols - 1)
            tr, tc = rng.randint(0, self.rows - 1), rng.randint(0, self.cols - 1)
            manhattan = abs(sr - tr) + abs(sc - tc)
            if manhattan >= MIN_MANHATTAN_DISTANCE:
                break

        self.start_pos = (sr, sc)
        self.target_pos = (tr, tc)
        self.grid[sr][sc] = CellType.START
        self.grid[tr][tc] = CellType.TARGET

        # Lista celulelor disponibile (fără start și țintă)
        available = [
            (r, c) for r in range(self.rows) for c in range(self.cols)
            if (r, c) not in (self.start_pos, self.target_pos)
        ]
        rng.shuffle(available)

        total = len(available)
        idx = 0

        # Plasare obstacole
        n_obstacles = int(total * OBSTACLE_DENSITY)
        for i in range(n_obstacles):
            r, c = available[idx]
            self.grid[r][c] = CellType.OBSTACLE
            idx += 1

        # Plasare zone dificile (mud)
        n_mud = int(total * MUD_DENSITY)
        for i in range(n_mud):
            r, c = available[idx]
            self.grid[r][c] = CellType.MUD
            idx += 1

        # Plasare hrană
        n_food = int(total * FOOD_DENSITY)
        for i in range(n_food):
            r, c = available[idx]
            self.grid[r][c] = CellType.FOOD
            idx += 1

        # Plasare pericole
        n_danger = int(total * DANGER_DENSITY)
        for i in range(n_danger):
            r, c = available[idx]
            self.grid[r][c] = CellType.DANGER
            idx += 1

    # ------------------------------------------------------------------
    # Validare topologică (BFS)
    # ------------------------------------------------------------------

    def _validate_path(self):
        """Verifică dacă există cel puțin un drum valid start→țintă (BFS)."""
        return self.bfs(self.start_pos, self.target_pos) is not None

    def bfs(self, start, goal):
        """
        BFS clasic pe grid. Returnează lungimea drumului minim sau None dacă nu există drum.
        Traversează EMPTY, MUD, FOOD, START, TARGET. NU traversează OBSTACLE sau DANGER.
        """
        if start == goal:
            return 0

        visited = set()
        visited.add(start)
        queue = deque()
        queue.append((start, 0))

        while queue:
            (r, c), dist = queue.popleft()
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in visited:
                    cell = self.grid[nr][nc]
                    if cell not in (CellType.OBSTACLE, CellType.DANGER):
                        if (nr, nc) == goal:
                            return dist + 1
                        visited.add((nr, nc))
                        queue.append(((nr, nc), dist + 1))
        return None

    # ------------------------------------------------------------------
    # Interacțiune cu agentul
    # ------------------------------------------------------------------

    def get_cell(self, row, col):
        """Returnează tipul celulei la coordonatele date."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return CellType.OBSTACLE  # în afara limitelor = perete

    def try_move(self, position, action):
        """
        Procesează o acțiune a agentului.

        Args:
            position: (row, col) poziția curentă
            action: int (0-4) — indexul acțiunii

        Returns:
            dict cu:
                new_pos: (row, col) noua poziție
                energy_cost: int — costul în energie
                energy_gain: int — energia câștigată
                reward: float — recompensa
                is_terminal: bool — episod terminat?
                terminal_reason: str sau None — motivul terminării
        """
        from src.constants import (
            REWARD_STEP, REWARD_FOOD, REWARD_COLLISION,
            REWARD_TARGET, REWARD_DEATH, REWARD_MUD,
            ENERGY_STAY_COST,
        )

        row, col = position
        dr, dc = ACTION_DELTAS[action]
        nr, nc = row + dr, col + dc

        result = {
            "new_pos": position,
            "cell_type": self.get_cell(row, col),
            "energy_cost": ENERGY_COST_NORMAL,
            "energy_gain": 0,
            "reward": REWARD_STEP,
            "is_terminal": False,
            "terminal_reason": None,
        }

        # Acțiunea STAY
        if action == 4:
            result["energy_cost"] = ENERGY_STAY_COST
            return result

        # Verificare limite și obstacole
        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            result["cell_type"] = CellType.OBSTACLE
            result["reward"] = REWARD_COLLISION
            return result

        cell = self.grid[nr][nc]
        result["cell_type"] = cell

        if cell == CellType.OBSTACLE:
            result["reward"] = REWARD_COLLISION
            return result

        # Mișcare validă — actualizare poziție
        result["new_pos"] = (nr, nc)

        if cell == CellType.MUD:
            result["energy_cost"] = ENERGY_COST_MUD
            result["reward"] = REWARD_STEP + REWARD_MUD

        elif cell == CellType.FOOD:
            result["energy_gain"] = ENERGY_GAIN_FOOD
            result["reward"] = REWARD_FOOD
            self.grid[nr][nc] = CellType.EMPTY  # resursa dispare

        elif cell == CellType.DANGER:
            result["reward"] = REWARD_DEATH
            result["is_terminal"] = True
            result["terminal_reason"] = "danger"

        elif cell == CellType.TARGET:
            result["reward"] = REWARD_TARGET
            result["is_terminal"] = True
            result["terminal_reason"] = "target_reached"

        return result

    def reset(self, seed=None):
        """Regenerează harta (opțional cu un seed nou)."""
        self.generate(seed if seed is not None else self.seed)

    def get_food_positions(self):
        """Returnează lista pozițiilor cu hrană existentă."""
        return [
            (r, c)
            for r in range(self.rows) for c in range(self.cols)
            if self.grid[r][c] == CellType.FOOD
        ]
