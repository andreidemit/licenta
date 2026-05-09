import { BarChart3 } from 'lucide-react';
import type { MonteCarloResult } from './types';

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
  };
  return labels[value] ?? value;
}

export function ExperimentDashboard({ result, busy = false }: { result?: MonteCarloResult; busy?: boolean }) {
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
      <div className="comparison-table">
        <div className="table-head">
          <span>Algoritm</span><span>Succes</span><span>Pași</span><span>Risc</span><span>Recompensă</span>
        </div>
        {sortedRows.map((row) => (
          <div className="table-row" key={row.algorithm}>
            <strong>{algorithmLabel(row.algorithm)}</strong>
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
            <label><span>{algorithmLabel(row.algorithm)} - succes</span><b>{pct(row.success_rate)}</b></label>
            <div className="bar"><i style={{ width: `${row.success_rate * 100}%` }} /></div>
          </div>
        ))}
        {sortedRows.map((row) => (
          <div key={`${row.algorithm}-risk`}>
            <label><span>{algorithmLabel(row.algorithm)} - expunere la risc</span><b>{num(row.average_risk_exposure)}</b></label>
            <div className="bar risk"><i style={{ width: `${(row.average_risk_exposure / maxRisk) * 100}%` }} /></div>
          </div>
        ))}
      </div>
    </section>
  );
}
