"""Agregare de metrici pentru comparații Monte Carlo."""

from __future__ import annotations

import math
import random
from typing import Iterable, Sequence


_BOOTSTRAP_SAMPLES = 1000
_BOOTSTRAP_SEED = 1234


def _avg(values):
    values = list(values)
    return sum(values) / len(values) if values else 0.0


def _std(values: Sequence[float]) -> float:
    n = len(values)
    if n < 2:
        return 0.0
    mean = sum(values) / n
    variance = sum((value - mean) ** 2 for value in values) / (n - 1)
    return math.sqrt(variance)


def _percentile(sorted_values: Sequence[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    rank = pct / 100.0 * (len(sorted_values) - 1)
    lower_index = int(math.floor(rank))
    upper_index = int(math.ceil(rank))
    if lower_index == upper_index:
        return float(sorted_values[lower_index])
    weight = rank - lower_index
    return float(sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight)


def _bootstrap_ci(values: Sequence[float], confidence: float = 0.95,
                  iterations: int = _BOOTSTRAP_SAMPLES,
                  seed: int = _BOOTSTRAP_SEED) -> tuple[float, float]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(values[0]), float(values[0])
    rng = random.Random(seed)
    means = []
    for _ in range(iterations):
        sample = [values[rng.randrange(n)] for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    alpha = (1 - confidence) / 2
    return _percentile(means, alpha * 100), _percentile(means, (1 - alpha) * 100)


def _distribution_block(values: Iterable[float]) -> dict:
    sample = [float(v) for v in values]
    sorted_sample = sorted(sample)
    mean = sum(sample) / len(sample) if sample else 0.0
    ci_low, ci_high = _bootstrap_ci(sample)
    return {
        "mean": mean,
        "std": _std(sample),
        "p05": _percentile(sorted_sample, 5),
        "p25": _percentile(sorted_sample, 25),
        "p50": _percentile(sorted_sample, 50),
        "p75": _percentile(sorted_sample, 75),
        "p95": _percentile(sorted_sample, 95),
        "ci95_low": ci_low,
        "ci95_high": ci_high,
        "min": min(sample) if sample else 0.0,
        "max": max(sample) if sample else 0.0,
    }


def _per_map_breakdown(results) -> list[dict]:
    grouped: dict[tuple[int, str], list] = {}
    for result in results:
        seed = getattr(result, "map_seed", None)
        if seed is None:
            continue
        grouped.setdefault((seed, result.algorithm), []).append(result)

    breakdown = []
    for (map_seed, algorithm), items in sorted(grouped.items(), key=lambda entry: (entry[0][0], entry[0][1])):
        breakdown.append({
            "map_seed": map_seed,
            "algorithm": algorithm,
            "episodes": len(items),
            "success_rate": _avg(1.0 if item.success else 0.0 for item in items),
            "average_reward": _avg(item.total_reward for item in items),
            "average_steps": _avg(item.steps for item in items),
            "average_risk_exposure": _avg(item.total_risk_exposure for item in items),
            "collision_rate": _avg(1.0 if item.collisions > 0 else 0.0 for item in items),
            "danger_entry_rate": _avg(1.0 if item.danger_entries > 0 else 0.0 for item in items),
            "timeout_rate": _avg(1.0 if item.timeout else 0.0 for item in items),
        })
    return breakdown


def aggregate_results(results) -> dict:
    grouped: dict[str, list] = {}
    for result in results:
        grouped.setdefault(result.algorithm, []).append(result)

    rows = []
    for algorithm, items in sorted(grouped.items()):
        count = len(items)
        rewards = [item.total_reward for item in items]
        steps = [item.steps for item in items]
        risk = [item.total_risk_exposure for item in items]
        success_flags = [1.0 if item.success else 0.0 for item in items]
        collision_flags = [1.0 if item.collisions > 0 else 0.0 for item in items]
        danger_flags = [1.0 if item.danger_entries > 0 else 0.0 for item in items]
        timeout_flags = [1.0 if item.timeout else 0.0 for item in items]

        success_ci_low, success_ci_high = _bootstrap_ci(success_flags)
        collision_ci_low, collision_ci_high = _bootstrap_ci(collision_flags)
        danger_ci_low, danger_ci_high = _bootstrap_ci(danger_flags)
        timeout_ci_low, timeout_ci_high = _bootstrap_ci(timeout_flags)

        rows.append({
            "algorithm": algorithm,
            "episodes": count,
            "success_rate": _avg(success_flags),
            "success_rate_ci95_low": success_ci_low,
            "success_rate_ci95_high": success_ci_high,
            "average_reward": _avg(rewards),
            "average_steps": _avg(steps),
            "average_collisions": _avg(item.collisions for item in items),
            "collision_rate": _avg(collision_flags),
            "collision_rate_ci95_low": collision_ci_low,
            "collision_rate_ci95_high": collision_ci_high,
            "average_danger_entries": _avg(item.danger_entries for item in items),
            "danger_entry_rate": _avg(danger_flags),
            "danger_entry_rate_ci95_low": danger_ci_low,
            "danger_entry_rate_ci95_high": danger_ci_high,
            "average_risk_exposure": _avg(risk),
            "average_total_cost": _avg(item.total_cost for item in items),
            "timeout_rate": _avg(timeout_flags),
            "timeout_rate_ci95_low": timeout_ci_low,
            "timeout_rate_ci95_high": timeout_ci_high,
            "average_computation_time_ms": _avg(item.computation_time_ms for item in items),
            "reward_distribution": _distribution_block(rewards),
            "steps_distribution": _distribution_block(steps),
            "risk_distribution": _distribution_block(risk),
        })
    return {
        "agents": rows,
        "episode_count": len(results),
        "per_map": _per_map_breakdown(results),
    }
