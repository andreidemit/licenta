"""
Modul Analytics: export CSV și grafice Matplotlib pentru analiza antrenamentului Q-Learning.
"""

import csv
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend non-interactiv (fără GUI)
import matplotlib.pyplot as plt

from src.constants import ACTIONS
from src.environment import CellType


# Mapare outcome intern → etichetă pentru CSV/grafice
OUTCOME_LABELS = {
    "target_reached": "SUCCESS",
    "energy_depleted": "DEATH_ENERGY",
    "danger": "DEATH_TRAP",
    "timeout": "TIMEOUT",
}

CELL_RGB = {
    CellType.EMPTY: (144, 238, 144),
    CellType.OBSTACLE: (100, 100, 100),
    CellType.MUD: (139, 119, 101),
    CellType.FOOD: (255, 215, 0),
    CellType.DANGER: (220, 20, 60),
    CellType.TARGET: (0, 191, 255),
    CellType.START: (50, 205, 50),
}


class Analytics:
    """
    Gestionează exportul de date și vizualizările post-antrenament.

    Fișierele generate sunt salvate în `out_dir` cu denumire standard:
      - results_<scenario>_<grid>_<seed>.csv
      - convergence_<scenario>_<grid>_<seed>.png
      - epsilon_<scenario>_<grid>_<seed>.png
      - success_<scenario>_<grid>_<seed>.png
    """

    def __init__(self, scenario: str, grid_size: int, seed: int, out_dir: str = "data"):
        self.scenario = scenario
        self.grid_size = grid_size
        self.seed = seed
        self.out_dir = out_dir
        os.makedirs(out_dir, exist_ok=True)

    def _filename(self, prefix: str, ext: str) -> str:
        return os.path.join(
            self.out_dir,
            f"{prefix}_{self.scenario}_{self.grid_size}_{self.seed}.{ext}"
        )

    def _validated_window(self, history, window: int) -> int:
        """Ajustează fereastra rolling la istoricul disponibil."""
        if not history:
            raise ValueError("Istoricul episoadelor este gol.")
        return max(1, min(window, len(history)))

    # ------------------------------------------------------------------
    # Export CSV
    # ------------------------------------------------------------------

    def export_csv(self, history) -> str:
        """
        Exportă istoricul episoadelor în CSV.

        Args:
            history: list[EpisodeResult]

        Returns:
            str — calea fișierului generat
        """
        filepath = self._filename("results", "csv")
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "episode_id", "steps", "total_reward", "epsilon",
                "outcome", "coverage_pct", "energy_remaining",
                "collisions", "food_collected", "mud_steps",
                "danger_entries", "energy_spent", "energy_gained",
                "action_up", "action_down", "action_left",
                "action_right", "action_stay", "mean_abs_td",
                "q_nonzero", "q_fill_pct"
            ])
            for ep in history:
                action_counts = getattr(ep, "action_counts", [0, 0, 0, 0, 0])
                writer.writerow([
                    ep.episode_id,
                    ep.total_steps,
                    f"{ep.total_reward:.2f}",
                    f"{ep.epsilon:.4f}",
                    OUTCOME_LABELS.get(ep.outcome, ep.outcome),
                    f"{ep.coverage:.2f}",
                    f"{ep.energy_remaining:.1f}",
                    getattr(ep, "collisions", 0),
                    getattr(ep, "food_collected", 0),
                    getattr(ep, "mud_steps", 0),
                    getattr(ep, "danger_entries", 0),
                    f"{getattr(ep, 'energy_spent', 0.0):.1f}",
                    f"{getattr(ep, 'energy_gained', 0.0):.1f}",
                    action_counts[0] if len(action_counts) > 0 else 0,
                    action_counts[1] if len(action_counts) > 1 else 0,
                    action_counts[2] if len(action_counts) > 2 else 0,
                    action_counts[3] if len(action_counts) > 3 else 0,
                    action_counts[4] if len(action_counts) > 4 else 0,
                    f"{getattr(ep, 'mean_abs_td', 0.0):.4f}",
                    getattr(ep, "q_nonzero", 0),
                    f"{getattr(ep, 'q_fill_pct', 0.0):.2f}",
                ])
        return filepath

    # ------------------------------------------------------------------
    # Grafice individuale
    # ------------------------------------------------------------------

    def plot_convergence(self, history, window: int = 50) -> str:
        """
        Grafic: reward per episod + rolling average.

        Returns:
            str — calea fișierului PNG generat
        """
        window = self._validated_window(history, window)
        rewards = [ep.total_reward for ep in history]
        episodes = list(range(len(rewards)))

        # Rolling average
        kernel = np.ones(window) / window
        rolling = np.convolve(rewards, kernel, mode="valid")
        rolling_x = list(range(window - 1, len(rewards)))

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(episodes, rewards, alpha=0.15, s=4, color="#7fbfff", label="Reward per episod")
        ax.plot(rolling_x, rolling, color="#ff6b35", linewidth=2,
                label=f"Rolling avg (window={window})")
        ax.set_xlabel("Episod")
        ax.set_ylabel("Reward total")
        ax.set_title(f"Convergență Reward — Scenariul {self.scenario} | Grid {self.grid_size}×{self.grid_size} | Seed {self.seed}")
        ax.legend()
        ax.grid(True, alpha=0.3)

        filepath = self._filename("convergence", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_epsilon_decay(self, history) -> str:
        """
        Grafic: decăderea epsilon de-a lungul antrenamentului.

        Returns:
            str — calea fișierului PNG generat
        """
        epsilons = [ep.epsilon for ep in history]
        episodes = list(range(len(epsilons)))

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(episodes, epsilons, color="#50c878", linewidth=1.5)
        ax.set_xlabel("Episod")
        ax.set_ylabel("Epsilon")
        ax.set_title(f"Decădere Epsilon — Scenariul {self.scenario}")
        ax.grid(True, alpha=0.3)

        filepath = self._filename("epsilon", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_success_rate(self, history, window: int = 50) -> str:
        """
        Grafic: rata de succes rolling.

        Returns:
            str — calea fișierului PNG generat
        """
        window = self._validated_window(history, window)
        successes = [1 if ep.outcome == "target_reached" else 0 for ep in history]

        kernel = np.ones(window) / window
        rolling = np.convolve(successes, kernel, mode="valid") * 100
        rolling_x = list(range(window - 1, len(successes)))

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(rolling_x, rolling, color="#9b59b6", linewidth=2,
                label=f"Rată succes rolling (window={window})")
        ax.axhline(y=80, color="#e74c3c", linestyle="--", alpha=0.7, label="Prag 80%")
        ax.set_xlabel("Episod")
        ax.set_ylabel("Rată succes (%)")
        ax.set_ylim(0, 105)
        ax.set_title(f"Rată Succes — Scenariul {self.scenario}")
        ax.legend()
        ax.grid(True, alpha=0.3)

        filepath = self._filename("success", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def save_all_plots(self, history, window: int = 50) -> list:
        """
        Generează și salvează toate cele 3 grafice standard.

        Returns:
            list[str] — căile fișierelor generate
        """
        paths = [
            self.plot_convergence(history, window=window),
            self.plot_epsilon_decay(history),
            self.plot_success_rate(history, window=window),
        ]
        return paths

    # ------------------------------------------------------------------
    # Artefacte metadata și traseu
    # ------------------------------------------------------------------

    def _map_stats(self, environment) -> dict:
        counts = {cell.name.lower(): 0 for cell in CellType}
        for row in environment.grid:
            for cell in row:
                counts[CellType(cell).name.lower()] += 1
        return {
            "rows": environment.rows,
            "cols": environment.cols,
            "start": list(environment.start_pos),
            "target": list(environment.target_pos),
            "bfs_distance": environment.bfs(environment.start_pos, environment.target_pos),
            "cell_counts": counts,
        }

    def _history_summary(self, history) -> dict:
        if not history:
            return {
                "episodes": 0,
                "success_rate_last_100": 0.0,
                "avg_reward_last_100": 0.0,
                "avg_steps_last_100": 0.0,
                "outcomes": {},
            }
        recent = history[-min(100, len(history)):]
        outcomes = {}
        for ep in history:
            outcomes[ep.outcome] = outcomes.get(ep.outcome, 0) + 1
        return {
            "episodes": len(history),
            "success_rate_last_100": (
                sum(1 for ep in recent if ep.outcome == "target_reached") / len(recent) * 100
            ),
            "avg_reward_last_100": sum(ep.total_reward for ep in recent) / len(recent),
            "avg_steps_last_100": sum(ep.total_steps for ep in recent) / len(recent),
            "outcomes": outcomes,
        }

    def export_run_manifest(self, history, environment, q_learner,
                            artifacts=None, greedy_summary=None,
                            energy=None) -> str:
        """Salvează metadata reproductibilă pentru o rulare."""
        artifacts = artifacts or {}
        filepath = self._filename("manifest", "json")
        q_total = q_learner.q_table.size
        payload = {
            "scenario": self.scenario,
            "grid_size": self.grid_size,
            "seed": self.seed,
            "energy": energy,
            "hyperparameters": {
                "alpha": q_learner.alpha,
                "gamma": q_learner.gamma,
                "epsilon": q_learner.epsilon,
                "epsilon_min": q_learner.epsilon_min,
                "epsilon_decay": q_learner.epsilon_decay,
            },
            "map": self._map_stats(environment),
            "history": self._history_summary(history),
            "q_table": {
                "shape": list(q_learner.q_table.shape),
                "nonzero": q_learner.get_nonzero_count(),
                "total": q_total,
                "fill_pct": (q_learner.get_nonzero_count() / q_total * 100) if q_total else 0.0,
            },
            "greedy": greedy_summary or {},
            "artifacts": artifacts,
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        return filepath

    def export_greedy_trajectory(self, trajectory, summary=None) -> tuple:
        """Exportă traseul greedy final în CSV și sumar JSON."""
        csv_path = self._filename("greedy_trajectory", "csv")
        json_path = self._filename("greedy_trajectory", "json")
        fieldnames = [
            "step", "previous_row", "previous_col", "row", "col", "energy",
            "reward", "total_reward", "action", "action_name", "cell_type",
            "terminal_reason",
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for item in trajectory:
                row = dict(item)
                action = row.get("action")
                row["action_name"] = ACTIONS.get(action, action)
                writer.writerow({key: row.get(key, "") for key in fieldnames})
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(summary or {}, f, ensure_ascii=False, indent=2)
        return csv_path, json_path

    # ------------------------------------------------------------------
    # Vizualizări statice pentru hartă, Q-table și traseu
    # ------------------------------------------------------------------

    def _grid_rgb(self, environment):
        image = np.zeros((environment.rows, environment.cols, 3), dtype=float)
        for row in range(environment.rows):
            for col in range(environment.cols):
                image[row, col] = np.array(CELL_RGB[CellType(environment.grid[row][col])]) / 255.0
        return image

    def _setup_grid_axes(self, ax, environment, title):
        ax.set_title(title)
        ax.set_xticks(np.arange(-0.5, environment.cols, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, environment.rows, 1), minor=True)
        ax.grid(which="minor", color="white", linestyle="-", linewidth=0.4, alpha=0.45)
        ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)

    def plot_environment_map(self, environment) -> str:
        """Salvează harta mediului ca PNG static."""
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(self._grid_rgb(environment))
        self._setup_grid_axes(ax, environment, f"Harta mediu - Scenariul {self.scenario}")
        for label, pos, color in (
            ("S", environment.start_pos, "black"),
            ("T", environment.target_pos, "white"),
        ):
            row, col = pos
            ax.text(col, row, label, ha="center", va="center", color=color, weight="bold")
        filepath = self._filename("map", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_policy_map(self, environment, q_learner, energy_level: int = 3) -> str:
        """Salvează politica greedy învățată ca săgeți peste hartă."""
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(self._grid_rgb(environment))
        self._setup_grid_axes(ax, environment, f"Politica greedy - E={energy_level}")
        directions = {
            0: (0, -0.35),
            1: (0, 0.35),
            2: (-0.35, 0),
            3: (0.35, 0),
        }
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] == CellType.OBSTACLE:
                    continue
                q_slice = q_learner.q_table[row, col, energy_level, :]
                if np.max(q_slice) == 0.0:
                    continue
                action = int(np.argmax(q_slice))
                if action == 4:
                    ax.scatter(col, row, s=14, c="white", edgecolors="black", linewidths=0.5)
                else:
                    dx, dy = directions[action]
                    ax.arrow(col, row, dx, dy, color="white", width=0.025,
                             head_width=0.16, length_includes_head=True)
        filepath = self._filename(f"policy_e{energy_level}", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_q_heatmap(self, environment, q_learner, energy_level: int = 3) -> str:
        """Salvează heatmap-ul max-Q pentru un bucket de energie."""
        values = np.full((environment.rows, environment.cols), np.nan)
        for row in range(environment.rows):
            for col in range(environment.cols):
                if environment.grid[row][col] != CellType.OBSTACLE:
                    values[row, col] = np.max(q_learner.q_table[row, col, energy_level, :])
        fig, ax = plt.subplots(figsize=(7, 7))
        im = ax.imshow(values, cmap="RdYlGn")
        self._setup_grid_axes(ax, environment, f"Max-Q heatmap - E={energy_level}")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        filepath = self._filename(f"q_heatmap_e{energy_level}", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_visit_heatmap(self, environment, q_learner) -> str:
        """Salvează heatmap-ul vizitelor per celulă."""
        visits = np.array(q_learner.get_visit_counts(), dtype=float)
        values = np.log1p(visits)
        values[visits == 0] = np.nan
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(self._grid_rgb(environment), alpha=0.35)
        im = ax.imshow(values, cmap="Blues", alpha=0.85)
        self._setup_grid_axes(ax, environment, "Heatmap vizite")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        filepath = self._filename("visit_heatmap", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_td_heatmap(self, environment, q_learner) -> str:
        """Salvează heatmap-ul TD-error decăzut."""
        values = np.array(q_learner.get_td_error_map(), dtype=float)
        values[values <= 1e-9] = np.nan
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(self._grid_rgb(environment), alpha=0.35)
        im = ax.imshow(values, cmap="hot", alpha=0.85)
        self._setup_grid_axes(ax, environment, "Heatmap TD-error")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        filepath = self._filename("td_heatmap", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_greedy_path(self, environment, trajectory) -> str:
        """Salvează traseul greedy final peste hartă."""
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.imshow(self._grid_rgb(environment))
        self._setup_grid_axes(ax, environment, f"Traseu greedy - Scenariul {self.scenario}")
        if trajectory:
            xs = [item["previous_col"] for item in trajectory[:1]] + [item["col"] for item in trajectory]
            ys = [item["previous_row"] for item in trajectory[:1]] + [item["row"] for item in trajectory]
            ax.plot(xs, ys, color="white", linewidth=2.2, marker="o", markersize=3)
        filepath = self._filename("greedy_path", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def save_visual_artifacts(self, environment, q_learner, trajectory=None,
                              energy_level: int = 3) -> dict:
        """Generează pachetul standard de vizualizări statice."""
        artifacts = {
            "map_png": self.plot_environment_map(environment),
            "policy_png": self.plot_policy_map(environment, q_learner, energy_level=energy_level),
            "q_heatmap_png": self.plot_q_heatmap(environment, q_learner, energy_level=energy_level),
            "visit_heatmap_png": self.plot_visit_heatmap(environment, q_learner),
            "td_heatmap_png": self.plot_td_heatmap(environment, q_learner),
        }
        if trajectory is not None:
            artifacts["greedy_path_png"] = self.plot_greedy_path(environment, trajectory)
        return artifacts

    # ------------------------------------------------------------------
    # Grafic comparativ alpha (Scenariul C)
    # ------------------------------------------------------------------

    def plot_alpha_comparison(self, histories: dict, window: int = 50) -> str:
        """
        Grafic suprapus pentru analiza sensibilității la alpha.

        Args:
            histories: dict[float, list[EpisodeResult]] — {alpha: history}
            window: fereastra rolling average

        Returns:
            str — calea fișierului PNG generat
        """
        if not histories:
            raise ValueError("Nu există istorice pentru comparația alpha.")

        colors = ["#ff6b35", "#50c878", "#7fbfff", "#e74c3c", "#9b59b6"]

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        ax_reward, ax_success = axes

        for i, (alpha, history) in enumerate(sorted(histories.items())):
            window_for_history = self._validated_window(history, window)
            kernel = np.ones(window_for_history) / window_for_history
            color = colors[i % len(colors)]
            label = f"α={alpha}"

            rewards = [ep.total_reward for ep in history]
            rolling_r = np.convolve(rewards, kernel, mode="valid")
            rolling_rx = list(range(window_for_history - 1, len(rewards)))
            ax_reward.plot(rolling_rx, rolling_r, color=color, linewidth=1.8, label=label)

            successes = [1 if ep.outcome == "target_reached" else 0 for ep in history]
            rolling_s = np.convolve(successes, kernel, mode="valid") * 100
            rolling_sx = list(range(window_for_history - 1, len(successes)))
            ax_success.plot(rolling_sx, rolling_s, color=color, linewidth=1.8, label=label)

        ax_reward.set_xlabel("Episod")
        ax_reward.set_ylabel("Reward rolling avg")
        ax_reward.set_title("Convergență Reward vs Alpha")
        ax_reward.legend()
        ax_reward.grid(True, alpha=0.3)

        ax_success.set_xlabel("Episod")
        ax_success.set_ylabel("Rată succes (%)")
        ax_success.set_ylim(0, 105)
        ax_success.set_title("Rată Succes vs Alpha")
        ax_success.axhline(y=80, color="gray", linestyle="--", alpha=0.5)
        ax_success.legend()
        ax_success.grid(True, alpha=0.3)

        fig.suptitle(f"Analiză Sensibilitate Alpha — Scenariul C | Grid {self.grid_size}×{self.grid_size} | Seed {self.seed}")

        filepath = os.path.join(
            self.out_dir,
            f"alpha_comparison_C_{self.grid_size}_{self.seed}.png"
        )
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath

    def plot_scenario_comparison(self, histories: dict, window: int = 50) -> str:
        """
        Grafic comparativ pentru scenarii: reward rolling, success rolling și outcome-uri.
        """
        if not histories:
            raise ValueError("Nu există istorice pentru comparația scenariilor.")

        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        ax_reward, ax_success, ax_outcomes = axes
        colors = ["#ff6b35", "#50c878", "#7fbfff", "#9b59b6", "#e74c3c"]
        outcome_keys = ["target_reached", "energy_depleted", "danger", "timeout"]

        for i, (scenario, history) in enumerate(histories.items()):
            window_for_history = self._validated_window(history, window)
            kernel = np.ones(window_for_history) / window_for_history
            color = colors[i % len(colors)]

            rewards = [ep.total_reward for ep in history]
            rolling_r = np.convolve(rewards, kernel, mode="valid")
            rolling_rx = list(range(window_for_history - 1, len(rewards)))
            ax_reward.plot(rolling_rx, rolling_r, color=color, linewidth=1.8, label=scenario)

            successes = [1 if ep.outcome == "target_reached" else 0 for ep in history]
            rolling_s = np.convolve(successes, kernel, mode="valid") * 100
            rolling_sx = list(range(window_for_history - 1, len(successes)))
            ax_success.plot(rolling_sx, rolling_s, color=color, linewidth=1.8, label=scenario)

        x = np.arange(len(histories))
        bottom = np.zeros(len(histories))
        scenario_names = list(histories.keys())
        for outcome in outcome_keys:
            values = [
                sum(1 for ep in histories[scenario] if ep.outcome == outcome)
                for scenario in scenario_names
            ]
            ax_outcomes.bar(x, values, bottom=bottom, label=OUTCOME_LABELS.get(outcome, outcome))
            bottom += np.array(values)

        ax_reward.set_title("Reward rolling avg")
        ax_reward.set_xlabel("Episod")
        ax_reward.set_ylabel("Reward")
        ax_reward.grid(True, alpha=0.3)
        ax_reward.legend()

        ax_success.set_title("Rata succes rolling")
        ax_success.set_xlabel("Episod")
        ax_success.set_ylabel("Succes (%)")
        ax_success.set_ylim(0, 105)
        ax_success.grid(True, alpha=0.3)
        ax_success.legend()

        ax_outcomes.set_title("Distribuție outcome-uri")
        ax_outcomes.set_xticks(x)
        ax_outcomes.set_xticklabels(scenario_names)
        ax_outcomes.set_ylabel("Episoade")
        ax_outcomes.legend(fontsize=8)

        fig.suptitle("Comparație scenarii")
        filepath = self._filename("scenario_comparison", "png")
        fig.savefig(filepath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        return filepath
