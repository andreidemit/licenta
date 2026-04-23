# Copilot instructions

## Project overview

This repository is an academic Python simulation of tabular Q-Learning for autonomous grid navigation and survival. The core reinforcement-learning state is `(row, col, energy_bucket)`, and the project intentionally uses a numpy Q-table rather than a neural-network policy.

## Commands

Run commands from the repository root with the active virtual-environment interpreter.

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Manual mode
python -m src.main
python -m src.main --grid 10 --seed 100

# Training / replay
python -m src.main --train
python -m src.main --train --scenario A
python -m src.main --train --scenario C
python -m src.main --alpha-sensitivity
python -m src.main --train --scenario WAREHOUSE
python -m src.main --train --save-qtable data/qt.npy
python -m src.main --load-qtable data/qt.npy --visualize

# Test modules
python -m tests.test_quick
python -m tests.test_convergence
python -m tests.test_scenarios
python -m tests.test_warehouse
python -m tests.test_analytics
python -m tests.test_persistence

# Single test function
python -c "from tests.test_analytics import test_export_csv_creates_file; test_export_csv_creates_file()"
```

## Architecture

- `src/main.py` is the orchestration layer. It selects manual mode, training, Q-table replay, alpha-sensitivity analysis, or the fixed `WAREHOUSE` scenario.
- `src/environment.py` owns map generation and move resolution. Procedural maps are seed-based and BFS-validated so start and target stay connected. `Environment.try_move()` returns the full transition payload used everywhere else.
- `src/agent.py` owns continuous agent state and per-episode metrics. `Agent.get_state()` is the projection into the RL state space consumed by Q-Learning.
- `src/q_learning.py` stores the Q-table as a numpy array shaped `(rows, cols, 4, 5)` and owns epsilon-greedy action selection, Bellman updates, and Q-table persistence.
- `src/trainer.py` is the only training loop. It resets the environment each episode, applies action results to the agent, performs Bellman updates, tracks `EpisodeResult`, and implements Scenario C obstacle relocation.
- `src/renderer.py` is a visualization layer only. It can overlay a Q-value heatmap and learned policy arrows over the grid.
- `src/analytics.py` exports CSV results and Matplotlib plots under `data/` after training.
- `src/warehouse_scenario.py` replaces procedural generation with a fixed 20x20 warehouse layout, but still reuses the same `QLearning`, `Trainer`, `Renderer`, and `Analytics` pipeline.

## Key conventions

- Keep the transition contract centered on `Environment.try_move()` plus `Agent.apply_action_result()`. Reward rules, terrain effects, food consumption, and terminal conditions belong in the environment result; the agent applies that result and updates its own state and stats.
- Preserve the split between continuous energy and discrete RL state. The agent stores real energy in `[0, ENERGY_MAX]`, but Q-Learning indexes 4 energy buckets defined by `constants.ENERGY_THRESHOLDS`.
- Scenario wiring is centralized in `src/main.py`: Scenario A swaps in effectively infinite energy, Scenario C passes a relocation switch into `Trainer`, and `WAREHOUSE` delegates fully to `warehouse_scenario.py`.
- `Environment.reset()` is expected to regenerate from the stored seed each episode. Any new environment subclass should keep `reset()` compatible with how `Trainer` calls it before every run.
- Training via `src.main.run_training()` always exports `results_*`, `convergence_*`, `epsilon_*`, and `success_*` artifacts into `data/`. Tests and existing outputs assume that naming pattern.
- Tests are script-style modules, not a repo-configured pytest suite. Prefer `python -m tests.<module>` from the repo root; for single-test granularity, import and call the function directly.
- Comments, docstrings, and user-facing UI strings are mostly Romanian while code identifiers stay English. Keep new UI copy and inline documentation aligned with that mixed style.
- For quick CLI smoke tests, use at least `--episodes 50`; `Analytics.save_all_plots()` uses a 50-episode rolling window and can fail for smaller histories.
