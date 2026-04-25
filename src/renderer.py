"""
Renderer Pygame: vizualizare grid, agent, energie și informații.
"""

import pygame

import numpy as np

from src.constants import (
    CELL_SIZE, SIDEBAR_WIDTH, FPS,
    COLOR_EMPTY, COLOR_OBSTACLE, COLOR_MUD, COLOR_FOOD, COLOR_DANGER,
    COLOR_TARGET, COLOR_AGENT, COLOR_START,
    COLOR_BACKGROUND, COLOR_GRID_LINE, COLOR_TEXT,
    COLOR_ENERGY_BAR, COLOR_ENERGY_LOW,
    GRID_ROWS, GRID_COLS, ACTION_DELTAS, ACTIONS,
)
from src.environment import CellType


# Mapare CellType → culoare
CELL_COLORS = {
    CellType.EMPTY: COLOR_EMPTY,
    CellType.OBSTACLE: COLOR_OBSTACLE,
    CellType.MUD: COLOR_MUD,
    CellType.FOOD: COLOR_FOOD,
    CellType.DANGER: COLOR_DANGER,
    CellType.TARGET: COLOR_TARGET,
    CellType.START: COLOR_START,
}


class Renderer:
    """
    Randare Pygame a simulării.
    """

    def __init__(self, rows=GRID_ROWS, cols=GRID_COLS):
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.window_width = cols * CELL_SIZE + SIDEBAR_WIDTH
        self.window_height = max(rows * CELL_SIZE, 400)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Q-Learning: Navigare Autonomă")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 14)
        self.font_tiny = pygame.font.SysFont("monospace", 12)
        self.font_xl = pygame.font.SysFont("monospace", 36, bold=True)

        # Toggle overlay-uri
        self.show_heatmap = False
        self.show_policy = False
        self.show_visits = False
        self.show_td = False
        self.show_knowledge_mask = False
        self.show_trail = True
        self.policy_energy_level = None

        # Efecte tranzitorii pentru feedback vizual per pas
        self._active_effects = []
        self._last_feedback_signature = None

        # Trail-ul agentului în episodul curent
        self._trail_max = 40
        self._trail = []
        self._last_episode_id = None

    def cycle_policy_level(self):
        """Comută între bucket-ul curent și bucket-urile fixe 0..3."""
        if self.policy_energy_level is None:
            self.policy_energy_level = 0
        elif self.policy_energy_level >= 3:
            self.policy_energy_level = None
        else:
            self.policy_energy_level += 1

    def toggle_visits(self):
        self.show_visits = not self.show_visits

    def toggle_td(self):
        self.show_td = not self.show_td

    def toggle_knowledge_mask(self):
        self.show_knowledge_mask = not self.show_knowledge_mask

    def toggle_trail(self):
        self.show_trail = not self.show_trail

    def reset_visual_state(self):
        """Curăță efectele tranzitorii între episoade sau reset-uri manuale."""
        self._active_effects = []
        self._last_feedback_signature = None
        self._trail = []

    def _get_overlay_energy_level(self, agent):
        """Returnează bucket-ul de energie folosit pentru overlay-uri."""
        if self.policy_energy_level is None:
            return agent.get_energy_level()
        return self.policy_energy_level

    def _overlay_level_label(self, agent):
        """Etichetă scurtă pentru modul overlay curent."""
        if self.policy_energy_level is None:
            return f"curent ({agent.get_energy_level()})"
        return f"fix ({self.policy_energy_level})"

    def _push_cell_flash(self, row, col, color, ttl=16):
        self._active_effects.append({
            "kind": "flash",
            "row": row,
            "col": col,
            "color": color,
            "ttl": ttl,
            "max_ttl": ttl,
        })

    def _push_floating_text(self, row, col, text, color, ttl=24):
        self._active_effects.append({
            "kind": "text",
            "row": row,
            "col": col,
            "text": text,
            "color": color,
            "ttl": ttl,
            "max_ttl": ttl,
        })

    def _queue_feedback_effects(self, agent, info):
        """Generează efecte vizuale scurte pentru ultimul pas al agentului."""
        if not info or "_feedback" not in info:
            return

        feedback = info["_feedback"]
        signature = (
            agent.total_steps,
            feedback.get("action"),
            feedback.get("reward"),
            feedback.get("energy_cost"),
            feedback.get("energy_gain"),
            feedback.get("new_pos"),
            feedback.get("terminal_reason"),
        )
        if signature == self._last_feedback_signature:
            return

        self._last_feedback_signature = signature
        row, col = feedback.get("new_pos", agent.position)
        reward = feedback.get("reward", 0)
        terminal_reason = feedback.get("terminal_reason")

        # Pulse de învățare: flash subtil pe celula unde s-a actualizat Q-ul.
        learning = info.get("_learning") if info else None
        if learning and learning.get("last_update") is not None:
            lr_row, lr_col, _, _, td = learning["last_update"]
            magnitude = min(1.0, abs(td) / 20.0)
            if magnitude > 0.02:
                # Albastru pentru TD pozitiv (valoare în creștere), violet pentru negativ
                color = (80, 140, 255) if td >= 0 else (180, 80, 220)
                self._push_cell_flash(lr_row, lr_col, color, ttl=8 + int(magnitude * 12))

        if feedback.get("is_collision"):
            self._push_cell_flash(row, col, (255, 80, 80))
            self._push_floating_text(row, col, f"{reward:.0f}", (255, 120, 120))
            return

        if terminal_reason == "target_reached":
            self._push_cell_flash(row, col, (60, 220, 255), ttl=28)
            self._push_floating_text(row, col, f"+{reward:.0f}", (150, 240, 255), ttl=30)
            return

        if terminal_reason == "danger":
            self._push_cell_flash(row, col, (255, 40, 60), ttl=28)
            self._push_floating_text(row, col, f"{reward:.0f}", (255, 140, 140), ttl=30)
            return

        if feedback.get("energy_gain", 0) > 0:
            self._push_cell_flash(row, col, (255, 215, 0))
            self._push_floating_text(row, col, f"+{reward:.0f}", (255, 240, 160))
            return

        if feedback.get("energy_cost", 0) > 1:
            self._push_cell_flash(row, col, (160, 110, 70))
            self._push_floating_text(row, col, f"{reward:.0f}", (230, 200, 170))

    def _draw_active_effects(self):
        """Randează flash-uri de celulă și texte plutitoare."""
        next_effects = []
        for effect in self._active_effects:
            ratio = effect["ttl"] / effect["max_ttl"]
            row = effect["row"]
            col = effect["col"]
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            if effect["kind"] == "flash":
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                alpha = max(0, min(180, int(190 * ratio)))
                surf.fill((*effect["color"], alpha))
                self.screen.blit(surf, (x, y))
            elif effect["kind"] == "text":
                text = self.font_small.render(effect["text"], True, effect["color"])
                offset = int((1 - ratio) * 18)
                text_rect = text.get_rect(center=(
                    x + CELL_SIZE // 2,
                    y + CELL_SIZE // 2 - 8 - offset,
                ))
                self.screen.blit(text, text_rect)

            effect["ttl"] -= 1
            if effect["ttl"] > 0:
                next_effects.append(effect)

        self._active_effects = next_effects

    def draw(self, environment, agent, info=None, q_learner=None):
        """
        Randează un frame complet: grid + agent + sidebar.

        Args:
            environment: instanța Environment
            agent: instanța Agent
            info: dict opțional cu informații extra (episod, epsilon etc.)
            q_learner: instanța QLearning, necesară pentru overlay-uri heatmap/policy
        """
        self._queue_feedback_effects(agent, info)
        self._update_trail(agent, info)
        overlay_energy_level = self._get_overlay_energy_level(agent)

        self.screen.fill(COLOR_BACKGROUND)
        self._draw_grid(environment)
        if self.show_knowledge_mask and q_learner is not None:
            self._draw_knowledge_mask(environment, q_learner)
        if self.show_visits and q_learner is not None:
            self._draw_visit_heatmap(environment, q_learner)
        if self.show_td and q_learner is not None:
            self._draw_td_heatmap(environment, q_learner)
        if self.show_heatmap and q_learner is not None:
            self._draw_heatmap(environment, q_learner, overlay_energy_level)
        if self.show_policy and q_learner is not None:
            self._draw_policy_arrows(environment, q_learner, overlay_energy_level)
        if self.show_trail:
            self._draw_trail()
        self._draw_active_effects()
        self._draw_agent(agent)
        self._draw_sidebar(agent, environment, info, q_learner=q_learner)
        pygame.display.flip()
        self.clock.tick(FPS)

    def _draw_grid(self, environment):
        """Desenează celulele gridului."""
        for row in range(environment.rows):
            for col in range(environment.cols):
                cell = environment.grid[row][col]
                color = CELL_COLORS.get(cell, COLOR_EMPTY)
                rect = pygame.Rect(
                    col * CELL_SIZE, row * CELL_SIZE,
                    CELL_SIZE, CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

        # Marchează ținta cu un simbol distinct
        if environment.target_pos:
            tr, tc = environment.target_pos
            cx = tc * CELL_SIZE + CELL_SIZE // 2
            cy = tr * CELL_SIZE + CELL_SIZE // 2
            # Stea simplă (cerc + text)
            pygame.draw.circle(self.screen, COLOR_TARGET, (cx, cy), CELL_SIZE // 3)
            star = self.font_large.render("★", True, (255, 255, 255))
            star_rect = star.get_rect(center=(cx, cy))
            self.screen.blit(star, star_rect)

    def _draw_heatmap(self, environment, q_learner, energy_level):
        """Suprapune heatmap-ul valorilor Q maxime pe grid (semi-transparent)."""
        # Colectează toate valorile max-Q pentru normalizare globală
        q_max_values = []
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] != CellType.OBSTACLE:
                    q_max_values.append(float(np.max(q_learner.q_table[row, col, energy_level, :])))

        if not q_max_values:
            return

        global_min = min(q_max_values)
        global_max = max(q_max_values)
        value_range = global_max - global_min + 1e-9

        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] == CellType.OBSTACLE:
                    continue
                max_q = float(np.max(q_learner.q_table[row, col, energy_level, :]))
                t = (max_q - global_min) / value_range

                # Interpolare culoare: t=0 → roșu (180,0,0), t=1 → verde (0,200,80)
                r_ch = int(180 * (1 - t))
                g_ch = int(200 * t)
                b_ch = int(80 * t)

                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                surf.fill((r_ch, g_ch, b_ch, 160))
                self.screen.blit(surf, (col * CELL_SIZE, row * CELL_SIZE))

    def _draw_policy_arrows(self, environment, q_learner, energy_level):
        """Desenează săgeți pentru acțiunea optimă în fiecare celulă vizitată."""
        for row in range(environment.rows):
            for col in range(environment.cols):
                cell = environment.grid[row][col]
                if cell == CellType.OBSTACLE:
                    continue

                q_slice = q_learner.q_table[row, col, energy_level, :]
                if np.max(q_slice) == 0.0:
                    continue  # celulă nevizitată, fără săgeată

                best_action = int(np.argmax(q_slice))
                cx = col * CELL_SIZE + CELL_SIZE // 2
                cy = row * CELL_SIZE + CELL_SIZE // 2

                if best_action == 4:  # STAY — punct central
                    pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), 3)
                else:
                    dy, dx = ACTION_DELTAS[best_action]
                    tip = (cx + dx * CELL_SIZE // 3, cy + dy * CELL_SIZE // 3)
                    tail = (cx - dx * CELL_SIZE // 4, cy - dy * CELL_SIZE // 4)
                    pygame.draw.line(self.screen, (255, 255, 255), tail, tip, 2)
                    # Vârful săgeții (triunghi mic)
                    perp = (-dy, dx)
                    head1 = (tip[0] - dx * 5 + perp[0] * 4, tip[1] - dy * 5 + perp[1] * 4)
                    head2 = (tip[0] - dx * 5 - perp[0] * 4, tip[1] - dy * 5 - perp[1] * 4)
                    pygame.draw.polygon(self.screen, (255, 255, 255), [tip, head1, head2])

    # ------------------------------------------------------------------
    # Overlay-uri pentru evoluția învățării
    # ------------------------------------------------------------------

    def _update_trail(self, agent, info):
        """Actualizează coada de poziții recente. Resetează la episod nou."""
        episode_id = info.get("Episod") if info else None
        feedback = info.get("_feedback") if info else None
        if episode_id is not None and episode_id != self._last_episode_id:
            self._trail = []
            self._last_episode_id = episode_id

        pos = agent.position
        if not self._trail or self._trail[-1] != pos:
            self._trail.append(pos)
            if len(self._trail) > self._trail_max:
                self._trail = self._trail[-self._trail_max:]

        if feedback and feedback.get("terminal_reason"):
            # Lăsăm trail-ul vizibil până la următorul episod
            pass

    def _draw_trail(self):
        """Desenează urma agentului în episodul curent (fade către prezent)."""
        if len(self._trail) < 2:
            return
        n = len(self._trail)
        for i in range(n - 1):
            ratio = (i + 1) / n
            alpha = max(20, int(180 * ratio))
            (r1, c1), (r2, c2) = self._trail[i], self._trail[i + 1]
            x1 = c1 * CELL_SIZE + CELL_SIZE // 2
            y1 = r1 * CELL_SIZE + CELL_SIZE // 2
            x2 = c2 * CELL_SIZE + CELL_SIZE // 2
            y2 = r2 * CELL_SIZE + CELL_SIZE // 2
            surf = pygame.Surface((self.cols * CELL_SIZE, self.rows * CELL_SIZE), pygame.SRCALPHA)
            pygame.draw.line(surf, (255, 255, 255, alpha), (x1, y1), (x2, y2), 2)
            self.screen.blit(surf, (0, 0))

    def _draw_visit_heatmap(self, environment, q_learner):
        """Heatmap log-scale al numărului de vizite per celulă (gradient albastru)."""
        visits = q_learner.get_visit_counts()
        if visits.max() == 0:
            return
        log_visits = np.log1p(visits)
        vmax = log_visits.max()
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] == CellType.OBSTACLE:
                    continue
                t = log_visits[row, col] / vmax if vmax > 0 else 0
                if t <= 0.001:
                    continue
                alpha = int(40 + 140 * t)
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                surf.fill((40, 110, 220, alpha))
                self.screen.blit(surf, (col * CELL_SIZE, row * CELL_SIZE))

    def _draw_td_heatmap(self, environment, q_learner):
        """Heatmap al magnitudinii TD-error decăzute (gradient galben/roșu)."""
        td_map = q_learner.get_td_error_map()
        vmax = float(td_map.max())
        if vmax <= 1e-6:
            return
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] == CellType.OBSTACLE:
                    continue
                t = td_map[row, col] / vmax
                if t <= 0.01:
                    continue
                # Galben (puține) → roșu intens (multă învățare)
                r_ch = 255
                g_ch = int(220 * (1 - t))
                b_ch = 30
                alpha = int(60 + 150 * t)
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                surf.fill((r_ch, g_ch, b_ch, alpha))
                self.screen.blit(surf, (col * CELL_SIZE, row * CELL_SIZE))

    def _draw_knowledge_mask(self, environment, q_learner):
        """Întunecă celulele nevizitate — frontiera cunoașterii."""
        visits = q_learner.get_visit_counts()
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] == CellType.OBSTACLE:
                    continue
                if visits[row, col] == 0:
                    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    surf.fill((0, 0, 0, 160))
                    self.screen.blit(surf, (col * CELL_SIZE, row * CELL_SIZE))

    def _draw_agent(self, agent):
        """Desenează agentul ca un cerc pe grid."""
        row, col = agent.position
        cx = col * CELL_SIZE + CELL_SIZE // 2
        cy = row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3

        # Culoare bazată pe energie
        if agent.energy_percent > 0.5:
            color = COLOR_AGENT
        elif agent.energy_percent > 0.25:
            color = (255, 200, 50)  # galben
        else:
            color = COLOR_ENERGY_LOW

        pygame.draw.circle(self.screen, color, (cx, cy), radius)
        # Contur negru
        pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), radius, 2)

    def _draw_sparkline(self, x, y, values, color, label, width=None, height=28):
        """Desenează un sparkline compact și returnează y-ul după el."""
        if width is None:
            width = SIDEBAR_WIDTH - 30
        if not values:
            return y
        if label:
            surf = self.font_tiny.render(label, True, (170, 170, 170))
            self.screen.blit(surf, (x, y))
            y += 14
        rect_bg = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (45, 45, 45), rect_bg)
        pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect_bg, 1)
        vmin = min(values)
        vmax = max(values)
        span = vmax - vmin if vmax > vmin else 1.0
        n = len(values)
        if n == 1:
            return y + height + 2
        points = []
        for i, v in enumerate(values):
            px = x + int(i * (width - 1) / (n - 1))
            py = y + height - 1 - int((v - vmin) / span * (height - 2))
            points.append((px, py))
        if len(points) >= 2:
            pygame.draw.lines(self.screen, color, False, points, 1)
        # Linia 0 dacă e în range
        if vmin <= 0 <= vmax:
            zy = y + height - 1 - int((0 - vmin) / span * (height - 2))
            pygame.draw.line(self.screen, (90, 90, 90), (x, zy), (x + width - 1, zy), 1)
        return y + height + 2

    def _draw_sidebar(self, agent, environment, info, q_learner=None):
        """Desenează panoul lateral cu informații."""
        x_start = self.cols * CELL_SIZE + 10
        y = 15

        # Titlu
        title = self.font_large.render("SIMULARE Q-LEARNING", True, COLOR_TEXT)
        self.screen.blit(title, (x_start, y))
        y += 30

        # Separator
        pygame.draw.line(
            self.screen, COLOR_GRID_LINE,
            (x_start, y), (x_start + SIDEBAR_WIDTH - 20, y)
        )
        y += 15

        # Energie
        energy_label = self.font_small.render(
            f"Energie: {agent.energy:.0f}/{agent.energy_max}", True, COLOR_TEXT
        )
        self.screen.blit(energy_label, (x_start, y))
        y += 20

        # Bară energie
        bar_width = SIDEBAR_WIDTH - 30
        bar_height = 16
        bar_bg = pygame.Rect(x_start, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (50, 50, 50), bar_bg)
        fill_width = int(bar_width * agent.energy_percent)
        bar_color = COLOR_ENERGY_BAR if agent.energy_percent > 0.25 else COLOR_ENERGY_LOW
        bar_fill = pygame.Rect(x_start, y, fill_width, bar_height)
        pygame.draw.rect(self.screen, bar_color, bar_fill)
        pygame.draw.rect(self.screen, COLOR_GRID_LINE, bar_bg, 1)
        y += 30

        # Poziție
        pos_text = self.font_small.render(
            f"Pozitie: ({agent.position[0]}, {agent.position[1]})", True, COLOR_TEXT
        )
        self.screen.blit(pos_text, (x_start, y))
        y += 22

        # Nivel energie discrete
        level_text = self.font_small.render(
            f"Nivel energie: {agent.get_energy_level()}/3", True, COLOR_TEXT
        )
        self.screen.blit(level_text, (x_start, y))
        y += 22

        # Pași / Reward
        steps_text = self.font_small.render(
            f"Pasi: {agent.total_steps}", True, COLOR_TEXT
        )
        self.screen.blit(steps_text, (x_start, y))
        y += 22

        reward_text = self.font_small.render(
            f"Reward: {agent.total_reward:.1f}", True, COLOR_TEXT
        )
        self.screen.blit(reward_text, (x_start, y))
        y += 22

        coverage_text = self.font_small.render(
            f"Celule vizitate: {agent.coverage}", True, COLOR_TEXT
        )
        self.screen.blit(coverage_text, (x_start, y))
        y += 30

        overlay_text = self.font_small.render(
            f"Policy nivel: {self._overlay_level_label(agent)}", True, COLOR_TEXT
        )
        self.screen.blit(overlay_text, (x_start, y))
        y += 22

        # --- Cunoaștere (instrumentare Q-Learning) ---
        if q_learner is not None:
            stats = q_learner.get_knowledge_stats()
            pygame.draw.line(
                self.screen, COLOR_GRID_LINE,
                (x_start, y), (x_start + SIDEBAR_WIDTH - 20, y)
            )
            y += 10
            header = self.font_small.render("CUNOASTERE", True, (180, 200, 255))
            self.screen.blit(header, (x_start, y))
            y += 20
            lines = [
                f"Q nenule: {stats['nonzero']}/{stats['total']} ({stats['fill_pct']:.1f}%)",
                f"Celule expl.: {stats['visited_cells']}/{stats['total_cells']} ({stats['coverage_pct']:.1f}%)",
                f"Mean |Q|: {stats['mean_abs_q']:.2f}",
                f"Mean |TD| 200: {stats['mean_recent_td']:.2f}",
            ]
            for line in lines:
                surf = self.font_tiny.render(line, True, COLOR_TEXT)
                self.screen.blit(surf, (x_start, y))
                y += 16

            # Sparkline reward rolling (din history)
            history = info.get("_learning", {}).get("history", []) if info else []
            if len(history) >= 2:
                y = self._draw_sparkline(
                    x_start, y + 4,
                    values=[ep.total_reward for ep in history[-150:]],
                    color=(100, 220, 120),
                    label="Reward / episod",
                )
            y += 6

        # Informații adiționale
        if info:
            pygame.draw.line(
                self.screen, COLOR_GRID_LINE,
                (x_start, y), (x_start + SIDEBAR_WIDTH - 20, y)
            )
            y += 15
            for key, value in info.items():
                if key.startswith("_") or value in (None, ""):
                    continue
                if key == "Actiune" and isinstance(value, int):
                    value = ACTIONS.get(value, value)
                line = self.font_small.render(f"{key}: {value}", True, COLOR_TEXT)
                self.screen.blit(line, (x_start, y))
                y += 20

        # Stare agent
        y = self.window_height - 80
        pygame.draw.line(
            self.screen, COLOR_GRID_LINE,
            (x_start, y), (x_start + SIDEBAR_WIDTH - 20, y)
        )
        y += 10

        if not agent.is_alive:
            status = self.font_large.render("DECEDAT", True, COLOR_ENERGY_LOW)
        elif agent.reached_target:
            status = self.font_large.render("VICTORIE!", True, (50, 255, 50))
        else:
            status = self.font_large.render("IN VIATA", True, COLOR_ENERGY_BAR)
        self.screen.blit(status, (x_start, y))
        y += 25

        # Scurtături tastatură
        shortcuts = [
            "[H] Heatmap   [P] Policy",
            "[V] Vizite    [T] TD-err",
            "[K] Mask      [L] Trail",
            "[E] Nivel     [R] Reset  [Q] Quit",
        ]
        for line in shortcuts:
            surf = self.font_tiny.render(line, True, (150, 150, 150))
            self.screen.blit(surf, (x_start, y))
            y += 18

    def draw_episode_end_overlay(self, outcome: str) -> None:
        """
        Afișează un overlay semi-transparent cu rezultatul episodului.

        Args:
            outcome: str — 'target_reached', 'energy_depleted', 'danger', 'timeout'
        """
        grid_w = self.cols * CELL_SIZE
        grid_h = self.rows * CELL_SIZE

        # Fundal semi-transparent negru peste grid
        overlay = pygame.Surface((grid_w, grid_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        self.screen.blit(overlay, (0, 0))

        # Text și culoare în funcție de outcome
        if outcome == "target_reached":
            label = "SUCCESS"
            color = (50, 255, 80)
        elif outcome in ("energy_depleted", "danger"):
            label = "DEATH"
            color = (255, 60, 60)
        else:
            label = "TIMEOUT"
            color = (255, 210, 50)

        text_surf = self.font_xl.render(label, True, color)
        text_rect = text_surf.get_rect(center=(grid_w // 2, grid_h // 2))
        self.screen.blit(text_surf, text_rect)
        pygame.display.flip()

    def close(self):
        """Închide fereastra Pygame."""
        pygame.quit()
