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

DASHBOARD_PANEL = (36, 39, 48)
DASHBOARD_PANEL_ALT = (44, 48, 58)
DASHBOARD_ACCENT = (92, 170, 255)
DASHBOARD_MUTED = (155, 163, 178)
DASHBOARD_SUCCESS = (86, 222, 151)
DASHBOARD_WARNING = (255, 205, 86)
DASHBOARD_DANGER = (255, 101, 117)


class Renderer:
    """
    Randare Pygame a simulării.
    """

    def __init__(self, rows=GRID_ROWS, cols=GRID_COLS, human_paced=False):
        pygame.init()
        self.rows = rows
        self.cols = cols
        self.window_width = cols * CELL_SIZE + SIDEBAR_WIDTH
        self.window_height = max(rows * CELL_SIZE, 700)
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Q-Learning: Navigare Autonomă")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("arial", 22, bold=True)
        self.font_metric = pygame.font.SysFont("arial", 20, bold=True)
        self.font_label = pygame.font.SysFont("arial", 12)
        self.font_large = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 14)
        self.font_tiny = pygame.font.SysFont("monospace", 12)
        self.font_xl = pygame.font.SysFont("monospace", 36, bold=True)

        # Playback pentru vizualizare umană în training/replay.
        self.human_paced = human_paced
        self.speed_levels = [1, 2, 4, 8, 15, 30, 60]
        self.speed_index = 2 if human_paced else len(self.speed_levels) - 1
        self.paused = False
        self._step_requested = False

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

    @property
    def target_fps(self):
        return self.speed_levels[self.speed_index]

    def _speed_label(self):
        return f"{self.target_fps} pas/s"

    def _playback_status(self):
        if self.paused:
            return "PAUZA"
        return f"PLAY {self._speed_label()}"

    def handle_playback_event(self, event):
        """Taste pentru ritmul vizualizării: pauză, step, mai lent/rapid."""
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_SPACE:
            self.paused = not self.paused
        elif event.key == pygame.K_PERIOD:
            self._step_requested = True
            self.paused = True
        elif event.key in (pygame.K_MINUS, getattr(pygame, "K_LEFTBRACKET", pygame.K_MINUS)):
            self.speed_index = max(0, self.speed_index - 1)
        elif event.key in (
            pygame.K_EQUALS,
            getattr(pygame, "K_PLUS", pygame.K_EQUALS),
            getattr(pygame, "K_RIGHTBRACKET", pygame.K_EQUALS),
        ):
            self.speed_index = min(len(self.speed_levels) - 1, self.speed_index + 1)
        else:
            return False
        return True

    def handle_ui_event(self, event):
        """Procesează controalele UI comune pentru training/replay."""
        return self.handle_playback_event(event) or self.handle_overlay_event(event)

    def handle_overlay_event(self, event):
        """Procesează tastele comune pentru overlay-uri. Returnează True dacă a gestionat event-ul."""
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_h:
            self.show_heatmap = not self.show_heatmap
        elif event.key == pygame.K_p:
            self.show_policy = not self.show_policy
        elif event.key == pygame.K_e:
            self.cycle_policy_level()
        elif event.key == pygame.K_v:
            self.toggle_visits()
        elif event.key == pygame.K_t:
            self.toggle_td()
        elif event.key == pygame.K_k:
            self.toggle_knowledge_mask()
        elif event.key == pygame.K_l:
            self.toggle_trail()
        else:
            return False
        return True

    def wait_for_playback(self, environment, agent, info=None, q_learner=None):
        """
        Blochează avansarea simulării cât timp vizualizarea este în pauză.

        Returns:
            bool — False dacă utilizatorul a cerut închiderea ferestrei.
        """
        if not self.paused:
            return True

        while self.paused and not self._step_requested:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_q
                ):
                    return False
                self.handle_ui_event(event)
            self.draw(environment, agent, info, q_learner=q_learner)

        if self._step_requested:
            self._step_requested = False
            return True
        return True

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

    def _reward_color(self, reward):
        """Culoare semantică pentru feedback-ul de recompensă."""
        if reward > 0:
            return (80, 230, 120)
        if reward <= -50:
            return (255, 60, 70)
        if reward < 0:
            return (255, 190, 80)
        return COLOR_TEXT

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

    def _push_action_arrow(self, previous_pos, new_pos, color, ttl=18):
        if previous_pos == new_pos:
            return
        self._active_effects.append({
            "kind": "arrow",
            "previous_pos": previous_pos,
            "new_pos": new_pos,
            "color": color,
            "ttl": ttl,
            "max_ttl": ttl,
        })

    def _push_collision_cross(self, row, col, color, ttl=18):
        self._active_effects.append({
            "kind": "cross",
            "row": row,
            "col": col,
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
            feedback.get("energy_delta"),
            feedback.get("previous_pos"),
            feedback.get("new_pos"),
            feedback.get("terminal_reason"),
        )
        if signature == self._last_feedback_signature:
            return

        self._last_feedback_signature = signature
        row, col = feedback.get("new_pos", agent.position)
        reward = feedback.get("reward", 0)
        terminal_reason = feedback.get("terminal_reason")
        previous_pos = feedback.get("previous_pos")
        reward_color = self._reward_color(reward)

        if previous_pos is not None and not feedback.get("is_collision"):
            self._push_action_arrow(previous_pos, (row, col), reward_color)

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
            self._push_collision_cross(row, col, (255, 60, 60))
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

            if effect["kind"] == "flash":
                row = effect["row"]
                col = effect["col"]
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                alpha = max(0, min(180, int(190 * ratio)))
                surf.fill((*effect["color"], alpha))
                self.screen.blit(surf, (x, y))
            elif effect["kind"] == "text":
                row = effect["row"]
                col = effect["col"]
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                text = self.font_small.render(effect["text"], True, effect["color"])
                offset = int((1 - ratio) * 18)
                text_rect = text.get_rect(center=(
                    x + CELL_SIZE // 2,
                    y + CELL_SIZE // 2 - 8 - offset,
                ))
                self.screen.blit(text, text_rect)
            elif effect["kind"] == "arrow":
                pr, pc = effect["previous_pos"]
                nr, nc = effect["new_pos"]
                start = (pc * CELL_SIZE + CELL_SIZE // 2, pr * CELL_SIZE + CELL_SIZE // 2)
                end = (nc * CELL_SIZE + CELL_SIZE // 2, nr * CELL_SIZE + CELL_SIZE // 2)
                color = effect["color"]
                width = max(2, int(5 * ratio))
                pygame.draw.line(self.screen, color, start, end, width)
                pygame.draw.circle(self.screen, color, end, max(4, int(8 * ratio)))
            elif effect["kind"] == "cross":
                row = effect["row"]
                col = effect["col"]
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                margin = max(5, int(8 * ratio))
                color = effect["color"]
                width = max(2, int(4 * ratio))
                pygame.draw.line(
                    self.screen, color,
                    (x + margin, y + margin),
                    (x + CELL_SIZE - margin, y + CELL_SIZE - margin),
                    width,
                )
                pygame.draw.line(
                    self.screen, color,
                    (x + CELL_SIZE - margin, y + margin),
                    (x + margin, y + CELL_SIZE - margin),
                    width,
                )

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
        self._draw_live_hud(info)
        self._draw_playback_banner()
        self._draw_agent(agent)
        self._draw_sidebar(agent, environment, info, q_learner=q_learner)
        pygame.display.flip()
        self.clock.tick(self.target_fps)

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

    def _draw_progress_bar(self, x, y, width, value, label, color):
        """Desenează o bară compactă de progres și returnează y-ul următor."""
        value = max(0.0, min(1.0, value))
        text = self.font_tiny.render(label, True, (180, 180, 180))
        self.screen.blit(text, (x, y))
        y += 14
        rect = pygame.Rect(x, y, width, 10)
        pygame.draw.rect(self.screen, (45, 45, 45), rect)
        fill = pygame.Rect(x, y, int(width * value), 10)
        pygame.draw.rect(self.screen, color, fill)
        pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)
        return y + 14

    def _draw_action_distribution(self, x, y, action_counts, width=None):
        """Afișează distribuția acțiunilor din episodul curent."""
        if width is None:
            width = SIDEBAR_WIDTH - 30
        total = max(1, sum(action_counts))
        header = self.font_tiny.render("Actiuni episod curent", True, (180, 180, 180))
        self.screen.blit(header, (x, y))
        y += 16
        colors = {
            0: (120, 180, 255),
            1: (120, 220, 180),
            2: (210, 170, 255),
            3: (255, 210, 120),
            4: (180, 180, 180),
        }
        for action in range(min(len(action_counts), len(ACTIONS))):
            label = ACTIONS.get(action, str(action))[:5]
            count = action_counts[action]
            ratio = count / total
            surf = self.font_tiny.render(f"{label:>5}", True, COLOR_TEXT)
            self.screen.blit(surf, (x, y))
            bar_x = x + 44
            bar_w = width - 78
            rect = pygame.Rect(bar_x, y + 3, bar_w, 8)
            pygame.draw.rect(self.screen, (45, 45, 45), rect)
            pygame.draw.rect(
                self.screen,
                colors.get(action, COLOR_TEXT),
                pygame.Rect(bar_x, y + 3, int(bar_w * ratio), 8),
            )
            count_text = self.font_tiny.render(str(count), True, (170, 170, 170))
            self.screen.blit(count_text, (bar_x + bar_w + 5, y - 1))
            y += 13
        return y + 4

    def _draw_live_event_card(self, x, y, info, width=None):
        """Card compact cu ultimul pas: acțiune, reward, energie și TD-error."""
        if not info or "_feedback" not in info:
            return y
        if width is None:
            width = SIDEBAR_WIDTH - 30
        feedback = info["_feedback"]
        learning = info.get("_learning", {})
        last_update = learning.get("last_update")
        reward = feedback.get("reward", 0)
        energy_delta = feedback.get("energy_delta", 0)
        action = feedback.get("action")
        terminal = feedback.get("terminal_reason")
        td = last_update[4] if last_update is not None else 0.0

        height = 58
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (38, 38, 38), rect)
        pygame.draw.rect(self.screen, self._reward_color(reward), rect, 2)

        title = f"{ACTIONS.get(action, action)} | R {reward:+.1f} | E {energy_delta:+.0f}"
        title_surf = self.font_tiny.render(title, True, self._reward_color(reward))
        self.screen.blit(title_surf, (x + 8, y + 7))

        td_color = (80, 140, 255) if td >= 0 else (180, 80, 220)
        td_surf = self.font_tiny.render(f"TD {td:+.2f}", True, td_color)
        self.screen.blit(td_surf, (x + 8, y + 24))

        cell = feedback.get("cell_type", "")
        detail = f"Cell: {cell}"
        if terminal:
            detail = f"Final: {terminal}"
        detail_surf = self.font_tiny.render(detail, True, COLOR_TEXT)
        self.screen.blit(detail_surf, (x + 8, y + 41))
        return y + height + 8

    def _draw_live_hud(self, info):
        """HUD pe grid pentru feedback imediat în timpul antrenamentului live."""
        if not info or "_feedback" not in info:
            return
        feedback = info["_feedback"]
        learning = info.get("_learning", {})
        last_update = learning.get("last_update")
        reward = feedback.get("reward", 0)
        energy_delta = feedback.get("energy_delta", 0)
        action = feedback.get("action")
        td = last_update[4] if last_update is not None else 0.0

        x, y = 10, 10
        width, height = 260, 74
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((20, 20, 20, 185))
        self.screen.blit(surf, (x, y))
        pygame.draw.rect(self.screen, self._reward_color(reward), (x, y, width, height), 2)

        title = self.font_small.render(
            f"{ACTIONS.get(action, action)}  reward {reward:+.1f}",
            True,
            self._reward_color(reward),
        )
        self.screen.blit(title, (x + 10, y + 8))

        energy_color = COLOR_ENERGY_BAR if energy_delta >= 0 else COLOR_ENERGY_LOW
        energy = self.font_tiny.render(f"Energie pas: {energy_delta:+.0f}", True, energy_color)
        self.screen.blit(energy, (x + 10, y + 32))

        td_color = (100, 165, 255) if td >= 0 else (210, 120, 240)
        td_text = self.font_tiny.render(f"TD-error: {td:+.2f}", True, td_color)
        self.screen.blit(td_text, (x + 10, y + 50))

    def _draw_playback_banner(self):
        """Afișează starea playback-ului direct pe grid."""
        if not self.human_paced:
            return
        grid_w = self.cols * CELL_SIZE
        y = self.rows * CELL_SIZE - 36
        width = min(360, grid_w - 20)
        x = 10
        surf = pygame.Surface((width, 26), pygame.SRCALPHA)
        surf.fill((15, 15, 15, 175))
        self.screen.blit(surf, (x, y))
        color = (255, 210, 80) if self.paused else (100, 220, 140)
        label = (
            f"{self._playback_status()}   SPACE pauza   . pas   +/- viteza"
        )
        text = self.font_tiny.render(label, True, color)
        self.screen.blit(text, (x + 8, y + 7))

    def _draw_card(self, x, y, width, height, title=None, accent=DASHBOARD_ACCENT):
        """Desenează un card de dashboard și returnează coordonata y a conținutului."""
        rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, DASHBOARD_PANEL, rect, border_radius=12)
        pygame.draw.rect(self.screen, (60, 66, 78), rect, 1, border_radius=12)
        pygame.draw.rect(
            self.screen,
            accent,
            pygame.Rect(x, y, 4, height),
            border_radius=2,
        )
        if title:
            surf = self.font_label.render(title.upper(), True, DASHBOARD_MUTED)
            self.screen.blit(surf, (x + 14, y + 10))
            return y + 31
        return y + 12

    def _draw_pill(self, x, y, text, color, width=None):
        """Badge rotunjit pentru status/shortcut-uri."""
        if width is None:
            width = max(54, self.font_label.size(text)[0] + 18)
        rect = pygame.Rect(x, y, width, 22)
        pygame.draw.rect(self.screen, color, rect, border_radius=11)
        surf = self.font_label.render(text, True, (16, 18, 22))
        self.screen.blit(surf, surf.get_rect(center=rect.center))
        return width

    def _draw_metric_tile(self, x, y, width, label, value, color):
        """Card mic pentru o metrică importantă."""
        rect = pygame.Rect(x, y, width, 46)
        pygame.draw.rect(self.screen, DASHBOARD_PANEL_ALT, rect, border_radius=10)
        pygame.draw.rect(self.screen, (62, 68, 80), rect, 1, border_radius=10)
        label_surf = self.font_label.render(label, True, DASHBOARD_MUTED)
        value_surf = self.font_metric.render(str(value), True, color)
        self.screen.blit(label_surf, (x + 10, y + 7))
        self.screen.blit(value_surf, (x + 10, y + 22))

    def _draw_energy_gauge(self, x, y, width, agent):
        """Bară de energie mai lizibilă, cu praguri vizuale."""
        pct = max(0.0, min(1.0, agent.energy_percent))
        color = COLOR_ENERGY_BAR if pct > 0.5 else DASHBOARD_WARNING if pct > 0.25 else DASHBOARD_DANGER
        label = self.font_label.render("ENERGIE", True, DASHBOARD_MUTED)
        self.screen.blit(label, (x, y))
        value = self.font_metric.render(f"{agent.energy:.0f}/{agent.energy_max}", True, color)
        self.screen.blit(value, (x + width - value.get_width(), y - 4))
        y += 24
        rect = pygame.Rect(x, y, width, 18)
        pygame.draw.rect(self.screen, (54, 58, 68), rect, border_radius=9)
        fill = pygame.Rect(x, y, int(width * pct), 18)
        pygame.draw.rect(self.screen, color, fill, border_radius=9)
        for threshold in (0.25, 0.5, 0.75):
            tx = x + int(width * threshold)
            pygame.draw.line(self.screen, (25, 27, 32), (tx, y), (tx, y + 18), 1)
        pygame.draw.rect(self.screen, (76, 82, 96), rect, 1, border_radius=9)
        return y + 28

    def _draw_overlay_badges(self, x, y):
        """Badges ON/OFF pentru overlay-uri."""
        badges = [
            ("Q", self.show_heatmap),
            ("POL", self.show_policy),
            ("VIS", self.show_visits),
            ("TD", self.show_td),
            ("MASK", self.show_knowledge_mask),
            ("TRAIL", self.show_trail),
        ]
        cur_x = x
        for label, enabled in badges:
            color = DASHBOARD_SUCCESS if enabled else (75, 80, 92)
            width = self._draw_pill(cur_x, y, label, color)
            cur_x += width + 6
        return y + 26

    def _draw_terrain_legend(self, x, y, width):
        """Legendă vizuală pentru celulele din hartă."""
        items = [
            ("Start", CellType.START),
            ("Țintă", CellType.TARGET),
            ("Hrană", CellType.FOOD),
            ("Noroi", CellType.MUD),
            ("Pericol", CellType.DANGER),
            ("Zid", CellType.OBSTACLE),
        ]
        col_w = width // 2
        for idx, (label, cell) in enumerate(items):
            lx = x + (idx % 2) * col_w
            ly = y + (idx // 2) * 20
            pygame.draw.rect(
                self.screen,
                CELL_COLORS[cell],
                pygame.Rect(lx, ly + 3, 12, 12),
                border_radius=3,
            )
            surf = self.font_label.render(label, True, COLOR_TEXT)
            self.screen.blit(surf, (lx + 18, ly))
        return y + 62

    def _draw_controls_footer(self, x, y, width):
        """Footer fix cu tastele principale, grupate vizual."""
        rect = pygame.Rect(x, y, width, 68)
        pygame.draw.rect(self.screen, (28, 31, 38), rect, border_radius=12)
        lines = [
            ("PLAYBACK", "SPACE pauză · . pas · -/+ viteză"),
            ("OVERLAY", "H Q-map · P policy · V vizite · T TD"),
            ("CONTROL", "E nivel energie · K mask · L trail · Q quit"),
        ]
        cur_y = y + 9
        for label, text in lines:
            label_surf = self.font_label.render(label, True, DASHBOARD_ACCENT)
            text_surf = self.font_label.render(text, True, DASHBOARD_MUTED)
            self.screen.blit(label_surf, (x + 12, cur_y))
            self.screen.blit(text_surf, (x + 86, cur_y))
            cur_y += 18

    def _draw_sidebar(self, agent, environment, info, q_learner=None):
        """Desenează panoul lateral cu informații."""
        x_start = self.cols * CELL_SIZE
        panel_x = x_start + 14
        panel_w = SIDEBAR_WIDTH - 28
        y = 14

        pygame.draw.rect(
            self.screen,
            (24, 27, 34),
            pygame.Rect(x_start, 0, SIDEBAR_WIDTH, self.window_height),
        )

        # Header
        title = self.font_title.render("Q-Learning Lab", True, (245, 248, 255))
        subtitle = self.font_label.render("Observabilitate training live", True, DASHBOARD_MUTED)
        self.screen.blit(title, (panel_x, y))
        self.screen.blit(subtitle, (panel_x, y + 27))

        if not agent.is_alive:
            status_text, status_color = "DECEDAT", DASHBOARD_DANGER
        elif agent.reached_target:
            status_text, status_color = "VICTORIE", DASHBOARD_SUCCESS
        else:
            status_text, status_color = "ACTIV", DASHBOARD_SUCCESS
        self._draw_pill(panel_x + panel_w - 86, y + 4, status_text, status_color, width=76)
        y += 58

        # Agent card
        card_h = 156
        content_y = self._draw_card(panel_x, y, panel_w, card_h, title="Agent", accent=status_color)
        content_y = self._draw_energy_gauge(panel_x + 14, content_y, panel_w - 28, agent)
        tile_w = (panel_w - 38) // 2
        self._draw_metric_tile(panel_x + 14, content_y, tile_w, "Pași", agent.total_steps, DASHBOARD_ACCENT)
        self._draw_metric_tile(
            panel_x + 24 + tile_w,
            content_y,
            tile_w,
            "Reward",
            f"{agent.total_reward:.1f}",
            self._reward_color(agent.total_reward),
        )
        content_y += 52
        self._draw_metric_tile(
            panel_x + 14,
            content_y,
            tile_w,
            "Poziție",
            f"{agent.position[0]},{agent.position[1]}",
            COLOR_TEXT,
        )
        self._draw_metric_tile(
            panel_x + 24 + tile_w,
            content_y,
            tile_w,
            "Celule",
            agent.coverage,
            DASHBOARD_SUCCESS,
        )
        y += card_h + 10

        # Playback + live step card
        live = info.get("_live", {}) if info else {}
        content_y = self._draw_card(panel_x, y, panel_w, 214, title="Live step", accent=DASHBOARD_ACCENT)
        if self.human_paced:
            play_color = DASHBOARD_WARNING if self.paused else DASHBOARD_SUCCESS
            self._draw_pill(panel_x + 14, content_y, self._playback_status(), play_color)
            content_y += 28
        if live:
            content_y = self._draw_progress_bar(
                panel_x + 14,
                content_y,
                panel_w - 28,
                live.get("progress", 0.0),
                f"Episod {live.get('step', 0) + 1}/{live.get('max_steps', 0)}",
                DASHBOARD_ACCENT,
            )
        content_y = self._draw_live_event_card(panel_x + 14, content_y + 4, info, width=panel_w - 28)
        if live:
            chip_y = content_y
            chip_w = (panel_w - 44) // 3
            self._draw_metric_tile(panel_x + 14, chip_y, chip_w, "Coliziuni", live.get("collisions", 0), DASHBOARD_DANGER)
            self._draw_metric_tile(panel_x + 22 + chip_w, chip_y, chip_w, "Hrană", live.get("food_collected", 0), DASHBOARD_WARNING)
            self._draw_metric_tile(panel_x + 30 + chip_w * 2, chip_y, chip_w, "Noroi", live.get("mud_steps", 0), (205, 160, 115))
        y += 224

        # Learning card
        if q_learner is not None:
            stats = q_learner.get_knowledge_stats()
            content_y = self._draw_card(panel_x, y, panel_w, 176, title="Învățare", accent=(180, 120, 255))
            content_y = self._draw_progress_bar(
                panel_x + 14,
                content_y,
                panel_w - 28,
                stats["fill_pct"] / 100,
                f"Q-table completat: {stats['fill_pct']:.1f}%",
                (180, 120, 255),
            )
            content_y = self._draw_progress_bar(
                panel_x + 14,
                content_y + 5,
                panel_w - 28,
                stats["coverage_pct"] / 100,
                f"Celule explorate: {stats['coverage_pct']:.1f}%",
                DASHBOARD_SUCCESS,
            )
            tile_w = (panel_w - 38) // 2
            self._draw_metric_tile(panel_x + 14, content_y + 6, tile_w, "Mean |Q|", f"{stats['mean_abs_q']:.2f}", COLOR_TEXT)
            self._draw_metric_tile(panel_x + 24 + tile_w, content_y + 6, tile_w, "TD recent", f"{stats['mean_recent_td']:.2f}", DASHBOARD_WARNING)
            history = info.get("_learning", {}).get("history", []) if info else []
            if len(history) >= 2:
                self._draw_sparkline(
                    panel_x + 14,
                    content_y + 58,
                    values=[ep.total_reward for ep in history[-120:]],
                    color=DASHBOARD_SUCCESS,
                    label="Reward / episod",
                    width=panel_w - 28,
                    height=24,
                )
            y += 186

        # Overlay + legend card
        bottom_reserved = 84
        remaining = self.window_height - y - bottom_reserved - 12
        if remaining >= 120:
            content_y = self._draw_card(panel_x, y, panel_w, remaining, title="Hartă & overlay", accent=DASHBOARD_WARNING)
            level = self.font_label.render(f"Policy energie: {self._overlay_level_label(agent)}", True, COLOR_TEXT)
            self.screen.blit(level, (panel_x + 14, content_y))
            content_y += 20
            content_y = self._draw_overlay_badges(panel_x + 14, content_y)
            content_y += 8
            self._draw_terrain_legend(panel_x + 14, content_y, panel_w - 28)

        self._draw_controls_footer(panel_x, self.window_height - 78, panel_w)

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
