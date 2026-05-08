"""Agregare de metrici pentru comparații Monte Carlo."""


def _avg(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def aggregate_results(results) -> dict:
    grouped: dict[str, list] = {}
    for result in results:
        grouped.setdefault(result.algorithm, []).append(result)

    rows = []
    for algorithm, items in sorted(grouped.items()):
        count = len(items)
        rows.append({
            "algorithm": algorithm,
            "episodes": count,
            "success_rate": _avg(1.0 if item.success else 0.0 for item in items),
            "average_reward": _avg(item.total_reward for item in items),
            "average_steps": _avg(item.steps for item in items),
            "average_collisions": _avg(item.collisions for item in items),
            "collision_rate": _avg(1.0 if item.collisions > 0 else 0.0 for item in items),
            "average_danger_entries": _avg(item.danger_entries for item in items),
            "danger_entry_rate": _avg(1.0 if item.danger_entries > 0 else 0.0 for item in items),
            "average_risk_exposure": _avg(item.total_risk_exposure for item in items),
            "average_total_cost": _avg(item.total_cost for item in items),
            "timeout_rate": _avg(1.0 if item.timeout else 0.0 for item in items),
            "average_computation_time_ms": _avg(item.computation_time_ms for item in items),
        })
    return {"agents": rows, "episode_count": len(results)}
