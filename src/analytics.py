"""
Modul Analytics: export CSV și grafice Matplotlib pentru analiza antrenamentului Q-Learning.
"""

import csv
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend non-interactiv (fără GUI)
import matplotlib.pyplot as plt


# Mapare outcome intern → etichetă pentru CSV/grafice
OUTCOME_LABELS = {
    "target_reached": "SUCCESS",
    "energy_depleted": "DEATH_ENERGY",
    "danger": "DEATH_TRAP",
    "timeout": "TIMEOUT",
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
                "outcome", "coverage_pct", "energy_remaining"
            ])
            for ep in history:
                writer.writerow([
                    ep.episode_id,
                    ep.total_steps,
                    f"{ep.total_reward:.2f}",
                    f"{ep.epsilon:.4f}",
                    OUTCOME_LABELS.get(ep.outcome, ep.outcome),
                    f"{ep.coverage:.2f}",
                    f"{ep.energy_remaining:.1f}",
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
        colors = ["#ff6b35", "#50c878", "#7fbfff", "#e74c3c", "#9b59b6"]
        kernel = np.ones(window) / window

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        ax_reward, ax_success = axes

        for i, (alpha, history) in enumerate(sorted(histories.items())):
            color = colors[i % len(colors)]
            label = f"α={alpha}"

            rewards = [ep.total_reward for ep in history]
            rolling_r = np.convolve(rewards, kernel, mode="valid")
            rolling_rx = list(range(window - 1, len(rewards)))
            ax_reward.plot(rolling_rx, rolling_r, color=color, linewidth=1.8, label=label)

            successes = [1 if ep.outcome == "target_reached" else 0 for ep in history]
            rolling_s = np.convolve(successes, kernel, mode="valid") * 100
            rolling_sx = list(range(window - 1, len(successes)))
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
