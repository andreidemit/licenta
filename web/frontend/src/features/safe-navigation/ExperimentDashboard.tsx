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
      <h2><BarChart3 size={18} /> Comparison Dashboard</h2>
      <p className="dashboard-caption">
        Monte Carlo compares each agent across generated maps and summarizes success, path efficiency and risk exposure.
      </p>
      <div className="comparison-table">
        <div className="table-head">
          <span>Algorithm</span><span>Success</span><span>Steps</span><span>Risk</span><span>Reward</span>
        </div>
        {sortedRows.map((row) => (
          <div className="table-row" key={row.algorithm}>
            <strong>{row.algorithm}</strong>
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
            <label><span>{row.algorithm} success</span><b>{pct(row.success_rate)}</b></label>
            <div className="bar"><i style={{ width: `${row.success_rate * 100}%` }} /></div>
          </div>
        ))}
        {sortedRows.map((row) => (
          <div key={`${row.algorithm}-risk`}>
            <label><span>{row.algorithm} risk exposure</span><b>{num(row.average_risk_exposure)}</b></label>
            <div className="bar risk"><i style={{ width: `${(row.average_risk_exposure / maxRisk) * 100}%` }} /></div>
          </div>
        ))}
      </div>
    </section>
  );
}
