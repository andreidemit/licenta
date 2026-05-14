"""Asistent LLM pentru transformarea cerințelor în configurații safe-navigation."""

from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from environment.map_generator import SCENARIOS
from web.backend.llm_client import LlmClient
from web.backend.models import (
    LlmConfigRequest,
    LlmConfigResponse,
    MonteCarloRequest,
    SafeNavigationRequest,
)


ALLOWED_ALGORITHMS = {
    "random",
    "rule_based",
    "astar",
    "risk_aware_astar",
    "tabular_q",
    "feature_q",
    "feature_risk_astar",
}
ALLOWED_CONFIG_FIELDS = {
    "algorithm",
    "optimization_objective",
    "experiment_profile",
    "scenario",
    "rows",
    "cols",
    "wall_probability",
    "danger_probability",
    "movement_noise",
    "risk_weight",
    "max_steps",
    "training_episodes",
    "number_of_maps",
    "episodes_per_map",
    "random_seed",
}
SAFE_NAVIGATION_FIELDS = set(SafeNavigationRequest.model_fields)

SYSTEM_PROMPT = """Ești asistent de configurare pentru Safe Navigation Simulator.
Transformi o cerință în limbaj natural într-o configurație JSON validă.
Reguli obligatorii:
- Returnează strict JSON cu cheile: config, rationale, warnings.
- config poate conține doar câmpuri din schema primită.
- Nu inventa algoritmi, scenarii, profile sau obiective în afara valorilor permise.
- Nu rula simulări și nu pretinde rezultate experimentale.
- Dacă utilizatorul cere siguranță, preferă optimization_objective=safety_first și risk_weight mai mare.
- Dacă utilizatorul cere viteză/demo rapid, preferă hărți mai mici, episoade mai puține și objective=efficiency_first sau balanced.
- Dacă utilizatorul cere robustețe/stocasticitate, folosește movement_noise > 0, experiment_profile=stochastic_execution și optimization_objective=robustness_first.
- Pentru densități mari, păstrează valorile în limite rezonabile ca să rămână probabil generabilă harta.
"""


class LlmConfigValidationError(ValueError):
    """Configurația propusă de model nu respectă schema aplicației."""


def _json_response_candidates(raw_content: str) -> list[str]:
    stripped = raw_content.strip()
    candidates = [stripped]
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            candidates.append("\n".join(lines[1:-1]).strip())
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        candidates.append(stripped[start:end + 1])
    return list(dict.fromkeys(candidate for candidate in candidates if candidate))


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _parse_llm_json(raw_content: str) -> dict[str, Any]:
    for candidate in _json_response_candidates(raw_content):
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    raise LlmConfigValidationError("Modelul nu a returnat JSON valid pentru configurare.")


def _base_config(current_config: dict[str, Any]) -> dict[str, Any]:
    monte_carlo_defaults = MonteCarloRequest().model_dump()
    config = {
        **SafeNavigationRequest().model_dump(),
        "number_of_maps": monte_carlo_defaults["number_of_maps"],
        "episodes_per_map": monte_carlo_defaults["episodes_per_map"],
    }
    for key in ALLOWED_CONFIG_FIELDS:
        if key in current_config and current_config[key] is not None:
            config[key] = current_config[key]
    return config


