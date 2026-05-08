import { BarChart3 } from 'lucide-react';
import type { MonteCarloResult } from './types';

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function num(value: number) {
  return value.toFixed(1);
}

export function ExperimentDashboard({ result }: { result?: MonteCarloResult }) {
  if (!result) {
    return (
      <section className="panel-card comparison-dashboard">
        <h2><BarChart3 size={18} /> Comparison Dashboard</h2>
        <p className="muted">Run Monte Carlo comparison to see statistical metrics across generated maps.</p>
      </section>
    );
  }

  const maxRisk = Math.max(1, ...result.summary.agents.map((row) => row.average_risk_exposure));
  return (
    <section className="panel-card comparison-dashboard">
      <h2><BarChart3 size={18} /> Comparison Dashboard</h2>
      <div className="comparison-table">
        <div className="table-head">
          <span>Algorithm</span><span>Success</span><span>Steps</span><span>Risk</span><span>Reward</span>
        </div>
        {result.summary.agents.map((row) => (
          <div className="table-row" key={row.algorithm}>
            <strong>{row.algorithm}</strong>
            <span>{pct(row.success_rate)}</span>
            <span>{num(row.average_steps)}</span>
            <span>{num(row.average_risk_exposure)}</span>
            <span>{num(row.average_reward)}</span>
          </div>
        ))}
      </div>
      <div className="bar-list">
        {result.summary.agents.map((row) => (
          <div key={row.algorithm}>
            <label>{row.algorithm} success</label>
            <div className="bar"><i style={{ width: `${row.success_rate * 100}%` }} /></div>
          </div>
        ))}
        {result.summary.agents.map((row) => (
          <div key={`${row.algorithm}-risk`}>
            <label>{row.algorithm} risk exposure</label>
            <div className="bar risk"><i style={{ width: `${(row.average_risk_exposure / maxRisk) * 100}%` }} /></div>
          </div>
        ))}
      </div>
    </section>
  );
}
