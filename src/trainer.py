"""
Bucla de antrenament Q-Learning: rulează episoade, colectează metrici, apelul Q-update.

NOTĂ: clasa ``EpisodeResult`` definită aici aparține stivei legacy de Q-Learning
cu energie și nu trebuie confundată cu ``simulation.episode_result.EpisodeResult``
folosită de pipeline-ul safe-navigation / Monte Carlo. Cele două sunt complet
independente; importați direct din modulul corect.
"""

import random
from dataclasses import dataclass, field

from src.environment import Environment, CellType
from src.agent import Agent
from src.q_learning import QLearning
from src.constants import (
    MAX_STEPS_PER_EPISODE, DEFAULT_EPISODES, ENERGY_MAX,
    SCENARIO_C_SWITCH_EPISODE, SCENARIO_C_OBSTACLE_RELOCATE_FRACTION,
)
from src.transitions import build_step_feedback, is_collision


__all__ = ["EpisodeResult", "Trainer"]


@dataclass(slots=True)
class EpisodeResult:
    """Rezultatul unui episod legacy (energie, food, mud, scenariile A/B/C)."""
    episode_id: int
    total_steps: int
    total_reward: float
    epsilon: float
    outcome: str
    coverage: float
    energy_remaining: float
    collisions: int = 0
    food_collected: int = 0
    mud_steps: int = 0
    danger_entries: int = 0
    energy_spent: float = 0.0
    energy_gained: float = 0.0
    action_counts: list[int] = field(default_factory=lambda: [0, 0, 0, 0, 0])
    mean_abs_td: float = 0.0
    q_nonzero: int = 0
    q_fill_pct: float = 0.0

    def __post_init__(self):
        self.action_counts = list(self.action_counts)


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
        self._reset_grid = None
        self._reset_start_pos = None
        self._reset_target_pos = None
        self.last_training_event = None

    def _build_render_info(self, episode_id, step, agent, action, result, reason,
                           live_metrics=None):
        """Construiește payload-ul trimis renderer-ului pentru feedback live."""
        previous_pos = result["previous_pos"]
        recent = self.history[-50:]
        avg_reward = (
            sum(item.total_reward for item in recent) / len(recent)
            if recent else agent.total_reward
        )
        success_rate = (
            sum(1 for item in recent if item.outcome == "target_reached") / len(recent) * 100
            if recent else 0.0
        )
        last_update = self.q.get_last_update()
        knowledge = self.q.get_knowledge_stats()
        live_metrics = live_metrics or {}
        energy_delta = result["energy_gain"] - result["energy_cost"]

        return {
            "Episod": episode_id,
            "Pas": step,
            "Progres ep": f"{min(100, (step + 1) / self.max_steps * 100):.0f}%",
            "Epsilon": f"{self.q.epsilon:.3f}",
            "Actiune": action,
            "Reward pas": f"{result['reward']:.1f}",
            "Delta energie": f"{energy_delta:+.0f}",
            "Medie 50 ep": f"{avg_reward:.1f}",
            "Success 50 ep": f"{success_rate:.1f}%",
            "Eveniment": self.last_training_event,
            "_feedback": build_step_feedback(action, result, previous_pos, reason),
            "_learning": {
                "last_update": last_update,
                "knowledge": knowledge,
                "history": self.history,
            },
            "_live": {
                "step": step,
                "max_steps": self.max_steps,
                "progress": min(1.0, (step + 1) / self.max_steps),
                "action_counts": live_metrics.get("action_counts", [0, 0, 0, 0, 0]),
                "collisions": live_metrics.get("collisions", 0),
                "food_collected": live_metrics.get("food_collected", 0),
                "mud_steps": live_metrics.get("mud_steps", 0),
                "energy_spent": live_metrics.get("energy_spent", 0.0),
                "energy_gained": live_metrics.get("energy_gained", 0.0),
            },
            "_episode_done": reason is not None,
            "_terminal_reason": reason,
        }

    def _reset_environment_for_episode(self):
        """
        Resetează mediul la configurația de bază a episodului.

        În mod normal, Environment.reset() regenerează harta din seed-ul stocat.
        Pentru Scenariul C, după relocarea obstacolelor, episoadele viitoare trebuie
        să pornească din aceeași configurație relocată, nu din harta inițială.
        """
        if self._reset_grid is None:
            self.env.reset()
            return

        self.env.grid = [row[:] for row in self._reset_grid]
        self.env.start_pos = self._reset_start_pos
        self.env.target_pos = self._reset_target_pos

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
        self._reset_environment_for_episode()
        agent = Agent(start_pos=self.env.start_pos, energy=self.energy)

        state = agent.get_state()
        outcome = "timeout"
        action_counts = [0 for _ in range(self.q.num_actions)]
        collisions = 0
        food_collected = 0
        mud_steps = 0
        danger_entries = 0
        energy_spent = 0.0
        energy_gained = 0.0
        td_abs_total = 0.0
        q_updates = 0

        for step in range(self.max_steps):
            # 1. Alege acțiune (epsilon-greedy)
            action = self.q.choose_action(state)
            action_counts[action] += 1

            # 2. Execută acțiunea în mediu
            previous_pos = agent.position
            result = self.env.try_move(agent.position, action)
            cell_type = result.get("cell_type")
            if is_collision(action, result, previous_pos):
                collisions += 1
            if cell_type == CellType.FOOD and result["energy_gain"] > 0:
                food_collected += 1
            if cell_type == CellType.MUD and result["new_pos"] != previous_pos:
                mud_steps += 1
            if result["terminal_reason"] == "danger":
                danger_entries += 1
            energy_spent += result["energy_cost"]
            energy_gained += result["energy_gain"]

            # 3. Aplică rezultatul asupra agentului
            reason = agent.apply_action_result(result)

            # 4. Observă noua stare
            next_state = agent.get_state()

            # 5. Determină dacă episodul s-a terminat
            done = reason is not None

            # 6. Q-update (Bellman)
            td_error = self.q.update(state, action, result["reward"], next_state, done)
            td_abs_total += abs(td_error)
            q_updates += 1

            # Opțional: render
            if render_callback is not None:
                info = self._build_render_info(
                    episode_id=episode_id,
                    step=step,
                    agent=agent,
                    action=action,
                    result={**result, "previous_pos": previous_pos},
                    reason=reason,
                    live_metrics={
                        "action_counts": action_counts,
                        "collisions": collisions,
                        "food_collected": food_collected,
                        "mud_steps": mud_steps,
                        "energy_spent": energy_spent,
                        "energy_gained": energy_gained,
                    },
                )
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
        q_nonzero = self.q.get_nonzero_count()
        q_total = self.q.q_table.size
        mean_abs_td = td_abs_total / q_updates if q_updates else 0.0

        result = EpisodeResult(
            episode_id=episode_id,
            total_steps=agent.total_steps,
            total_reward=agent.total_reward,
            epsilon=self.q.epsilon,
            outcome=outcome,
            coverage=coverage,
            energy_remaining=agent.energy,
            collisions=collisions,
            food_collected=food_collected,
            mud_steps=mud_steps,
            danger_entries=danger_entries,
            energy_spent=energy_spent,
            energy_gained=energy_gained,
            action_counts=action_counts,
            mean_abs_td=mean_abs_td,
            q_nonzero=q_nonzero,
            q_fill_pct=(q_nonzero / q_total * 100) if q_total else 0.0,
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
                self._reset_grid = [row[:] for row in env.grid]
                self._reset_start_pos = env.start_pos
                self._reset_target_pos = env.target_pos
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
        self.last_training_event = None

        for ep in range(num_episodes):
            # Scenariul C: relocă obstacolele o singură dată după episodul N
            if (scenario_c_switch is not None
                    and not obstacle_relocated
                    and ep == scenario_c_switch):
                success = self._relocate_obstacles(self.env)
                obstacle_relocated = True
                if success:
                    self.last_training_event = f"Obstacole relocate la ep. {ep}"
                    print(f"[Scenariul C] Obstacole relocate după episodul {ep}.")
                else:
                    self.last_training_event = f"Relocare eșuată la ep. {ep}"
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
        agent, outcome, _ = self.run_greedy_trajectory()
        return agent, outcome

    def run_greedy_trajectory(self):
        """
        Rulează un episod greedy și returnează și traseul pas-cu-pas.

        Returns:
            (Agent, str, list[dict]) — agentul final, outcome și tranzițiile greedy
        """
        self._reset_environment_for_episode()
        agent = Agent(start_pos=self.env.start_pos, energy=self.energy)
        state = agent.get_state()
        outcome = "timeout"
        trajectory = []

        for step in range(self.max_steps):
            action = self.q.get_best_action(state)
            previous_pos = agent.position
            result = self.env.try_move(agent.position, action)
            reason = agent.apply_action_result(result)
            row, col = agent.position
            prev_row, prev_col = previous_pos
            cell_type = result.get("cell_type")
            trajectory.append({
                "step": step,
                "previous_row": prev_row,
                "previous_col": prev_col,
                "row": row,
                "col": col,
                "energy": agent.energy,
                "reward": result["reward"],
                "total_reward": agent.total_reward,
                "action": action,
                "cell_type": cell_type.name if hasattr(cell_type, "name") else str(cell_type),
                "terminal_reason": reason,
            })

            if reason is not None:
                outcome = reason
                break

            state = agent.get_state()

        return agent, outcome, trajectory
