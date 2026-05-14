import { Award, ListChecks, Scale, Target } from 'lucide-react';
import { algorithmLabel, formatNumber, formatPercent } from './analysis/analysisHelpers';
import type { MonteCarloResult, OptimizationObjective, StrategyRecommendation } from './types';

const OBJECTIVE_OPTIONS: { id: OptimizationObjective; label: string }[] = [
  { id: 'balanced', label: 'Echilibrat' },
  { id: 'safety_first', label: 'Siguranță' },
  { id: 'efficiency_first', label: 'Eficiență' },
  { id: 'robustness_first', label: 'Robustețe' },
];

function score(value: number) {
  return `${Math.round(value * 100)} / 100`;
}

function metricLine(item: StrategyRecommendation['ranking'][number]) {
  return `${formatPercent(item.metrics.success_rate)} succes · risc ${formatNumber(item.metrics.average_risk_exposure, 1)} · ${formatNumber(item.metrics.average_steps, 1)} pași`;
}

export function RecommendationPanel({
  result,
  selectedObjective,
  onObjectiveChange,
}: {
  result?: MonteCarloResult;
  selectedObjective?: OptimizationObjective;
  onObjectiveChange?: (objective: OptimizationObjective) => void;
}) {
  const recommendation = result?.recommendation;
  const objectiveChanged = !!selectedObjective && !!recommendation && selectedObjective !== recommendation.objective;

  if (!recommendation || !recommendation.recommended_algorithm) {
    return (
      <section className="recommendation-panel recommendation-panel--empty">
        <div className="recommendation-panel__topline">
          <h3><Target size={17} /> Recomandare strategie</h3>
          {selectedObjective && onObjectiveChange ? (
            <select value={selectedObjective} onChange={(event) => onObjectiveChange(event.target.value as OptimizationObjective)}>
              {OBJECTIVE_OPTIONS.map((objective) => (
                <option key={objective.id} value={objective.id}>{objective.label}</option>
              ))}
            </select>
          ) : null}
        </div>
        <p>Rulează Monte Carlo pentru a calcula o recomandare explicabilă din metricile reale.</p>
      </section>
    );
  }

  const top = recommendation.ranking[0];
  const ranking = recommendation.ranking.slice(0, 5);

  return (
    <section className="recommendation-panel">
      <div className="recommendation-panel__hero">
        <div>
          <p className="eyebrow"><Award size={14} /> Recomandare strategie</p>
          <h3>{algorithmLabel(recommendation.recommended_algorithm)}</h3>
          <span>Obiectiv: {recommendation.objective_label}</span>
        </div>
        <div className="recommendation-panel__objective">
          {selectedObjective && onObjectiveChange ? (
            <select value={selectedObjective} onChange={(event) => onObjectiveChange(event.target.value as OptimizationObjective)}>
              {OBJECTIVE_OPTIONS.map((objective) => (
                <option key={objective.id} value={objective.id}>{objective.label}</option>
              ))}
            </select>
          ) : null}
          <strong>{score(top.score)}</strong>
        </div>
      </div>

      <p className="recommendation-panel__explanation">{recommendation.explanation}</p>
      {objectiveChanged ? (
        <p className="recommendation-panel__stale">
          Obiectivul selectat s-a schimbat. Rulează din nou Monte Carlo pentru a recalcula ranking-ul.
        </p>
      ) : null}

      <div className="recommendation-panel__grid">
        <div>
          <h4><ListChecks size={15} /> Ranking calculat</h4>
          <div className="recommendation-ranking">
            {ranking.map((item) => (
              <div key={item.algorithm} className={item.rank === 1 ? 'is-recommended' : ''}>
                <span>{item.rank}</span>
                <div>
                  <strong>{algorithmLabel(item.algorithm)}</strong>
                  <small>{metricLine(item)}</small>
                </div>
                <b>{score(item.score)}</b>
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4><Scale size={15} /> Compromisuri</h4>
          <ul className="recommendation-tradeoffs">
            {recommendation.tradeoffs.map((tradeoff) => (
              <li key={tradeoff}>{tradeoff}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default RecommendationPanel;
