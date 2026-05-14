"""
Smoke tests pentru API-ul FastAPI Safe Navigation Simulator.
"""

import os
import sys
from dataclasses import replace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from web.backend import app as app_module


def test_health_endpoint():
    client = TestClient(app_module.app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_safe_navigation_status_lists_algorithms():
    client = TestClient(app_module.app)
    response = client.get("/api/safe-navigation/status")
    assert response.status_code == 200, response.text
    payload = response.json()
    algorithm_ids = {item["id"] for item in payload["algorithms"]}
    assert {
        "random",
        "rule_based",
        "astar",
        "risk_aware_astar",
        "tabular_q",
        "feature_q",
        "feature_risk_astar",
    }.issubset(algorithm_ids)
    assert "scenarios" in payload and len(payload["scenarios"]) >= 3


def test_safe_navigation_llm_status_and_disabled_fallback():
    original_settings = app_module.settings
    app_module.settings = replace(original_settings, llm_enabled=False)
    client = TestClient(app_module.app)

    try:
        status = client.get("/api/safe-navigation/analysis/status")
        assert status.status_code == 200, status.text
        assert status.json()["enabled"] is False
        assert status.json()["available"] is False

        response = client.post(
            "/api/safe-navigation/analysis/explain",
            json={
                "config": {"scenario": "medium"},
                "summary": {
                    "agents": [
                        {
                            "algorithm": "Risk-Aware A*",
                            "success_rate": 1.0,
                            "average_risk_exposure": 4.0,
                        }
                    ]
                },
                "recommendation": {
                    "objective": "safety_first",
                    "recommended_algorithm": "Risk-Aware A*",
                    "ranking": [{"algorithm": "Risk-Aware A*", "score": 0.9}],
                    "tradeoffs": [],
                },
                "question": "Explică recomandarea.",
            },
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["fallback"] is True
        assert "dezactivat" in payload["answer"].lower()

        config_response = client.post(
            "/api/safe-navigation/analysis/configure",
            json={
                "prompt": "Configurează un scenariu sigur.",
                "current_config": {
                    "algorithm": "astar",
                    "optimization_objective": "balanced",
                    "scenario": "medium",
                    "number_of_maps": 5,
                    "episodes_per_map": 2,
                },
            },
        )
        assert config_response.status_code == 200, config_response.text
        config_payload = config_response.json()
        assert config_payload["fallback"] is True
        assert config_payload["config"]["algorithm"] == "astar"
        assert config_payload["warnings"]
    finally:
        app_module.settings = original_settings


if __name__ == "__main__":
    print("=== Teste Web API ===\n")
    test_health_endpoint()
    test_safe_navigation_status_lists_algorithms()
    test_safe_navigation_llm_status_and_disabled_fallback()
    print("\n✅ Toate testele Web API au trecut!")
