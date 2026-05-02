# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

A Python-based Q-Learning simulation for autonomous grid navigation and survival. An agent learns to navigate a procedurally generated grid (with obstacles, mud, food, danger zones, and a target) using tabular Q-Learning with an energy homeostasis mechanic. Academic thesis project.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Manual control mode (arrow keys in Pygame)
python -m src.main
python -m src.main --grid 10 --seed 100

# Training mode
python -m src.main --train
python -m src.main --train --grid 20 --seed 42 --episodes 2000 --energy 100 --visualize

# Run tests
python tests/test_quick.py          # Basic environment/agent functionality
python tests/test_convergence.py    # Q-Learning convergence on 10×10 grid
```

## Architecture

**Five core modules** in `src/`:

- **`environment.py`** — Procedural grid generation (seed-based, BFS-validated to guarantee solvability) and action processing via `try_move()`. Returns reward, new state, terminal flag.
- **`agent.py`** — Agent state: `(row, col, energy_level)`. Energy is continuous [0–100] but discretized into 4 buckets for Q-table indexing. Tracks per-episode statistics.
- **`q_learning.py`** — Tabular Q-table as numpy array `(rows, cols, 4_energy_levels, 5_actions)`. Epsilon-greedy policy with per-episode ε decay. Bellman updates.
- **`trainer.py`** — Orchestrates training loop. `run_episode()` executes one episode; `run_greedy_episode()` evaluates the learned policy with no exploration. Returns `EpisodeResult` dataclass.
- **`renderer.py`** — Pygame GUI: grid cells color-coded by type, agent circle shifts red as energy depletes, sidebar shows live stats.
- **`main.py`** — CLI entry point (argparse). Two modes: manual (Pygame event loop) or training.

**Data flow per step:** Renderer draws state → User/Agent selects action → `environment.try_move()` processes it → Agent updates state + energy → QLearning computes Bellman update → Trainer logs result.

## Key Design Details

**State space:** `(row, col, energy_bucket)` — energy discretized into 4 levels (0=<25%, 1=25–50%, 2=50–75%, 3=≥75%). Same position can have 4 different optimal actions depending on energy, enabling hunger-aware navigation.

**Q-table dimensions:** `(GRID_ROWS, GRID_COLS, 4, 5)` — 8,000 entries for default 20×20 grid. Intentionally tabular (not DQN) for interpretability and thesis analysis.

**Reward structure:** -1/step, +15 food, -5 obstacle hit, +100 target, -100 death (energy depleted or danger cell), -2 extra mud cost.

**Map generation:** Densities fixed at 15% obstacles, 8% mud, 5% food, 3% danger. Every map is BFS-validated before use; regenerate on failure.

**Hyperparameters** (`constants.py`): α=0.1, γ=0.95, ε_start=1.0, ε_min=0.01, ε_decay=0.995, MAX_STEPS=500.

## Implementation Status

**Completed:** Procedural generation, 7-cell terrain system, energy homeostasis, tabular Q-Learning, Pygame GUI, CLI, greedy evaluation, basic tests.

**Planned (not yet implemented):** Q-value heatmap overlay, policy arrow visualization, CSV episode export, Matplotlib convergence graphs, Scenario B (limited energy/mandatory pit-stops), Scenario C (dynamic environment mid-training), ablation studies. See `plan.md` for the full 9-step roadmap.
