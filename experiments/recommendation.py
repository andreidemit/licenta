"""Recomandare explicabilă de strategie pe baza rezultatelor Monte Carlo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


RecommendationObjective = str

VALID_OBJECTIVES = {"balanced", "safety_first", "efficiency_first", "robustness_first"}

OBJECTIVE_LABELS = {
    "balanced": "echilibru succes-risc-cost",
    "safety_first": "siguranță înainte de eficiență",
    "efficiency_first": "eficiență înainte de prudență",
    "robustness_first": "robustețe pe hărți și rulări diferite",
}

OBJECTIVE_WEIGHTS: dict[RecommendationObjective, dict[str, float]] = {
    "balanced": {
        "success": 0.30,
        "risk": 0.19,
        "cost": 0.13,
        "steps": 0.12,
        "collisions": 0.08,
        "danger": 0.08,
        "timeout": 0.06,
        "stability": 0.02,
        "runtime": 0.02,
    },
    "safety_first": {
        "risk": 0.28,
        "collisions": 0.18,
        "danger": 0.18,
        "success": 0.16,
        "timeout": 0.10,
        "stability": 0.05,
        "cost": 0.02,
        "steps": 0.02,
        "runtime": 0.01,
    },
    "efficiency_first": {
        "steps": 0.26,
        "cost": 0.22,
        "success": 0.20,
        "risk": 0.10,
        "runtime": 0.06,
        "timeout": 0.07,
        "collisions": 0.04,
        "danger": 0.03,
        "stability": 0.02,
    },
    "robustness_first": {
        "success": 0.32,
        "timeout": 0.22,
        "stability": 0.14,
        "risk": 0.12,
        "collisions": 0.08,
        "danger": 0.07,
        "cost": 0.02,
        "steps": 0.02,
        "runtime": 0.01,
    },
}


@dataclass(frozen=True)
class MetricVectors:
    risk: list[float]
    cost: list[float]
    steps: list[float]
    collisions: list[float]
    danger: list[float]
    timeout: list[float]
    instability: list[float]
    runtime: list[float]


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number != number:
        return default
    return number


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _inverse_minmax(value: float, values: list[float]) -> float:
    if not values:
        return 1.0
    low = min(values)
    high = max(values)
    if high == low:
        return 1.0
    return _clamp01(1.0 - ((value - low) / (high - low)))


def _ci_width(row: dict[str, Any], metric: str) -> float:
    low = row.get(f"{metric}_ci95_low")
    high = row.get(f"{metric}_ci95_high")
    if low is None or high is None:
        return 0.0
    return max(0.0, _safe_float(high) - _safe_float(low))


def _metric_vectors(rows: list[dict[str, Any]]) -> MetricVectors:
    return MetricVectors(
        risk=[_safe_float(row.get("average_risk_exposure")) for row in rows],
        cost=[_safe_float(row.get("average_total_cost")) for row in rows],
        steps=[_safe_float(row.get("average_steps")) for row in rows],
        collisions=[
            _safe_float(row.get("collision_rate"), _safe_float(row.get("average_collisions")))
            for row in rows
        ],
        danger=[_safe_float(row.get("danger_entry_rate")) for row in rows],
        timeout=[_safe_float(row.get("timeout_rate")) for row in rows],
        runtime=[_safe_float(row.get("average_computation_time_ms")) for row in rows],
        instability=[
            _ci_width(row, "success_rate")
            + _ci_width(row, "collision_rate")
            + _ci_width(row, "danger_entry_rate")
            + _ci_width(row, "timeout_rate")
            for row in rows
        ],
    )


def _component_scores(row: dict[str, Any], vectors: MetricVectors) -> dict[str, float]:
    collision_metric = _safe_float(row.get("collision_rate"), _safe_float(row.get("average_collisions")))
    instability = (
        _ci_width(row, "success_rate")
        + _ci_width(row, "collision_rate")
        + _ci_width(row, "danger_entry_rate")
        + _ci_width(row, "timeout_rate")
    )
    return {
        "success": _clamp01(_safe_float(row.get("success_rate"))),
        "risk": _inverse_minmax(_safe_float(row.get("average_risk_exposure")), vectors.risk),
        "cost": _inverse_minmax(_safe_float(row.get("average_total_cost")), vectors.cost),
        "steps": _inverse_minmax(_safe_float(row.get("average_steps")), vectors.steps),
        "collisions": _inverse_minmax(collision_metric, vectors.collisions),
        "danger": _inverse_minmax(_safe_float(row.get("danger_entry_rate")), vectors.danger),
        "timeout": _inverse_minmax(_safe_float(row.get("timeout_rate")), vectors.timeout),
        "stability": _inverse_minmax(instability, vectors.instability),
        "runtime": _inverse_minmax(_safe_float(row.get("average_computation_time_ms")), vectors.runtime),
    }


def _score(components: dict[str, float], objective: RecommendationObjective) -> float:
    weights = OBJECTIVE_WEIGHTS[objective]
    return sum(components[name] * weight for name, weight in weights.items())


def _metrics_payload(row: dict[str, Any]) -> dict[str, float]:
    return {
        "success_rate": _safe_float(row.get("success_rate")),
        "average_risk_exposure": _safe_float(row.get("average_risk_exposure")),
        "average_total_cost": _safe_float(row.get("average_total_cost")),
        "average_steps": _safe_float(row.get("average_steps")),
        "collision_rate": _safe_float(row.get("collision_rate"), _safe_float(row.get("average_collisions"))),
        "danger_entry_rate": _safe_float(row.get("danger_entry_rate")),
        "timeout_rate": _safe_float(row.get("timeout_rate")),
        "average_computation_time_ms": _safe_float(row.get("average_computation_time_ms")),
    }


def _pct(value: float) -> str:
    return f"{round(value * 100)}%"


def _num(value: float) -> str:
    return f"{value:.1f}"


def _top_metric(rows: list[dict[str, Any]], metric: str, reverse: bool = False) -> dict[str, Any]:
    return sorted(rows, key=lambda row: _safe_float(row.get(metric)), reverse=reverse)[0]


def _top_metric_value(row: dict[str, Any], metric: str) -> float:
    return _safe_float(row.get(metric))


def _build_explanation(
    recommended: dict[str, Any],
    objective: RecommendationObjective,
    rows: list[dict[str, Any]],
) -> str:
    metrics = recommended["metrics"]
    algorithm = recommended["algorithm"]
    objective_label = OBJECTIVE_LABELS[objective]
    safest = _top_metric(rows, "average_risk_exposure")
    fastest = _top_metric(rows, "average_steps")
    best_success = _top_metric(rows, "success_rate", reverse=True)

    if objective == "safety_first":
        return (
            f"Pentru obiectivul de {objective_label}, {algorithm} are cel mai bun scor deoarece combină "
            f"succes {_pct(metrics['success_rate'])} cu risc mediu {_num(metrics['average_risk_exposure'])}, "
            f"coliziuni {_pct(metrics['collision_rate'])} și intrări în pericol {_pct(metrics['danger_entry_rate'])}."
        )
    if objective == "efficiency_first":
        return (
            f"Pentru obiectivul de {objective_label}, {algorithm} este recomandat deoarece produce un compromis bun "
            f"între {_num(metrics['average_steps'])} pași medii, cost total {_num(metrics['average_total_cost'])} "
            f"și succes {_pct(metrics['success_rate'])}."
        )
    if objective == "robustness_first":
        return (
            f"Pentru obiectivul de {objective_label}, {algorithm} este recomandat deoarece păstrează o rată de succes "
            f"de {_pct(metrics['success_rate'])} și timeout {_pct(metrics['timeout_rate'])} pe setul de hărți generate."
        )
    return (
        f"Pentru obiectivul de {objective_label}, {algorithm} are scorul agregat cel mai bun. "
        f"Comparația include un lider la succes ({best_success['algorithm']}), agentul cu cea mai mică "
        f"expunere măsurată la risc ({safest['algorithm']}) și cel mai eficient ca pași ({fastest['algorithm']})."
    )


def _build_tradeoffs(recommended: dict[str, Any], rows: list[dict[str, Any]]) -> list[str]:
    if not rows:
        return []

    top_algorithm = recommended["algorithm"]
    top_metrics = recommended["metrics"]
    best_success = _top_metric(rows, "success_rate", reverse=True)
    safest = _top_metric(rows, "average_risk_exposure")
    fastest = _top_metric(rows, "average_steps")
    cheapest = _top_metric(rows, "average_total_cost")
    tradeoffs: list[str] = []

    top_success = top_metrics["success_rate"]
    best_success_value = _top_metric_value(best_success, "success_rate")
    if best_success["algorithm"] != top_algorithm and best_success_value > top_success:
        tradeoffs.append(
            f"{best_success['algorithm']} are rată de succes mai mare ({_pct(best_success_value)}), "
            f"dar scorul total al recomandării scade din cauza riscului, costului sau timeout-ului."
        )
    if safest["algorithm"] != top_algorithm:
        top_risk = top_metrics["average_risk_exposure"]
        safe_risk = _top_metric_value(safest, "average_risk_exposure")
        if top_risk > safe_risk:
            tradeoffs.append(
                f"{safest['algorithm']} minimizează riscul ({_num(safe_risk)}), în timp ce recomandarea acceptă "
                f"risc {_num(top_risk)} pentru un rezultat global mai bun."
            )
    fastest_steps = _top_metric_value(fastest, "average_steps")
    if fastest["algorithm"] != top_algorithm and fastest_steps < top_metrics["average_steps"]:
        tradeoffs.append(
            f"{fastest['algorithm']} are cele mai scurte trasee ({_num(fastest_steps)} pași), "
            "dar viteza singură nu explică siguranța sau robustețea."
        )
    cheapest_cost = _top_metric_value(cheapest, "average_total_cost")
    if cheapest["algorithm"] != top_algorithm and cheapest_cost < top_metrics["average_total_cost"]:
        tradeoffs.append(
            f"{cheapest['algorithm']} are cel mai mic cost total ({_num(cheapest_cost)}), "
            "însă criteriul selectat ia în calcul și succesul, riscul și erorile operaționale."
        )
    if top_metrics["timeout_rate"] > 0:
        tradeoffs.append(
            f"Recomandarea încă are timeout {_pct(top_metrics['timeout_rate'])}; pentru utilizare critică trebuie testată pe mai multe hărți."
        )
    if not tradeoffs:
        tradeoffs.append("Nu apar compromisuri majore în această rulare: strategia recomandată conduce și la metricile principale.")
    return tradeoffs[:4]


def build_recommendation(summary: dict[str, Any], objective: RecommendationObjective = "balanced") -> dict[str, Any]:
    """Calculează recomandarea de strategie din metricile agregate Monte Carlo."""

    if objective not in VALID_OBJECTIVES:
        objective = "balanced"

    rows = list(summary.get("agents") or [])
    if not rows:
        return {
            "objective": objective,
            "objective_label": OBJECTIVE_LABELS[objective],
            "recommended_algorithm": None,
            "ranking": [],
            "explanation": "Nu există rezultate Monte Carlo suficiente pentru a recomanda o strategie.",
            "tradeoffs": [],
        }

    vectors = _metric_vectors(rows)
    ranking = []
    for row in rows:
        components = _component_scores(row, vectors)
        ranking.append(
            {
                "rank": 0,
                "algorithm": row.get("algorithm", "unknown"),
                "score": round(_score(components, objective), 4),
                "metrics": _metrics_payload(row),
                "component_scores": {key: round(value, 4) for key, value in components.items()},
            }
        )

    ranking.sort(
        key=lambda item: (
            -item["score"],
            -item["metrics"]["success_rate"],
            item["metrics"]["average_risk_exposure"],
            item["metrics"]["average_total_cost"],
            item["metrics"]["average_steps"],
            item["metrics"]["average_computation_time_ms"],
            item["algorithm"],
        )
    )
    for index, item in enumerate(ranking, start=1):
        item["rank"] = index

    recommended = ranking[0]
    return {
        "objective": objective,
        "objective_label": OBJECTIVE_LABELS[objective],
        "recommended_algorithm": recommended["algorithm"],
        "ranking": ranking,
        "explanation": _build_explanation(recommended, objective, rows),
        "tradeoffs": _build_tradeoffs(recommended, rows),
    }
