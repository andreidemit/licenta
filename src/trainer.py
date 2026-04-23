"""
Bucla de antrenament Q-Learning: rulează episoade, colectează metrici, apelul Q-update.
"""

import random

from src.environment import Environment, CellType
from src.agent import Agent
from src.q_learning import QLearning
from src.constants import (
    MAX_STEPS_PER_EPISODE, DEFAULT_EPISODES, ENERGY_MAX,
    SCENARIO_C_SWITCH_EPISODE, SCENARIO_C_OBSTACLE_RELOCATE_FRACTION,
)


class EpisodeResult:
    """Rezultatul unui singur episod de antrenament."""
    __slots__ = ("episode_id", "total_steps", "total_reward", "epsilon",
                 "outcome", "coverage", "energy_remaining")

    def __init__(self, episode_id, total_steps, total_reward, epsilon,
                 outcome, coverage, energy_remaining):
        self.episode_id = episode_id
        self.total_steps = total_steps
        self.total_reward = total_reward
        self.epsilon = epsilon
        self.outcome = outcome
        self.coverage = coverage
        self.energy_remaining = energy_remaining


class Trainer:
    """
    Orchestrează antrenamentul Q-Learning.

    Rulează N episoade: în fiecare, agentul interacționează cu mediul,
    Q-Table se actualizează, iar la final epsilon descresce.
    """

    def __init__(self, env, q_learner, energy=ENERGY_MAX,
                 max_steps=MAX_STEPS_PER_EPISODE):
        self.env = env
        self.q = q_learner
        self.energy = energy
        self.max_steps = max_steps
        self.history = []  # lista EpisodeResult

    def run_episode(self, episode_id, render_callback=None):
        """
        Rulează un singur episod de antrenament.

        Args:
            episode_id: int — indexul episodului
            render_callback: opțional, funcție(env, agent, info) apelată la fiecare pas

        Returns:
            EpisodeResult
        """
        # Reset mediu și agent
        self.env.reset()
        agent = Agent(start_pos=self.env.start_pos, energy=self.energy)

        state = agent.get_state()
        outcome = "timeout"

        for step in range(self.max_steps):
            # 1. Alege acțiune (epsilon-greedy)
            action = self.q.choose_action(state)

            # 2. Execută acțiunea în mediu
            result = self.env.try_move(agent.position, action)

            # 3. Aplică rezultatul asupra agentului
            reason = agent.apply_action_result(result)

            # 4. Observă noua stare
            next_state = agent.get_state()

            # 5. Determină dacă episodul s-a terminat
            done = reason is not None

            # 6. Q-update (Bellman)
            self.q.update(state, action, result["reward"], next_state, done)

            # Opțional: render
            if render_callback is not None:
                info = {
                    "Episod": episode_id,
                    "Pas": step,
                    "Epsilon": f"{self.q.epsilon:.3f}",
                    "Actiune": action,
                }
                render_callback(self.env, agent, info)

            if done:
                outcome = reason
                break

            state = next_state

        # Decay epsilon la finalul episodului
        self.q.decay_epsilon()

        # Construiește rezultatul
        total_cells = self.env.rows * self.env.cols
        coverage = agent.coverage / total_cells * 100

        result = EpisodeResult(
            episode_id=episode_id,
            total_steps=agent.total_steps,
            total_reward=agent.total_reward,
            epsilon=self.q.epsilon,
            outcome=outcome,
            coverage=coverage,
            energy_remaining=agent.energy,
        )
        self.history.append(result)
        return result

    def _relocate_obstacles(self, env) -> bool:
        """
        Mută o fracțiune din obstacole în celule goale aleatorii (Scenariul C).
        Re-validează harta cu BFS; încearcă de max 10 ori înainte să renunțe.

        Returns:
            bool — True dacă relocarea a reușit, False dacă toate încercările au eșuat
        """
        obstacles = [
            (r, c)
            for r in range(env.rows)
            for c in range(env.cols)
            if env.grid[r][c] == CellType.OBSTACLE
        ]
        if not obstacles:
            return False

        n_move = max(1, int(len(obstacles) * SCENARIO_C_OBSTACLE_RELOCATE_FRACTION))

        for _ in range(10):
            chosen = random.sample(obstacles, min(n_move, len(obstacles)))

            empty_cells = [
                (r, c)
                for r in range(env.rows)
                for c in range(env.cols)
                if env.grid[r][c] == CellType.EMPTY
                and (r, c) != env.start_pos
                and (r, c) != env.target_pos
            ]
            if len(empty_cells) < len(chosen):
                continue

            new_positions = random.sample(empty_cells, len(chosen))

            # Aplică mutarea temporar
            for r, c in chosen:
                env.grid[r][c] = CellType.EMPTY
            for r, c in new_positions:
                env.grid[r][c] = CellType.OBSTACLE

            if env._validate_path():
                return True

            # Revine dacă harta e invalidă
            for r, c in chosen:
                env.grid[r][c] = CellType.OBSTACLE
            for r, c in new_positions:
                env.grid[r][c] = CellType.EMPTY

        return False

    def train(self, num_episodes=DEFAULT_EPISODES, print_every=100,
              render_callback=None, scenario_c_switch=None):
        """
        Rulează antrenamentul complet: N episoade.

        Args:
            num_episodes: int — numărul de episoade
            print_every: int — afișează progres la fiecare N episoade (0 = fără print)
            render_callback: opțional, funcție de rendering per pas
            scenario_c_switch: int sau None — episodul după care se relocă obstacolele (Scenariul C)

        Returns:
            list[EpisodeResult] — istoricul complet
        """
        obstacle_relocated = False

        for ep in range(num_episodes):
            # Scenariul C: relocă obstacolele o singură dată după episodul N
            if (scenario_c_switch is not None
                    and not obstacle_relocated
                    and ep == scenario_c_switch):
                success = self._relocate_obstacles(self.env)
                obstacle_relocated = True
                if success:
                    print(f"[Scenariul C] Obstacole relocate după episodul {ep}.")
                else:
                    print(f"[Scenariul C] Relocare eșuată după {ep} episoade — harta rămâne neschimbată.")

            result = self.run_episode(ep, render_callback=render_callback)

            if print_every > 0 and (ep + 1) % print_every == 0:
                # Calculăm media pe ultimele `print_every` episoade
                recent = self.history[-print_every:]
                avg_reward = sum(r.total_reward for r in recent) / len(recent)
                avg_steps = sum(r.total_steps for r in recent) / len(recent)
                successes = sum(1 for r in recent if r.outcome == "target_reached")
                success_rate = successes / len(recent) * 100

                print(
                    f"Ep {ep + 1:5d}/{num_episodes} | "
                    f"Avg Reward: {avg_reward:7.1f} | "
                    f"Avg Steps: {avg_steps:5.1f} | "
                    f"Success: {success_rate:5.1f}% | "
                    f"Epsilon: {self.q.epsilon:.4f}"
                )

        return self.history

    def run_greedy_episode(self):
        """
        Rulează un episod cu politica greedy (fără explorare).
        Util pentru evaluare post-antrenament.

        Returns:
            (Agent, str) — agentul final și outcome
        """
        self.env.reset()
        agent = Agent(start_pos=self.env.start_pos, energy=self.energy)
        state = agent.get_state()
        outcome = "timeout"

        for step in range(self.max_steps):
            action = self.q.get_best_action(state)
            result = self.env.try_move(agent.position, action)
            reason = agent.apply_action_result(result)

            if reason is not None:
                outcome = reason
                break

            state = agent.get_state()

        return agent, outcome
