"""
Serializare JSON pentru medii, Q-table și evenimente de simulare.
"""

from src.environment import CellType


def serialize_position(position):
    return [int(position[0]), int(position[1])]


def serialize_grid(environment):
    return [
        [int(CellType(cell)) for cell in row]
        for row in environment.grid
    ]


def cell_counts(environment):
    counts = {cell.name: 0 for cell in CellType}
    for row in environment.grid:
        for cell in row:
            counts[CellType(cell).name] += 1
    return counts


def serialize_environment(environment, environment_id=None, name=None):
    return {
        "id": environment_id,
        "name": name or getattr(environment, "name", None),
        "rows": environment.rows,
        "cols": environment.cols,
        "seed": getattr(environment, "seed", None),
        "start": serialize_position(environment.start_pos),
        "target": serialize_position(environment.target_pos),
        "bfs_distance": environment.bfs(environment.start_pos, environment.target_pos),
        "cell_counts": cell_counts(environment),
        "grid": serialize_grid(environment),
    }


def serialize_episode_result(result):
    return {
        "episode_id": result.episode_id,
        "steps": result.total_steps,
        "total_reward": result.total_reward,
        "epsilon": result.epsilon,
        "outcome": result.outcome,
        "coverage_pct": result.coverage,
        "energy_remaining": result.energy_remaining,
        "collisions": result.collisions,
        "food_collected": result.food_collected,
        "mud_steps": result.mud_steps,
        "danger_entries": result.danger_entries,
        "energy_spent": result.energy_spent,
        "energy_gained": result.energy_gained,
        "action_counts": list(result.action_counts),
        "mean_abs_td": result.mean_abs_td,
        "q_nonzero": result.q_nonzero,
        "q_fill_pct": result.q_fill_pct,
    }


def serialize_q_stats(q_learner):
    stats = q_learner.get_knowledge_stats()
    return {
        **stats,
        "shape": list(q_learner.q_table.shape),
        "epsilon": q_learner.epsilon,
        "alpha": q_learner.alpha,
        "gamma": q_learner.gamma,
    }


def serialize_live_info(info):
    """Curăță payload-ul Trainer pentru JSON/API."""
    if not info:
        return {}
    payload = {
        key: value
        for key, value in info.items()
        if not key.startswith("_")
    }
    payload["feedback"] = info.get("_feedback", {})
    payload["learning"] = {
        "last_update": info.get("_learning", {}).get("last_update"),
        "knowledge": info.get("_learning", {}).get("knowledge", {}),
    }
    payload["live"] = info.get("_live", {})
    payload["episode_done"] = info.get("_episode_done", False)
    payload["terminal_reason"] = info.get("_terminal_reason")
    return payload
