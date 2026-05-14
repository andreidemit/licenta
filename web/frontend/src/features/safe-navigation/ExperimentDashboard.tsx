import { BarChart3 } from 'lucide-react';
import { AiAnalystPanel } from './AiAnalystPanel';
import { RecommendationPanel } from './RecommendationPanel';
import { TooltipLabel } from './TooltipLabel';
import type { MonteCarloResult, OptimizationObjective } from './types';
import { algorithmUseCases } from './experimentProfiles';

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function num(value: number) {
  return value.toFixed(1);
}

function algorithmLabel(value: string) {
  const labels: Record<string, string> = {
    random: 'Aleator',
    Random: 'Aleator',
    rule_based: 'Bazat pe reguli',
    'Rule-Based': 'Bazat pe reguli',
    astar: 'A*',
    risk_aware_astar: 'A* conștient de risc',
    'Risk-Aware A*': 'A* conștient de risc',
    tabular_q: 'Q-Learning tabular',
    'Tabular Q-Learning': 'Q-Learning tabular',
    feature_q: 'Q-Learning pe trăsături',
    'Feature-Based Q-Learning': 'Q-Learning pe trăsături',
    feature_risk_astar: 'Feature-Risk A* experimental',
    'Feature-Risk A*': 'Feature-Risk A* experimental',
  };
  return labels[value] ?? value;
}

function algorithmKey(value: string) {
  const keys: Record<string, string> = {
    Random: 'random',
    'Rule-Based': 'rule_based',
    'Risk-Aware A*': 'risk_aware_astar',
    'Tabular Q-Learning': 'tabular_q',
    'Feature-Based Q-Learning': 'feature_q',
    'Feature-Risk A*': 'feature_risk_astar',
  };
  return keys[value] ?? value;
}

function useCaseFor(value: string) {
  return algorithmUseCases[algorithmKey(value)] ?? 'Folosit ca reper în comparația cu celelalte strategii.';
}

const columnTooltips = {
  algorithm: 'Strategia evaluată în experimentul Monte Carlo.',
  success: 'Procentul episoadelor în care agentul a ajuns la obiectiv.',
  steps: 'Numărul mediu de pași executați per episod. Mai mic înseamnă trasee mai eficiente.',
  risk: 'Expunerea medie acumulată la risc pe traseu. Mai mic înseamnă navigare mai sigură.',
  reward: 'Recompensa medie totală. Include pași, coliziuni, pericol, risc și succes.',
};

export function ExperimentDashboard({
  result,
  busy = false,
  selectedObjective,
  onObjectiveChange,
}: {
  result?: MonteCarloResult;
  busy?: boolean;
  selectedObjective?: OptimizationObjective;
  onObjectiveChange?: (objective: OptimizationObjective) => void;
}) {
  if (busy) {
    return (
      <section className="panel-card comparison-dashboard dashboard-loading">
        <h2><BarChart3 size={18} /> Dashboard comparativ</h2>
        <p className="dashboard-caption">
          Monte Carlo rulează pe hărți generate. Poate dura câteva secunde când sunt incluși agenți care învață.
        </p>
        <div className="loading-row"><i /> Se compară agenții...</div>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="panel-card comparison-dashboard">
        <h2><BarChart3 size={18} /> Dashboard comparativ</h2>
        <p className="muted">Rulează comparația Monte Carlo pentru a vedea metrici statistice pe hărți generate.</p>
      </section>
    );
  }

  const sortedRows = [...result.summary.agents].sort((a, b) => {
    if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
    return a.average_risk_exposure - b.average_risk_exposure;
  });
  const maxRisk = Math.max(1, ...sortedRows.map((row) => row.average_risk_exposure));
  const bestSuccess = Math.max(...sortedRows.map((row) => row.success_rate));
  const bestRisk = Math.min(...sortedRows.map((row) => row.average_risk_exposure));
  const bestSteps = Math.min(...sortedRows.map((row) => row.average_steps));
  return (
    <section className="panel-card comparison-dashboard">
      <h2><BarChart3 size={18} /> Dashboard comparativ</h2>
      <p className="dashboard-caption">
        Monte Carlo compară fiecare agent pe hărți generate și rezumă succesul, eficiența traseului și expunerea la risc.
      </p>
      <RecommendationPanel
        result={result}
        selectedObjective={selectedObjective}
        onObjectiveChange={onObjectiveChange}
      />
      <AiAnalystPanel result={result} />
      <div className="comparison-table">
        <div className="table-head">
          <span><TooltipLabel text={columnTooltips.algorithm}>Algoritm</TooltipLabel></span>
          <span><TooltipLabel text={columnTooltips.success}>Succes</TooltipLabel></span>
          <span><TooltipLabel text={columnTooltips.steps}>Pași</TooltipLabel></span>
          <span><TooltipLabel text={columnTooltips.risk}>Risc</TooltipLabel></span>
          <span><TooltipLabel text={columnTooltips.reward}>Recompensă</TooltipLabel></span>
        </div>
        {sortedRows.map((row) => (
          <div className="table-row" key={row.algorithm}>
            <div className="algorithm-cell">
              <strong>{algorithmLabel(row.algorithm)}</strong>
              <em>{useCaseFor(row.algorithm)}</em>
            </div>
            <span className={row.success_rate === bestSuccess ? 'winner-cell' : ''}>{pct(row.success_rate)}</span>
            <span className={row.average_steps === bestSteps ? 'winner-cell' : ''}>{num(row.average_steps)}</span>
            <span className={row.average_risk_exposure === bestRisk ? 'winner-cell' : ''}>{num(row.average_risk_exposure)}</span>
            <span>{num(row.average_reward)}</span>
          </div>
        ))}
      </div>
      <div className="bar-list">
        {sortedRows.map((row) => (
          <div key={row.algorithm}>
            <label>
              <span><TooltipLabel text={columnTooltips.success}>{algorithmLabel(row.algorithm)} - succes</TooltipLabel></span>
              <b>{pct(row.success_rate)}</b>
            </label>
            <div className="bar"><i style={{ width: `${row.success_rate * 100}%` }} /></div>
          </div>
        ))}
        {sortedRows.map((row) => (
          <div key={`${row.algorithm}-risk`}>
            <label>
              <span><TooltipLabel text={columnTooltips.risk}>{algorithmLabel(row.algorithm)} - expunere la risc</TooltipLabel></span>
              <b>{num(row.average_risk_exposure)}</b>
            </label>
            <div className="bar risk"><i style={{ width: `${(row.average_risk_exposure / maxRisk) * 100}%` }} /></div>
          </div>
        ))}
      </div>
    </section>
  );
}
