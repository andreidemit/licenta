"""Prompturi și normalizare răspuns pentru analistul AI safe-navigation."""

from __future__ import annotations

import json
from typing import Any

from web.backend.llm_client import LlmClient
from web.backend.models import LlmAnalysisRequest, LlmAnalysisResponse


SYSTEM_PROMPT = """Ești Analist AI pentru Safe Navigation Simulator.
Explici rezultatele Monte Carlo pe baza JSON-ului primit.
Reguli obligatorii:
- Folosește doar metricile și recomandarea furnizate în input.
- Nu inventa rezultate, algoritmi, hărți, procente sau comparații.
- Recomandarea este calculată determinist de simulator; nu o recalcula și nu o contrazice.
- Poți explica trade-off-uri: succes, risc, cost, pași, coliziuni, pericol, timeout, robustețe.
- Dacă datele sunt puține, menționează limitarea.
- Fii concis: maximum 6 propoziții în answer și maximum 5 puncte cheie.
- Răspunde strict ca JSON cu cheile: answer, key_points, limitations, used_metrics.
"""

DEFAULT_QUESTION = "Explică recomandarea, ranking-ul și principalele compromisuri pentru această rulare Monte Carlo."


def _truncate_json_payload(payload: dict[str, Any], max_chars: int) -> str:
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    if len(text) <= max_chars:
        return text
    compact = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    if len(compact) <= max_chars:
        return compact
    return compact[:max_chars] + "\n...[truncated]"


def build_messages(request: LlmAnalysisRequest, max_input_chars: int) -> list[dict[str, str]]:
    question = (request.question or DEFAULT_QUESTION).strip() or DEFAULT_QUESTION
    payload = {
        "question": question,
        "language": request.language,
        "config": request.config,
        "summary": request.summary,
        "recommendation": request.recommendation,
    }
    content = (
        "Analizează următoarele rezultate ale simulatorului. "
        "Returnează numai JSON valid.\n\n"
        f"{_truncate_json_payload(payload, max_input_chars)}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def parse_analysis_response(raw_content: str, model: str, provider: str) -> LlmAnalysisResponse:
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        return LlmAnalysisResponse(
            answer=raw_content.strip(),
            key_points=[],
            limitations=["Modelul nu a returnat JSON valid; răspunsul a fost afișat ca text brut."],
            used_metrics=[],
            model=model,
            provider=provider,
            fallback=True,
        )

    answer = str(parsed.get("answer") or "").strip()
    if not answer:
        answer = "Analiza a fost generată, dar modelul nu a furnizat un câmp answer explicit."
    return LlmAnalysisResponse(
        answer=answer,
        key_points=_string_list(parsed.get("key_points")),
        limitations=_string_list(parsed.get("limitations")),
        used_metrics=_string_list(parsed.get("used_metrics")),
        model=model,
        provider=provider,
        fallback=False,
    )


def disabled_response(model: str, provider: str) -> LlmAnalysisResponse:
    return LlmAnalysisResponse(
        answer=(
            "Analistul AI este dezactivat. Recomandarea deterministă rămâne disponibilă în dashboard, "
            "iar explicația LLM poate fi activată prin LLM_ENABLED=true."
        ),
        key_points=[
            "Simulatorul poate rula fără model lingvistic.",
            "Ranking-ul și scorurile rămân calculate determinist din metricile Monte Carlo.",
        ],
        limitations=["Nu a fost apelat niciun model LLM."],
        used_metrics=[],
        model=model,
        provider=provider,
        fallback=True,
    )


def explain_with_llm(
    request: LlmAnalysisRequest,
    client: LlmClient,
    max_input_chars: int,
) -> LlmAnalysisResponse:
    messages = build_messages(request, max_input_chars=max_input_chars)
    raw_content = client.chat(messages)
    return parse_analysis_response(raw_content, model=client.model, provider=client.provider)
