"""
Entry point: Mod manual (săgeți) sau Mod antrenament Q-Learning.
Utilizare:
    python -m src.main                          # mod manual, grid 20x20
    python -m src.main --train                  # antrenament Scenariul B (default)
    python -m src.main --train --scenario A     # Scenariul A: energie infinită
    python -m src.main --train --scenario C     # Scenariul C: mediu dinamic
    python -m src.main --train --scenario C --alpha-sensitivity  # analiză alpha
    python -m src.main --train --scenario WAREHOUSE  # simulare depozit industrial
    python -m src.main --train --save-qtable data/qt.npy        # salvare Q-Table
    python -m src.main --load-qtable data/qt.npy --visualize    # replay Q-Table salvat
    python -m src.main --train --grid 10 --episodes 1000 --visualize
"""

import sys
import argparse
import pygame

from src.environment import Environment
from src.agent import Agent
from src.renderer import Renderer
from src.q_learning import QLearning
from src.trainer import Trainer
from src.analytics import Analytics
from src.transitions import build_step_feedback
from src.constants import (
    DEFAULT_EPISODES, MAX_STEPS_PER_EPISODE, ENERGY_MAX,
    SCENARIO_C_SWITCH_EPISODE, ALPHA_SENSITIVITY_VALUES,
)


# Mapare taste → acțiuni
KEY_TO_ACTION = {
    pygame.K_UP: 0,
    pygame.K_DOWN: 1,
    pygame.K_LEFT: 2,
    pygame.K_RIGHT: 3,
    pygame.K_SPACE: 4,  # STAY
}

# Energie infinită pentru Scenariul A
ENERGY_INFINITE = 999999


def run_manual(seed=42, grid_size=20):
    """Mod manual — controlezi agentul cu tastele săgeți."""
    env = Environment(rows=grid_size, cols=grid_size, seed=seed)
    agent = Agent(start_pos=env.start_pos)
    renderer = Renderer(rows=grid_size, cols=grid_size)

    running = True
    episode_over = False

    info = {
        "Mod": "Manual",
        "Seed": seed,
        "Grid": f"{env.rows}x{env.cols}",
    }
    last_feedback = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

                elif event.key == pygame.K_r:
                    env.reset(seed=seed)
                    agent.reset(start_pos=env.start_pos)
                    episode_over = False
                    last_feedback = None
                    renderer.reset_visual_state()

                elif event.key == pygame.K_n:
                    seed += 1
                    env.reset(seed=seed)
                    agent.reset(start_pos=env.start_pos)
                    info["Seed"] = seed
                    episode_over = False
                    last_feedback = None
                    renderer.reset_visual_state()

                elif renderer.handle_overlay_event(event):
                    pass

                elif event.key in KEY_TO_ACTION and not episode_over:
                    action = KEY_TO_ACTION[event.key]
                    previous_pos = agent.position
                    result = env.try_move(agent.position, action)
                    reason = agent.apply_action_result(result)
                    last_feedback = build_step_feedback(action, result, previous_pos, reason)
                    info["Reward pas"] = f"{result['reward']:.1f}"
                    info["Actiune"] = action

                    if reason is not None:
                        episode_over = True
                        info["Rezultat"] = reason

        render_info = dict(info)
        if last_feedback is not None:
            render_info["_feedback"] = last_feedback
        renderer.draw(env, agent, render_info)

    renderer.close()


