"""Verificări pentru statisticile extinse din simulation.metrics."""

from simulation.episode_result import EpisodeResult
from simulation.metrics import aggregate_results


def _make_episode(algorithm: str, *, success: bool, reward: float, steps: int,
                  risk: float, collisions: int = 0, danger: int = 0,
                  timeout: bool = False, map_seed: int | None = None) -> EpisodeResult:
    return EpisodeResult(
        algorithm=algorithm,
        success=success,
        total_reward=reward,
        steps=steps,
        collisions=collisions,
        danger_entries=danger,
        total_risk_exposure=risk,
        path=[(0, 0)] * (steps + 1),
        reached_goal=success,
        timeout=timeout,
        events=[],
        computation_time_ms=1.0,
        map_seed=map_seed,
    )


def test_aggregate_results_includes_distributions_and_ci():
    episodes = [
        _make_episode("astar", success=True, reward=10.0, steps=5, risk=0.0, map_seed=1),
        _make_episode("astar", success=True, reward=12.0, steps=6, risk=0.5, map_seed=1),
        _make_episode("astar", success=False, reward=-5.0, steps=20, risk=2.0, timeout=True, map_seed=2),
        _make_episode("astar", success=True, reward=11.0, steps=4, risk=0.3, map_seed=2),
    ]

    summary = aggregate_results(episodes)
    assert summary["episode_count"] == 4
    assert len(summary["agents"]) == 1

    row = summary["agents"][0]
    assert row["algorithm"] == "astar"
    assert "reward_distribution" in row
    assert "steps_distribution" in row
    assert "risk_distribution" in row

    distribution = row["reward_distribution"]
    for key in ("mean", "std", "p05", "p25", "p50", "p75", "p95",
                "ci95_low", "ci95_high", "min", "max"):
        assert key in distribution

    assert distribution["min"] == -5.0
    assert distribution["max"] == 12.0
    assert distribution["p50"] >= -5.0
    assert distribution["p50"] <= 12.0
    assert distribution["std"] > 0
    assert distribution["ci95_low"] <= row["average_reward"] <= distribution["ci95_high"]

    assert row["success_rate_ci95_low"] <= row["success_rate"] <= row["success_rate_ci95_high"]
    assert 0.0 <= row["success_rate"] <= 1.0


def test_aggregate_results_per_map_breakdown():
    episodes = [
        _make_episode("astar", success=True, reward=10, steps=5, risk=0.0, map_seed=1),
        _make_episode("astar", success=False, reward=-1, steps=10, risk=1.0, map_seed=1),
        _make_episode("astar", success=True, reward=8, steps=6, risk=0.0, map_seed=2),
        _make_episode("rule_based", success=False, reward=-5, steps=20, risk=2.0, map_seed=1),
    ]

    summary = aggregate_results(episodes)
    per_map = summary["per_map"]
    assert len(per_map) == 3
    keys = {(item["map_seed"], item["algorithm"]) for item in per_map}
    assert keys == {(1, "astar"), (1, "rule_based"), (2, "astar")}

    astar_map_one = next(item for item in per_map if item["algorithm"] == "astar" and item["map_seed"] == 1)
    assert astar_map_one["episodes"] == 2
    assert astar_map_one["success_rate"] == 0.5


def test_aggregate_results_handles_missing_map_seed():
    episodes = [
        _make_episode("astar", success=True, reward=1.0, steps=3, risk=0.0),
        _make_episode("astar", success=True, reward=1.0, steps=3, risk=0.0),
    ]
    summary = aggregate_results(episodes)
    assert summary["per_map"] == []
    assert summary["agents"][0]["episodes"] == 2


if __name__ == "__main__":
    test_aggregate_results_includes_distributions_and_ci()
    test_aggregate_results_per_map_breakdown()
    test_aggregate_results_handles_missing_map_seed()
    print("OK")
