"""
Agentul autonom: poziție, energie, stare internă.
(Q-Learning va fi adăugat în Pasul 4)
"""

from src.constants import (
    ENERGY_MAX,
    ENERGY_THRESHOLDS,
)


class Agent:
    """
    Agentul autonom care navighează în mediu.

    Stare internă:
    - Poziția curentă (row, col)
    - Nivel de energie E ∈ [0, E_max]

    În acest pas implementăm doar starea internă și mișcarea.
    Q-Learning va fi adăugat ulterior.
    """

    def __init__(self, start_pos, energy=ENERGY_MAX):
        self.start_pos = start_pos
        self.position = start_pos
        self.energy = energy
        self.energy_max = ENERGY_MAX
        self.is_alive = True
        self.reached_target = False

        # Statistici per episod
        self.total_steps = 0
        self.total_reward = 0.0
        self.cells_visited = set()
        self.cells_visited.add(start_pos)

    # ------------------------------------------------------------------
    # Energie
    # ------------------------------------------------------------------

    def get_energy_level(self):
        """Returnează nivelul discretizat de energie (0-3)."""
        ratio = self.energy / self.energy_max
        for i, threshold in enumerate(ENERGY_THRESHOLDS):
            if ratio < threshold:
                return i
        return len(ENERGY_THRESHOLDS)  # nivel maxim (3)

    def consume_energy(self, cost):
        """Consumă energie. Returnează True dacă agentul mai e viu."""
        self.energy = max(0, self.energy - cost)
        if self.energy <= 0:
            self.is_alive = False
        return self.is_alive

    def gain_energy(self, amount):
        """Adaugă energie (limitată la E_max)."""
        self.energy = min(self.energy_max, self.energy + amount)

    # ------------------------------------------------------------------
    # Mișcare
    # ------------------------------------------------------------------

    def apply_action_result(self, result):
        """
        Aplică rezultatul unei acțiuni (returnat de Environment.try_move).

        Args:
            result: dict din Environment.try_move()

        Returns:
            str sau None — motivul terminării episodului
        """
        # Actualizare poziție
        self.position = result["new_pos"]
        self.cells_visited.add(self.position)

        # Actualizare energie
        self.gain_energy(result["energy_gain"])
        alive = self.consume_energy(result["energy_cost"])

        # Actualizare statistici
        self.total_steps += 1
        self.total_reward += result["reward"]

        # Verificare terminare
        if result["is_terminal"]:
            if result["terminal_reason"] == "target_reached":
                self.reached_target = True
            else:
                self.is_alive = False
            return result["terminal_reason"]

        if not alive:
            return "energy_depleted"

        return None

    # ------------------------------------------------------------------
    # Stare
    # ------------------------------------------------------------------

    def get_state(self):
        """Returnează starea curentă: (row, col, energy_level)."""
        r, c = self.position
        return (r, c, self.get_energy_level())

    def reset(self, start_pos=None, energy=None):
        """Resetează agentul la starea inițială."""
        self.position = start_pos if start_pos is not None else self.start_pos
        self.start_pos = self.position
        self.energy = energy if energy is not None else self.energy_max
        self.is_alive = True
        self.reached_target = False
        self.total_steps = 0
        self.total_reward = 0.0
        self.cells_visited = set()
        self.cells_visited.add(self.position)

    @property
    def energy_percent(self):
        """Procentul de energie rămas."""
        return self.energy / self.energy_max

    @property
    def coverage(self):
        """Numărul de celule unice vizitate."""
        return len(self.cells_visited)
