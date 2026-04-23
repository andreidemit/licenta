"""
Simulare practică: Robotul de Depozit (Amazon Kiva-style).

Această clasă implementează un mediu de tip depozit industrial pe un grid 20×20,
mapând direct pe arhitectura Q-Learning existentă.

Corespondențe cu lumea reală:
    OBSTACLE  → Raft de depozitare (nu poate fi traversat)
    MUD       → Intersecție aglomerată / pardoseală degradată (cost energetic dublu)
    FOOD      → Stație de încărcare baterie (energie +20)
    DANGER    → Zonă de operare stivuitor (pericol coliziune)
    TARGET    → Stație de expediere (livrare finalizată)
    START     → Zonă de recepție marfă
    EMPTY     → Culoar navigabil
"""

from src.environment import Environment, CellType
from src.constants import GRID_ROWS, GRID_COLS


# Layout 20×20 al depozitului.
# Simboluri: S=start, T=target, W=obstacle(raft), F=food(statie incarcare),
#            M=mud(zona aglomerata), D=danger(stivuitor), .=empty(culoar)
_WAREHOUSE_LAYOUT = [
    # Col: 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19
    list("S.................."),  # row 0: zona de recepție (start)
    list("..................."),  # row 1: arie de staging recepție
    list("..................."),  # row 2: arie de staging recepție
    list(".WWW.WWW.WWW.WWW.WW."),  # row 3: rafturi (blocare)
    list(".WWW.WWW.WWW.WWW.WW."),  # row 4: rafturi
    list(".WWW.WWW.WWW.WWW.WW."),  # row 5: rafturi
    list("...M...M...M...M...."),  # row 6: culoar transversal (intersecții aglomerate)
    list("F...F...............F"),  # row 7: stații de încărcare
    list("...M...M...M...M...."),  # row 8: culoar transversal
    list(".WWW.WWW.WWW.WWW.WW."),  # row 9: rafturi
    list(".WWW.WWW.WWW.WWW.WW."),  # row 10: rafturi
    list(".WWW.WWW.WWW.WWW.WW."),  # row 11: rafturi
    list("...M...M...M...M...."),  # row 12: culoar transversal
    list("F...F...............F"),  # row 13: stații de încărcare
    list("...M...M...M...M...."),  # row 14: culoar transversal
    list(".WWW.WWW.WWW.WWW.WW."),  # row 15: rafturi
    list(".WWW.WWW.WWW.WWW.WW."),  # row 16: rafturi
    list("D..................D"),  # row 17: zonă stivuitoare (pericol)
    list("..................."),  # row 18: arie de staging expediere
    list("....T.............."),  # row 19: zona de expediere (target col 4)
]

# Mapare simbol → CellType
_SYMBOL_TO_CELL = {
    "S": CellType.START,
    "T": CellType.TARGET,
    "W": CellType.OBSTACLE,
    "F": CellType.FOOD,
    "M": CellType.MUD,
    "D": CellType.DANGER,
    ".": CellType.EMPTY,
}

# Descrieri zona pentru afișaj și teză
ZONE_DESCRIPTIONS = {
    "receiving": "Zona de recepție marfă (rândul 0-2)",
    "storage_a": "Bloc depozitare A — rafturi 1-4 (rândurile 3-5)",
    "cross_aisle_1": "Culoar transversal 1 (rândurile 6-8) — stații de încărcare la col. 0, 4, 19",
    "storage_b": "Bloc depozitare B — rafturi 1-4 (rândurile 9-11)",
    "cross_aisle_2": "Culoar transversal 2 (rândurile 12-14) — stații de încărcare la col. 0, 4, 19",
    "storage_c": "Bloc depozitare C — rafturi 1-4 (rândurile 15-16)",
    "forklift_zone": "Zonă operare stivuitor (rândul 17) — PERICOL la col. 0 și 19",
    "dispatch": "Zona de expediere (rândurile 18-19) — target la (19, 4)",
}


