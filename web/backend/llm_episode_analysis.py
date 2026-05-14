"""Explicație LLM pentru un episod single-run de safe-navigation."""

from __future__ import annotations

import json
from typing import Any

from web.backend.llm_client import LlmClient
from web.backend.models import LlmAnalysisResponse


SYSTEM_PROMPT = """Ești Analist AI pentru Safe Navigation Simulator.
Explici rezultatul unui singur episod de navigare în mediu cu risc.
Reguli obligatorii:
- Folosește NUMAI metricile furnizate în input; nu inventa.
- Explică: dacă agentul a reușit sau nu și de ce, cât de eficient a fost traseul, situația de siguranță (coliziuni, pericole).
- Menționează 1-2 sugestii concrete pentru îmbunătățire, bazate pe date.
- Fii concis: maximum 5 propoziții în answer și maximum 4 puncte cheie.
- Răspunde strict ca JSON cu cheile: answer, key_points, limitations, used_metrics.
- Răspunde în limba cerută prin câmpul language.
"""


def _episode_digest(result: dict[str, Any], algorithm: str, config: dict[str, Any]) -> dict[str, Any]:
    return {
        "algorithm": algorithm or result.get("algorithm", ""),
        "success": result.get("success", False),
        "timeout": result.get("timeout", False),
        "steps": result.get("steps"),
        "total_reward": result.get("total_reward"),
        "total_risk_exposure": result.get("total_risk_exposure"),
        "collisions": result.get("collisions"),
        "danger_entries": result.get("danger_entries"),
        "total_cost": result.get("total_cost"),
        "path_length": result.get("path_length"),
        "computation_time_ms": result.get("computation_time_ms"),
        "config_summary": {
            k: config.get(k)
            for k in ("scenario", "movement_noise", "risk_weight", "max_steps", "training_episodes")
            if config.get(k) is not None
        },
    }


def build_episode_messages(
    result: dict[str, Any],
    algorithm: str,
    config: dict[str, Any],
    language: str = "ro",
) -> list[dict[str, str]]:
    digest = _episode_digest(result, algorithm, config)
    payload = {
        "language": language,
        "episode": digest,
        "instruction": (
            "Explică rezultatul acestui episod. "
            "Returnează numai JSON valid cu cheile: answer, key_points, limitations, used_metrics."
        ),
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        },
    ]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _parse_response(raw: str, model: str, provider: str) -> LlmAnalysisResponse:
    stripped = raw.strip()
    candidates = [stripped]
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[-1].strip() == "```":
            candidates.append("\n".join(lines[1:-1]).strip())
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end > start:
        candidates.append(stripped[start : end + 1])

    for candidate in dict.fromkeys(c for c in candidates if c):
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        answer = str(parsed.get("answer") or "").strip()
        if not answer:
            answer = "Analiza episodului a fost generată, dar modelul nu a furnizat câmpul answer."
        return LlmAnalysisResponse(
            answer=answer,
            key_points=_string_list(parsed.get("key_points")),
            limitations=_string_list(parsed.get("limitations")),
            used_metrics=_string_list(parsed.get("used_metrics")),
            model=model,
            provider=provider,
            fallback=False,
        )

    return LlmAnalysisResponse(
        answer=stripped,
        key_points=[],
        limitations=["Modelul nu a returnat JSON valid."],
        used_metrics=[],
        model=model,
        provider=provider,
        fallback=True,
    )


def explain_episode(
    result: dict[str, Any],
    algorithm: str,
    config: dict[str, Any],
    client: LlmClient,
    language: str = "ro",
) -> LlmAnalysisResponse:
    messages = build_episode_messages(result, algorithm, config, language)
    raw = client.chat(messages)
    return _parse_response(raw, model=client.model, provider=client.provider)


def disabled_episode_response(model: str, provider: str) -> LlmAnalysisResponse:
    return LlmAnalysisResponse(
        answer=(
            "Analistul AI este dezactivat. Activează LLM_ENABLED=true "
            "pentru explicații generate de model asupra episoadelor."
        ),
        key_points=["Episodul poate fi interpretat manual din metricile afișate."],
        limitations=["Nu a fost apelat niciun model LLM."],
        used_metrics=[],
        model=model,
        provider=provider,
        fallback=True,
    )
