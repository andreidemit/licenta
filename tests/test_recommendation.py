"""Teste pentru motorul de recomandare safe-navigation."""

from experiments.recommendation import build_recommendation


def _row(
    algorithm,
    success,
    risk,
    cost,
    steps,
    collisions=0.0,
    danger=0.0,
    timeout=0.0,
):
    return {
        "algorithm": algorithm,
        "episodes": 10,
        "success_rate": success,
        "success_rate_ci95_low": max(0.0, success - 0.05),
        "success_rate_ci95_high": min(1.0, success + 0.05),
        "average_risk_exposure": risk,
        "average_total_cost": cost,
        "average_steps": steps,
        "collision_rate": collisions,
        "collision_rate_ci95_low": max(0.0, collisions - 0.02),
        "collision_rate_ci95_high": min(1.0, collisions + 0.02),
        "danger_entry_rate": danger,
        "danger_entry_rate_ci95_low": max(0.0, danger - 0.02),
        "danger_entry_rate_ci95_high": min(1.0, danger + 0.02),
        "timeout_rate": timeout,
        "timeout_rate_ci95_low": max(0.0, timeout - 0.02),
        "timeout_rate_ci95_high": min(1.0, timeout + 0.02),
        "average_computation_time_ms": 1.0,
    }


def test_safety_first_prefers_low_risk_over_short_path():
    summary = {
        "agents": [
            _row("A*", success=0.95, risk=30, cost=80, steps=12, collisions=0.05, danger=0.10),
            _row("Risk-Aware A*", success=0.90, risk=4, cost=90, steps=20, collisions=0.0, danger=0.0),
            _row("Random", success=0.35, risk=18, cost=160, steps=45, collisions=0.30, danger=0.25),
        ]
    }

    recommendation = build_recommendation(summary, "safety_first")

    assert recommendation["recommended_algorithm"] == "Risk-Aware A*"
    assert recommendation["ranking"][0]["score"] > recommendation["ranking"][1]["score"]
    assert "risc" in recommendation["explanation"].lower()
    assert recommendation["tradeoffs"]


def test_efficiency_first_prefers_short_low_cost_strategy():
    summary = {
        "agents": [
            _row("A*", success=0.92, risk=20, cost=45, steps=10, collisions=0.05, danger=0.10),
            _row("Risk-Aware A*", success=0.92, risk=3, cost=70, steps=22, collisions=0.0, danger=0.0),
            _row("Feature-Based Q-Learning", success=0.80, risk=8, cost=95, steps=30, collisions=0.05, danger=0.03),
        ]
    }

    recommendation = build_recommendation(summary, "efficiency_first")

    assert recommendation["recommended_algorithm"] == "A*"
    assert [item["rank"] for item in recommendation["ranking"]] == [1, 2, 3]


def test_unknown_objective_falls_back_to_balanced():
    summary = {"agents": [_row("A*", 1.0, 1, 10, 8)]}

    recommendation = build_recommendation(summary, "not_real")

    assert recommendation["objective"] == "balanced"
    assert recommendation["recommended_algorithm"] == "A*"


if __name__ == "__main__":
    test_safety_first_prefers_low_risk_over_short_path()
    test_efficiency_first_prefers_short_low_cost_strategy()
    test_unknown_objective_falls_back_to_balanced()
    print("OK")