class WarehouseEnvironment(Environment):
    """
    Mediu de tip depozit industrial, derivat din Environment.

    Override-ul metodei generate() înlocuiește generarea procedurală
    cu un layout fix, realist, al unui depozit cu:
    - 4 culoare verticale (coloane 0, 4, 8, 12, 16, 19)
    - 3 blocuri de rafturi (fiecare 3 rânduri × 4 grupe de 3 coloane)
    - 2 culoare transversale cu stații de încărcare
    - Zonă stivuitoare periculoasă la intrarea în expediere
    - BFS-validat: distanță optimă start→target = 23 pași
    """

    def __init__(self, rows=20, cols=20):
        if rows != 20 or cols != 20:
            raise ValueError("WarehouseEnvironment necesită grid 20×20 fix.")
        super().__init__(rows=rows, cols=cols, seed=None)

    def generate(self, seed=None):
        """
        Construiește harta fixă a depozitului (ignoră seed-ul).
        Validează topologic cu BFS înainte de returnare.
        """
        self._build_warehouse_map()
        if not self._validate_path():
            raise RuntimeError(
                "Harta depozitului este invalidă (fără drum start→target). "
                "Verificați _WAREHOUSE_LAYOUT."
            )

    def _build_warehouse_map(self):
        """Construiește grid-ul din _WAREHOUSE_LAYOUT."""
        self.grid = [[CellType.EMPTY] * self.cols for _ in range(self.rows)]
        self.start_pos = None
        self.target_pos = None

        for row_idx, row_symbols in enumerate(_WAREHOUSE_LAYOUT):
            for col_idx, symbol in enumerate(row_symbols):
                if col_idx >= self.cols:
                    break
                cell = _SYMBOL_TO_CELL.get(symbol, CellType.EMPTY)
                self.grid[row_idx][col_idx] = cell
                if symbol == "S":
                    self.start_pos = (row_idx, col_idx)
                elif symbol == "T":
                    self.target_pos = (row_idx, col_idx)

    def reset(self, seed=None):
        """Resetează la harta fixă (ignoră seed — layout constant)."""
        self._build_warehouse_map()

    def get_warehouse_stats(self) -> dict:
        """Returnează statistici despre layout-ul depozitului."""
        counts = {ct: 0 for ct in CellType}
        for row in self.grid:
            for cell in row:
                counts[cell] += 1
        bfs_optimal = self.bfs(self.start_pos, self.target_pos)
        return {
            "total_cells": self.rows * self.cols,
            "shelves": counts[CellType.OBSTACLE],
            "aisles_empty": counts[CellType.EMPTY],
            "charging_stations": counts[CellType.FOOD],
            "mud_zones": counts[CellType.MUD],
            "danger_zones": counts[CellType.DANGER],
            "bfs_optimal_path": bfs_optimal,
            "start": self.start_pos,
            "target": self.target_pos,
        }


def print_warehouse_map(env: WarehouseEnvironment) -> None:
    """Afișează harta depozitului în consolă cu legendă."""
    symbols = {
        CellType.EMPTY: "·",
        CellType.OBSTACLE: "█",
        CellType.MUD: "≈",
        CellType.FOOD: "⚡",
        CellType.DANGER: "✖",
        CellType.TARGET: "★",
        CellType.START: "◉",
    }
    print("\n┌" + "─" * (env.cols * 2 + 1) + "┐")
    for row_idx, row in enumerate(env.grid):
        print(f"│ ", end="")
        for cell in row:
            print(symbols.get(cell, "?"), end=" ")
        print(f"│ r{row_idx:02d}")
    print("└" + "─" * (env.cols * 2 + 1) + "┘")
    print("Legendă: ◉=Start  ★=Target  █=Raft  ⚡=Încărcare  ≈=Zonă aglomerată  ✖=Pericol  ·=Culoar")