def run_training(seed=42, grid_size=20, num_episodes=DEFAULT_EPISODES,
                  visualize=False, energy=ENERGY_MAX, scenario="B",
                  save_qtable=None, alpha=None, out_dir="data",
                  export_visuals=False, export_trajectory=False):
    """
    Mod antrenament Q-Learning pentru un singur alpha.

    Returns:
        (list[EpisodeResult], QLearning) — istoricul și Q-learner-ul antrenat
    """
    scenario_c_switch = SCENARIO_C_SWITCH_EPISODE if scenario == "C" else None

    env = Environment(rows=grid_size, cols=grid_size, seed=seed)
    q = QLearning(rows=grid_size, cols=grid_size,
                  alpha=alpha if alpha is not None else 0.1)
    trainer = Trainer(env, q, energy=energy)

    renderer = None
    render_cb = None
    overlay_frames = [0]

    if visualize:
        renderer = Renderer(rows=grid_size, cols=grid_size, human_paced=True)

        def render_cb(env, agent, info):
            nonlocal overlay_frames
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_q
                ):
                    if renderer:
                        renderer.close()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    renderer.handle_ui_event(event)

            renderer.draw(env, agent, info, q_learner=q)
            if not renderer.wait_for_playback(env, agent, info, q_learner=q):
                renderer.close()
                sys.exit()

            # End-of-episode overlay
            done = not agent.is_alive or agent.reached_target
            if done and info.get("_episode_done"):
                if overlay_frames[0] < 90:
                    outcome = info.get("_terminal_reason") or (
                        "target_reached" if agent.reached_target else "energy_depleted"
                    )
                    renderer.draw_episode_end_overlay(outcome)
                    overlay_frames[0] += 1
                else:
                    overlay_frames[0] = 0

    print(f"=== Antrenament Q-Learning — Scenariul {scenario} ===")
    print(f"Grid: {grid_size}x{grid_size} | Seed: {seed} | Episoade: {num_episodes}")
    print(f"Energie: {'∞' if energy == ENERGY_INFINITE else energy} | "
          f"Max pași/episod: {MAX_STEPS_PER_EPISODE}")
    print(f"Q-Table: {q.get_state_count()} stări × {q.num_actions} acțiuni "
          f"= {q.get_state_count() * q.num_actions} intrări")
    if scenario == "C":
        print(f"[Scenariul C] Relocare obstacole după episodul {scenario_c_switch}")
    print()

    history = trainer.train(
        num_episodes=num_episodes,
        print_every=max(1, num_episodes // 20),
        render_callback=render_cb,
        scenario_c_switch=scenario_c_switch,
    )

    # Evaluare finală — episod greedy
    print()
    print("=== Evaluare Greedy (fără explorare) ===")
    agent, outcome, greedy_trajectory = trainer.run_greedy_trajectory()
    print(f"Rezultat: {outcome}")
    print(f"Pași: {agent.total_steps} | Reward: {agent.total_reward:.1f} | "
          f"Energie rămasă: {agent.energy:.0f}")

    # Statistici finale
    last_100 = history[-min(100, len(history)):]
    avg_reward = sum(r.total_reward for r in last_100) / len(last_100)
    successes = sum(1 for r in last_100 if r.outcome == "target_reached")
    print(f"\nMedia ultimelor {len(last_100)} episoade: "
          f"Reward={avg_reward:.1f} | Success={successes}/{len(last_100)}")
    print(f"Q-Table: {q.get_nonzero_count()} intrări nenule "
          f"din {q.get_state_count() * q.num_actions}")

    # Salvare Q-Table
    if save_qtable:
        q.save(save_qtable)
        print(f"\nQ-Table salvată: {save_qtable}")

    # Export CSV + grafice
    analytics = Analytics(scenario=scenario, grid_size=grid_size, seed=seed, out_dir=out_dir)
    artifacts = {}
    if save_qtable:
        artifacts["qtable_path"] = save_qtable
    csv_path = analytics.export_csv(history)
    artifacts["results_csv"] = csv_path
    print(f"CSV exportat: {csv_path}")
    plot_paths = analytics.save_all_plots(history)
    for p in plot_paths:
        print(f"Grafic salvat: {p}")
    artifacts.update({
        "convergence_png": plot_paths[0],
        "epsilon_png": plot_paths[1],
        "success_png": plot_paths[2],
    })

    bfs_dist = env.bfs(env.start_pos, env.target_pos)
    greedy_summary = {
        "outcome": outcome,
        "steps": agent.total_steps,
        "reward": agent.total_reward,
        "energy_remaining": agent.energy,
        "bfs_distance": bfs_dist,
        "bfs_overhead": agent.total_steps - bfs_dist if bfs_dist is not None else None,
    }
    if export_trajectory:
        trajectory_csv, trajectory_json = analytics.export_greedy_trajectory(
            greedy_trajectory,
            summary=greedy_summary,
        )
        artifacts["greedy_trajectory_csv"] = trajectory_csv
        artifacts["greedy_trajectory_json"] = trajectory_json
        print(f"Traseu greedy CSV: {trajectory_csv}")
        print(f"Traseu greedy JSON: {trajectory_json}")
    if export_visuals:
        visual_paths = analytics.save_visual_artifacts(
            env,
            q,
            trajectory=greedy_trajectory,
            energy_level=3,
        )
        artifacts.update(visual_paths)
        for p in visual_paths.values():
            print(f"Vizualizare salvată: {p}")
    manifest_path = analytics.export_run_manifest(
        history,
        env,
        q,
        artifacts=artifacts,
        greedy_summary=greedy_summary,
        energy=energy,
    )
    print(f"Manifest rulare: {manifest_path}")

    # Replay greedy vizual
    if renderer:
        _run_greedy_replay(env, q, energy, renderer)

    return history, q


def _run_greedy_replay(env, q, energy, renderer):
    """Replay greedy cu vizualizare după antrenament."""
    print("\n[Replay greedy vizual — apasă Q pentru a ieși]")
    env.reset()
    agent = Agent(start_pos=env.start_pos, energy=energy)
    state = agent.get_state()
    running = True
    last_feedback = None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                renderer.handle_ui_event(event)

        if not running:
            break

        if agent.is_alive and not agent.reached_target:
            action = q.get_best_action(state)
            previous_pos = agent.position
            result = env.try_move(agent.position, action)
            reason = agent.apply_action_result(result)
            state = agent.get_state()
            last_feedback = build_step_feedback(action, result, previous_pos, reason)

        info = {
            "Mod": "Replay Greedy",
            "Pasi": agent.total_steps,
            "Reward": f"{agent.total_reward:.1f}",
        }
        if agent.reached_target:
            info["Status"] = "VICTORIE!"
        elif not agent.is_alive:
            info["Status"] = "DECEDAT"
        if last_feedback is not None:
            info["Actiune"] = last_feedback["action"]
            info["Reward pas"] = f"{last_feedback['reward']:.1f}"
            info["_feedback"] = last_feedback

        renderer.draw(env, agent, info, q_learner=q)
        if not renderer.wait_for_playback(env, agent, info, q_learner=q):
            running = False

    renderer.close()


def run_alpha_sensitivity(seed=42, grid_size=20, num_episodes=DEFAULT_EPISODES):
    """
    Rulează antrenament de 3 ori cu alpha diferit (Scenariul C) și generează grafic comparativ.
    """
    print("=== Analiză Sensibilitate Alpha — Scenariul C ===")
    histories = {}

    for alpha in ALPHA_SENSITIVITY_VALUES:
        print(f"\n--- Alpha = {alpha} ---")
        history, _ = run_training(
            seed=seed, grid_size=grid_size, num_episodes=num_episodes,
            visualize=False, energy=ENERGY_MAX, scenario="C", alpha=alpha,
        )
        histories[alpha] = history

    analytics = Analytics(scenario="C", grid_size=grid_size, seed=seed)
    comparison_path = analytics.plot_alpha_comparison(histories)
    print(f"\nGrafic comparativ alpha salvat: {comparison_path}")


def run_load_and_visualize(qtable_path, seed=42, grid_size=20, energy=ENERGY_MAX):
    """Încarcă un Q-Table salvat și rulează replay greedy vizual."""
    env = Environment(rows=grid_size, cols=grid_size, seed=seed)
    q = QLearning(rows=grid_size, cols=grid_size)
    q.load(qtable_path)
    print(f"Q-Table încărcată din: {qtable_path}")
    renderer = Renderer(rows=grid_size, cols=grid_size, human_paced=True)
    _run_greedy_replay(env, q, energy, renderer)


def main():
    parser = argparse.ArgumentParser(description="Simulare Q-Learning: Navigare Autonomă")
    parser.add_argument("--train", action="store_true", help="Mod antrenament Q-Learning")
    parser.add_argument("--grid", type=int, default=20, help="Dimensiune grid (NxN)")
    parser.add_argument("--seed", type=int, default=42, help="Seed pentru generare hartă")
    parser.add_argument("--episodes", type=int, default=DEFAULT_EPISODES,
                        help="Număr episoade de antrenament")
    parser.add_argument("--visualize", action="store_true",
                        help="Vizualizare în timp real (mai lent)")
    parser.add_argument("--energy", type=int, default=None,
                        help="Energie inițială agent (default: depinde de scenariu)")
    parser.add_argument("--scenario", choices=["A", "B", "C", "WAREHOUSE"], default="B",
                        help="Scenariu: A=navigare pură, B=supraviețuire (default), C=mediu dinamic, WAREHOUSE=depozit industrial")
    parser.add_argument("--save-qtable", metavar="PATH",
                        help="Salvează Q-Table după antrenament la calea specificată")
    parser.add_argument("--load-qtable", metavar="PATH",
                        help="Încarcă Q-Table din fișier și rulează replay greedy")
    parser.add_argument("--alpha-sensitivity", action="store_true",
                        help="Analiză sensibilitate alpha pentru Scenariul C")
    parser.add_argument("--out-dir", default="data",
                        help="Directorul unde se salvează artefactele")
    parser.add_argument("--export-visuals", action="store_true",
                        help="Exportă harta, policy, Q heatmap, visits, TD și traseu greedy ca PNG")
    parser.add_argument("--export-trajectory", action="store_true",
                        help="Exportă traseul greedy final ca CSV + JSON")
    args = parser.parse_args()

    # Scenariul A = energie infinită
    if args.scenario == "A":
        energy = ENERGY_INFINITE
    elif args.energy is not None:
        energy = args.energy
    else:
        energy = ENERGY_MAX

    # Scenariul WAREHOUSE — delegat către modulul dedicat
    if args.scenario == "WAREHOUSE":
        from src.warehouse_scenario import run_warehouse_training
        run_warehouse_training(
            num_episodes=args.episodes,
            visualize=args.visualize,
            out_dir=args.out_dir,
            export_visuals=args.export_visuals,
            export_trajectory=args.export_trajectory,
        )
        return

    # Replay din Q-Table salvat
    if args.load_qtable:
        run_load_and_visualize(
            qtable_path=args.load_qtable,
            seed=args.seed,
            grid_size=args.grid,
            energy=energy,
        )
        return

    # Analiză sensibilitate alpha (Scenariul C)
    if args.alpha_sensitivity:
        run_alpha_sensitivity(
            seed=args.seed,
            grid_size=args.grid,
            num_episodes=args.episodes,
        )
        return

    if args.train:
        run_training(
            seed=args.seed,
            grid_size=args.grid,
            num_episodes=args.episodes,
            visualize=args.visualize,
            energy=energy,
            scenario=args.scenario,
            save_qtable=args.save_qtable,
            out_dir=args.out_dir,
            export_visuals=args.export_visuals,
            export_trajectory=args.export_trajectory,
        )
    else:
        run_manual(seed=args.seed, grid_size=args.grid)


if __name__ == "__main__":
    main()
