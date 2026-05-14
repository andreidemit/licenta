"""Explicație LLM pentru o hartă generată procedural în safe-navigation."""

from __future__ import annotations

import json
from typing import Any

from web.backend.llm_client import LlmClient
from web.backend.models import LlmAnalysisResponse


SYSTEM_PROMPT = """Ești Analist AI pentru Safe Navigation Simulator.
Explici caracteristicile unei hărți de navigare și implicațiile pentru agenți.
Reguli obligatorii:
- Folosește NUMAI datele furnizate în input; nu inventa statistici.
- Explică: structura generală a hărții, gradul de dificultate, ce tipuri de strategii pot fi avantajate.
- Menționează 2-3 observații concrete despre impactul densității, riscului sau configurației hărții.
- Fii concis: maximum 5 propoziții în answer și maximum 4 puncte cheie.
- Răspunde strict ca JSON cu cheile: answer, key_points, limitations, used_metrics.
- Răspunde în limba cerută prin câmpul language.
"""


def _count_cells(grid: list[list[int]]) -> dict[str, int]:
    """Numără tipurile de celule din grid. Convenție: 0=liber, 1=perete, 2=pericol, 3=start, 4=goal."""
    counts: dict[str, int] = {"free": 0, "wall": 0, "danger": 0, "other": 0}
    for row in grid:
        for cell in row:
            if cell == 0:
                counts["free"] += 1
            elif cell == 1:
                counts["wall"] += 1
            elif cell == 2:
                counts["danger"] += 1
            else:
                counts["other"] += 1
    return counts


def _map_digest(environment: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    rows = environment.get("rows", 0)
    cols = environment.get("cols", 0)
    grid = environment.get("grid") or []
    total_cells = rows * cols
    cell_counts = _count_cells(grid) if grid else {}

    return {
        "dimensions": f"{rows}x{cols}",
        "total_cells": total_cells,
        "wall_count": cell_counts.get("wall", 0),
        "danger_count": cell_counts.get("danger", 0),
        "free_count": cell_counts.get("free", 0),
        "wall_density": round(cell_counts.get("wall", 0) / max(total_cells, 1), 3),
        "danger_density": round(cell_counts.get("danger", 0) / max(total_cells, 1), 3),
        "start": environment.get("start"),
        "goal": environment.get("goal"),
        "config_summary": {
            k: config.get(k)
            for k in ("scenario", "movement_noise", "risk_weight", "wall_probability", "danger_probability", "random_seed")
            if config.get(k) is not None
        },
    }


def build_map_messages(
    environment: dict[str, Any],
    config: dict[str, Any],
    language: str = "ro",
) -> list[dict[str, str]]:
    digest = _map_digest(environment, config)
    payload = {
        "language": language,
        "map": digest,
        "instruction": (
            "Explică caracteristicile acestei hărți și implicațiile pentru navigare. "
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
            answer = "Analiza hărții a fost generată, dar modelul nu a furnizat câmpul answer."
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


def explain_map(
    environment: dict[str, Any],
    config: dict[str, Any],
    client: LlmClient,
    language: str = "ro",
) -> LlmAnalysisResponse:
    messages = build_map_messages(environment, config, language)
    raw = client.chat(messages)
    return _parse_response(raw, model=client.model, provider=client.provider)


def disabled_map_response(model: str, provider: str) -> LlmAnalysisResponse:
    return LlmAnalysisResponse(
        answer=(
            "Analistul AI este dezactivat. Activează LLM_ENABLED=true "
            "pentru explicații generate de model despre harta curentă."
        ),
        key_points=["Harta poate fi interpretată vizual din indicatorii afișați."],
        limitations=["Nu a fost apelat niciun model LLM."],
        used_metrics=[],
        model=model,
        provider=provider,
        fallback=True,
    )
