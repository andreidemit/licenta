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
    GRID_ROWS, GRID_COLS, ACTION_DELTAS,
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
        self.font_xl = pygame.font.SysFont("monospace", 36, bold=True)

        # Toggle overlay-uri
        self.show_heatmap = False
        self.show_policy = False

    def draw(self, environment, agent, info=None, q_learner=None):
        """
        Randează un frame complet: grid + agent + sidebar.

        Args:
            environment: instanța Environment
            agent: instanța Agent
            info: dict opțional cu informații extra (episod, epsilon etc.)
            q_learner: instanța QLearning, necesară pentru overlay-uri heatmap/policy
        """
        self.screen.fill(COLOR_BACKGROUND)
        self._draw_grid(environment)
        if self.show_heatmap and q_learner is not None:
            self._draw_heatmap(environment, q_learner)
        if self.show_policy and q_learner is not None:
            self._draw_policy_arrows(environment, q_learner)
        self._draw_agent(agent)
        self._draw_sidebar(agent, environment, info)
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

    def _draw_heatmap(self, environment, q_learner):
        """Suprapune heatmap-ul valorilor Q maxime pe grid (semi-transparent)."""
        # Colectează toate valorile max-Q pentru normalizare globală
        q_max_values = []
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] != CellType.OBSTACLE:
                    q_max_values.append(float(np.max(q_learner.q_table[row, col, :, :])))

        if not q_max_values:
            return

        global_min = min(q_max_values)
        global_max = max(q_max_values)
        value_range = global_max - global_min + 1e-9

        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] == CellType.OBSTACLE:
                    continue
                max_q = float(np.max(q_learner.q_table[row, col, :, :]))
                t = (max_q - global_min) / value_range

                # Interpolare culoare: t=0 → roșu (180,0,0), t=1 → verde (0,200,80)
                r_ch = int(180 * (1 - t))
                g_ch = int(200 * t)
                b_ch = int(80 * t)

                surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                surf.fill((r_ch, g_ch, b_ch, 160))
                self.screen.blit(surf, (col * CELL_SIZE, row * CELL_SIZE))

    def _draw_policy_arrows(self, environment, q_learner):
        """Desenează săgeți pentru acțiunea optimă în fiecare celulă vizitată."""
        for row in range(environment.rows):
            for col in range(environment.cols):
                cell = environment.grid[row][col]
                if cell == CellType.OBSTACLE:
                    continue

                q_slice = q_learner.q_table[row, col, :, :]
                if np.max(q_slice) == 0.0:
                    continue  # celulă nevizitată, fără săgeată

                best_action = int(np.argmax(np.max(q_slice, axis=0)))
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

    def _draw_sidebar(self, agent, environment, info):
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

        # Informații adiționale
        if info:
            pygame.draw.line(
                self.screen, COLOR_GRID_LINE,
                (x_start, y), (x_start + SIDEBAR_WIDTH - 20, y)
            )
            y += 15
            for key, value in info.items():
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
            "[R] Reset     [Q] Quit",
        ]
        for line in shortcuts:
            surf = self.font_small.render(line, True, (150, 150, 150))
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