def run_warehouse_training(num_episodes=2000, visualize=False):
    """
    Rulează antrenamentul Q-Learning pe scenariul de depozit.

    Returns:
        (list[EpisodeResult], QLearning) — istoricul și Q-learner-ul antrenat
    """
    from src.q_learning import QLearning
    from src.trainer import Trainer
    from src.analytics import Analytics
    from src.constants import ENERGY_MAX

    env = WarehouseEnvironment()
    stats = env.get_warehouse_stats()

    print("=" * 60)
    print("SIMULARE DEPOZIT INDUSTRIAL — Q-Learning Robot")
    print("=" * 60)
    print(f"Start: {stats['start']}  →  Target: {stats['target']}")
    print(f"Rafturi: {stats['shelves']} celule  |  Culoare: {stats['aisles_empty']} celule")
    print(f"Stații încărcare: {stats['charging_stations']}  |  Zone pericol: {stats['danger_zones']}")
    print(f"Distanță BFS optimă: {stats['bfs_optimal_path']} pași")
    print()
    print_warehouse_map(env)
    print()

    q = QLearning(rows=20, cols=20)
    trainer = Trainer(env, q, energy=ENERGY_MAX)

    renderer = None
    render_cb = None

    if visualize:
        import pygame
        import sys
        from src.renderer import Renderer

        renderer = Renderer(rows=20, cols=20)

        def render_cb(env, agent, info):
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_q
                ):
                    renderer.close()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        renderer.show_heatmap = not renderer.show_heatmap
                    elif event.key == pygame.K_p:
                        renderer.show_policy = not renderer.show_policy
            renderer.draw(env, agent, info, q_learner=q)

    history = trainer.train(
        num_episodes=num_episodes,
        print_every=max(1, num_episodes // 10),
        render_callback=render_cb,
    )

    # Evaluare greedy finală
    print()
    print("=== Evaluare Greedy — Robot de Depozit ===")
    agent, outcome = trainer.run_greedy_episode()
    print(f"Rezultat: {outcome}")
    print(f"Pași: {agent.total_steps}  (optim BFS: {stats['bfs_optimal_path']})")
    print(f"Reward: {agent.total_reward:.1f}  |  Energie rămasă: {agent.energy:.0f}")
    overhead = agent.total_steps - stats['bfs_optimal_path']
    print(f"Overhead față de optim: +{overhead} pași ({overhead / stats['bfs_optimal_path'] * 100:.1f}%)")

    # Export analytics
    analytics = Analytics(scenario="WAREHOUSE", grid_size=20, seed=0)
    csv_path = analytics.export_csv(history)
    plot_paths = analytics.save_all_plots(history)
    q.save("data/qtable_WAREHOUSE_20_0.npy")

    print(f"\nCSV: {csv_path}")
    for p in plot_paths:
        print(f"Grafic: {p}")
    print("Q-Table salvată: data/qtable_WAREHOUSE_20_0.npy")

    if renderer:
        # Replay greedy vizual
        print("\n[Replay greedy vizual — apasă Q pentru ieșire]")
        env.reset()
        from src.agent import Agent
        agent2 = Agent(start_pos=env.start_pos, energy=ENERGY_MAX)
        state = agent2.get_state()
        running = True
        while running:
            import pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_q
                ):
                    running = False
                    break
            if not running:
                break
            if agent2.is_alive and not agent2.reached_target:
                action = q.get_best_action(state)
                result = env.try_move(agent2.position, action)
                agent2.apply_action_result(result)
                state = agent2.get_state()
            renderer.draw(env, agent2, {"Mod": "Replay Greedy Depozit"}, q_learner=q)
        renderer.close()

    return history, q


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Simulare Robot de Depozit")
    parser.add_argument("--episodes", type=int, default=2000)
    parser.add_argument("--visualize", action="store_true")
    args = parser.parse_args()
    run_warehouse_training(num_episodes=args.episodes, visualize=args.visualize)
