"""Motor generic de simulare care rulează orice BaseAgent."""

import time

from simulation.episode_result import EpisodeResult, Transition


class Simulator:
    def __init__(self, environment, agent, max_steps: int = 300):
        self.environment = environment
        self.agent = agent
        self.max_steps = max_steps

    def run_episode(self, training: bool = False) -> EpisodeResult:
        observation = self.environment.reset()
        self.agent.reset()
        total_reward = 0.0
        collisions = 0
        danger_entries = 0
        path = [observation["position"]]
        events = []
        reached_goal = False
        timeout = False
        started = time.perf_counter()

        for step_index in range(self.max_steps):
            state = self.agent.state_key(observation) if hasattr(self.agent, "state_key") else observation["position"]
            action = self.agent.select_action(observation)
            next_observation, reward, done, info = self.environment.step(action)
            next_state = (
                self.agent.state_key(next_observation)
                if hasattr(self.agent, "state_key")
                else next_observation["position"]
            )
            transition = Transition(
                state=state,
                action=int(action),
                reward=reward,
                next_state=next_state,
                done=done,
                info=info,
            )
            if training:
                self.agent.learn(transition)

            total_reward += reward
            collisions += int(bool(info.get("collision")))
            danger_entries += int(bool(info.get("entered_danger")))
            reached_goal = bool(info.get("reached_goal"))
            path.append(info["current_position"])
            events.append({
                "step": step_index + 1,
                "event_type": info["event_type"],
                "position": list(info["current_position"]),
                "reward": reward,
                "risk_cost": info["risk_cost"],
                "action": info["executed_action"],
                "requested_action": info["requested_action"],
                "distance_to_goal": info["distance_to_goal"],
            })
            observation = next_observation
            if done:
                break
        else:
            timeout = True

        if training and hasattr(self.agent, "end_episode"):
            self.agent.end_episode()

        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return EpisodeResult(
            algorithm=self.agent.name,
            success=reached_goal,
            total_reward=total_reward,
            steps=len(path) - 1,
            collisions=collisions,
            danger_entries=danger_entries,
            total_risk_exposure=self.environment.total_risk_exposure,
            path=path,
            reached_goal=reached_goal,
            timeout=timeout,
            events=events,
            computation_time_ms=elapsed_ms,
        )
