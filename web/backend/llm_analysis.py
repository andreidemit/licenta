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
- Separă clar faptele numerice de interpretarea pedagogică.
- Citează valori numerice concrete când explici recomandarea, dacă sunt disponibile.
- Poți explica trade-off-uri: succes, risc, cost, pași, coliziuni, pericol, timeout, robustețe.
- Dacă datele sunt puține, menționează limitarea.
- Răspunde în limba cerută prin câmpul language.
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


def _round_metric(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 4)
    return value


def _metric_digest(request: LlmAnalysisRequest) -> dict[str, Any]:
    """Construiește un extras compact, determinist, pentru ancorarea explicației."""

    agents = request.summary.get("agents") if isinstance(request.summary, dict) else None
    agent_by_name = {
        row.get("algorithm"): row
        for row in (agents or [])
        if isinstance(row, dict) and row.get("algorithm")
    }
    ranking = request.recommendation.get("ranking") if isinstance(request.recommendation, dict) else None
    ranked_agents = []
    for item in (ranking or [])[:5]:
        if not isinstance(item, dict):
            continue
        algorithm = item.get("algorithm")
        metrics = item.get("metrics")
        if not isinstance(metrics, dict):
            metrics = agent_by_name.get(algorithm, {})
        digest_row = {
            "rank": item.get("rank"),
            "algorithm": algorithm,
            "score": _round_metric(item.get("score")),
            "success_rate": _round_metric(metrics.get("success_rate")),
            "collision_rate": _round_metric(metrics.get("collision_rate")),
            "danger_entry_rate": _round_metric(metrics.get("danger_entry_rate")),
            "timeout_rate": _round_metric(metrics.get("timeout_rate")),
            "average_steps": _round_metric(metrics.get("average_steps")),
            "average_risk_exposure": _round_metric(metrics.get("average_risk_exposure")),
            "average_total_cost": _round_metric(metrics.get("average_total_cost")),
            "average_reward": _round_metric(metrics.get("average_reward")),
        }
        ranked_agents.append({key: value for key, value in digest_row.items() if value is not None})

    return {
        "deterministic_recommendation": request.recommendation.get("recommended_algorithm"),
        "objective": request.recommendation.get("objective"),
        "objective_label": request.recommendation.get("objective_label"),
        "episode_count": request.summary.get("episode_count"),
        "ranked_agents": ranked_agents,
        "instruction": (
            "Aceste valori sunt calculate de simulator și motorul determinist de recomandare. "
            "Folosește-le ca fapte; adaugă doar interpretare textuală."
        ),
    }


def build_messages(request: LlmAnalysisRequest, max_input_chars: int) -> list[dict[str, str]]:
    question = (request.question or DEFAULT_QUESTION).strip() or DEFAULT_QUESTION
    payload = {
        "question": question,
        "language": request.language,
        "metric_digest": _metric_digest(request),
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


def parse_analysis_response(raw_content: str, model: str, provider: str) -> LlmAnalysisResponse:
    parsed = None
    for candidate in _json_response_candidates(raw_content):
        try:
            candidate_payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate_payload, dict):
            parsed = candidate_payload
            break

    if parsed is None:
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


STREAMING_SYSTEM_PROMPT = """Ești Analist AI pentru Safe Navigation Simulator.
Explici rezultatele Monte Carlo pe baza JSON-ului primit.
Reguli obligatorii:
- Folosește doar metricile și recomandarea furnizate în input.
- Nu inventa rezultate, algoritmi, hărți, procente sau comparații.
- Recomandarea este calculată determinist de simulator; nu o recalcula și nu o contrazice.
- Citează valori numerice concrete când explici recomandarea, dacă sunt disponibile.
- Poți explica trade-off-uri: succes, risc, cost, pași, coliziuni, pericol, timeout, robustețe.
- Dacă datele sunt puține, menționează limitarea.
- Răspunde în limba cerută prin câmpul language.
- Fii concis: maximum 6 propoziții în text continuu, fără liste, fără secțiuni numerotate.
- Răspunde DOAR cu text simplu, fără JSON, fără cod, fără formatare Markdown.
"""


def build_streaming_messages(request: LlmAnalysisRequest, max_input_chars: int) -> list[dict[str, str]]:
    """Construiește mesaje pentru streaming text plain (fără JSON mode)."""
    question = (request.question or DEFAULT_QUESTION).strip() or DEFAULT_QUESTION
    payload = {
        "question": question,
        "language": request.language,
        "metric_digest": _metric_digest(request),
        "config": request.config,
        "summary": request.summary,
        "recommendation": request.recommendation,
    }
    content = (
        "Analizează următoarele rezultate ale simulatorului. "
        "Răspunde DOAR cu text simplu (fără JSON), maximum 6 propoziții.\n\n"
        f"{_truncate_json_payload(payload, max_input_chars)}"
    )
    return [
        {"role": "system", "content": STREAMING_SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def stream_explain_with_llm(
    request: LlmAnalysisRequest,
    client: LlmClient,
    max_input_chars: int,
):
    """Iterează tokenii reali de la LLM pentru endpoint-ul SSE."""
    messages = build_streaming_messages(request, max_input_chars=max_input_chars)
    yield from client.chat_stream(messages)