def _normalize_and_validate_config(
    current_config: dict[str, Any],
    proposed_config: dict[str, Any],
) -> tuple[dict[str, Any], list[str], list[str]]:
    ignored_fields = sorted(set(proposed_config) - ALLOWED_CONFIG_FIELDS)
    base = _base_config(current_config)
    accepted_patch = {
        key: value
        for key, value in proposed_config.items()
        if key in ALLOWED_CONFIG_FIELDS and value is not None
    }
    merged = {**base, **accepted_patch}
    if merged["algorithm"] not in ALLOWED_ALGORITHMS:
        raise LlmConfigValidationError(f"Algoritmul propus nu este permis: {merged['algorithm']}")

    try:
        safe_request = SafeNavigationRequest.model_validate({
            key: merged[key]
            for key in SAFE_NAVIGATION_FIELDS
            if key in merged
        })
        monte_request = MonteCarloRequest.model_validate({
            **{
                key: merged[key]
                for key in SAFE_NAVIGATION_FIELDS
                if key != "algorithm" and key in merged
            },
            "number_of_maps": merged["number_of_maps"],
            "episodes_per_map": merged["episodes_per_map"],
        })
    except ValidationError as exc:
        raise LlmConfigValidationError(str(exc)) from exc

    normalized = {
        **safe_request.model_dump(),
        "number_of_maps": monte_request.number_of_maps,
        "episodes_per_map": monte_request.episodes_per_map,
    }
    if normalized["scenario"] != "custom":
        preset = SCENARIOS.get(normalized["scenario"])
        if preset:
            normalized.update({
                "rows": preset.rows,
                "cols": preset.cols,
                "wall_probability": preset.wall_probability,
                "danger_probability": preset.danger_probability,
            })

    applied_fields = sorted(
        key
        for key in accepted_patch
        if key in normalized and normalized[key] != base.get(key)
    )
    warnings = [
        f"Câmp ignorat din răspunsul LLM: {field}"
        for field in ignored_fields
    ]
    if normalized["scenario"] != "custom" and any(
        key in accepted_patch
        for key in ("rows", "cols", "wall_probability", "danger_probability")
    ):
        warnings.append(
            "Pentru scenariile presetate, dimensiunea și densitățile au fost realiniate la presetul aplicației."
        )
    return normalized, applied_fields, warnings


def build_config_messages(request: LlmConfigRequest) -> list[dict[str, str]]:
    schema = {
        "allowed_fields": sorted(ALLOWED_CONFIG_FIELDS),
        "allowed_values": {
            "algorithm": sorted(ALLOWED_ALGORITHMS),
            "scenario": ["easy", "medium", "hard", "custom"],
            "optimization_objective": ["balanced", "safety_first", "efficiency_first", "robustness_first"],
            "experiment_profile": [
                "known_static",
                "high_risk",
                "stochastic_execution",
                "same_map_learning",
                "transfer_learning",
                "training_cost",
            ],
        },
        "numeric_limits": {
            "rows": "5..50",
            "cols": "5..50",
            "wall_probability": "0..0.6",
            "danger_probability": "0..0.4",
            "movement_noise": "0..1",
            "risk_weight": "0..10",
            "max_steps": "1..5000",
            "training_episodes": "0..10000",
            "number_of_maps": "1..100",
            "episodes_per_map": "1..100",
        },
    }
    payload = {
        "language": request.language,
        "user_request": request.prompt,
        "current_config": _base_config(request.current_config),
        "schema": schema,
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Propune o configurație validă pentru următoarea cerință. "
                "Returnează numai JSON valid.\n\n"
                f"{json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)}"
            ),
        },
    ]


def disabled_config_response(model: str, provider: str, current_config: dict[str, Any]) -> LlmConfigResponse:
    return LlmConfigResponse(
        config=_base_config(current_config),
        rationale=(
            "Asistentul de configurare AI este dezactivat. Configurația curentă este păstrată, "
            "iar modificările pot fi făcute manual."
        ),
        warnings=["Nu a fost apelat niciun model LLM. Activează LLM_ENABLED=true pentru propuneri text->config."],
        applied_fields=[],
        model=model,
        provider=provider,
        fallback=True,
    )


def configure_with_llm(request: LlmConfigRequest, client: LlmClient) -> LlmConfigResponse:
    raw_content = client.chat(build_config_messages(request), temperature=0.1)
    payload = _parse_llm_json(raw_content)
    proposed_config = payload.get("config")
    if not isinstance(proposed_config, dict):
        raise LlmConfigValidationError("Răspunsul LLM nu conține obiectul config.")

    config, applied_fields, validation_warnings = _normalize_and_validate_config(
        request.current_config,
        proposed_config,
    )
    rationale = str(payload.get("rationale") or "").strip()
    if not rationale:
        rationale = "Configurația a fost propusă pe baza cerinței și validată de backend."
    return LlmConfigResponse(
        config=config,
        rationale=rationale,
        warnings=_string_list(payload.get("warnings")) + validation_warnings,
        applied_fields=applied_fields,
        model=client.model,
        provider=client.provider,
        fallback=False,
    )
