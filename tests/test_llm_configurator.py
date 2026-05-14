"""Teste pentru asistentul LLM text->config."""

from web.backend.llm_configurator import (
    build_config_messages,
    configure_with_llm,
    disabled_config_response,
)
from web.backend.models import LlmConfigRequest


def _request(prompt: str = "Configurează un scenariu dificil unde siguranța contează mai mult decât viteza."):
    return LlmConfigRequest(
        prompt=prompt,
        current_config={
            "algorithm": "astar",
            "optimization_objective": "balanced",
            "experiment_profile": "known_static",
            "scenario": "medium",
            "rows": 15,
            "cols": 15,
            "wall_probability": 0.2,
            "danger_probability": 0.1,
            "movement_noise": 0.0,
            "risk_weight": 1.0,
            "max_steps": 300,
            "training_episodes": 100,
            "number_of_maps": 5,
            "episodes_per_map": 2,
            "random_seed": 42,
        },
    )


def test_build_config_messages_contains_guardrails_and_schema():
    messages = build_config_messages(_request())

    assert messages[0]["role"] == "system"
    assert "Nu rula simulări" in messages[0]["content"]
    user_content = messages[1]["content"]
    assert "allowed_fields" in user_content
    assert "safety_first" in user_content
    assert "current_config" in user_content


def test_configure_with_llm_validates_and_normalizes_config():
    class FakeClient:
        model = "gemma4:26b"
        provider = "ollama"

        def chat(self, messages, temperature=0.1):
            assert temperature == 0.1
            return """
            ```json
            {
              "config": {
                "algorithm": "risk_aware_astar",
                "optimization_objective": "safety_first",
                "experiment_profile": "high_risk",
                "scenario": "custom",
                "rows": 20,
                "cols": 20,
                "wall_probability": 0.22,
                "danger_probability": 0.18,
                "movement_noise": 0.1,
                "risk_weight": 3.0,
                "number_of_maps": 8,
                "episodes_per_map": 3,
                "unknown_field": "ignored"
              },
              "rationale": "Am crescut riscul și obiectivul de siguranță.",
              "warnings": ["Testează cu mai multe seed-uri."]
            }
            ```
            """

    response = configure_with_llm(_request(), client=FakeClient())

    assert response.fallback is False
    assert response.config["scenario"] == "custom"
    assert response.config["algorithm"] == "risk_aware_astar"
    assert response.config["optimization_objective"] == "safety_first"
    assert response.config["rows"] == 20
    assert response.config["danger_probability"] == 0.18
    assert response.config["number_of_maps"] == 8
    assert response.config["episodes_per_map"] == 3
    assert "unknown_field" not in response.config
    assert "algorithm" in response.applied_fields
    assert any("unknown_field" in warning for warning in response.warnings)


def test_preset_scenario_realigns_map_parameters():
    class FakeClient:
        model = "gemma4:26b"
        provider = "ollama"

        def chat(self, messages, temperature=0.1):
            return """
            {
              "config": {
                "scenario": "hard",
                "rows": 50,
                "cols": 50,
                "wall_probability": 0.01,
                "danger_probability": 0.01
              },
              "rationale": "Folosesc presetul dificil.",
              "warnings": []
            }
            """

    response = configure_with_llm(_request("Vreau presetul dificil."), client=FakeClient())

    assert response.config["scenario"] == "hard"
    assert response.config["rows"] != 50
    assert response.config["wall_probability"] != 0.01
    assert any("preset" in warning.lower() for warning in response.warnings)


def test_disabled_config_response_keeps_current_config():
    response = disabled_config_response("gemma4:26b", "ollama", _request().current_config)

    assert response.fallback is True
    assert response.config["algorithm"] == "astar"
    assert response.applied_fields == []
    assert response.warnings


if __name__ == "__main__":
    test_build_config_messages_contains_guardrails_and_schema()
    test_configure_with_llm_validates_and_normalizes_config()
    test_preset_scenario_realigns_map_parameters()
    test_disabled_config_response_keeps_current_config()
    print("OK")
