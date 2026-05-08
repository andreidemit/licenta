import { Activity, AlertTriangle, CheckCircle2, Gauge, Route } from 'lucide-react';
import type { SafeEpisodeResult, SafeNavigationConfig } from './types';

function fmt(value?: number, digits = 1) {
  return value === undefined || Number.isNaN(value) ? '-' : value.toFixed(digits);
}

function algorithmLabel(value: string) {
  const labels: Record<string, string> = {
    random: 'Random',
    rule_based: 'Rule-Based',
    astar: 'A*',
    risk_aware_astar: 'Risk-Aware A*',
    tabular_q_learning: 'Tabular Q-Learning',
    feature_q_learning: 'Feature-Based Q-Learning',
  };
  return labels[value] ?? value;
}

export function MetricsPanel({
  config,
  result,
}: {
  config: SafeNavigationConfig;
  result?: SafeEpisodeResult;
}) {
  const status = result ? (result.success ? 'Success' : result.timeout ? 'Timeout' : 'Failed') : 'Ready';
  return (
    <aside className="metrics-panel">
      <section className="panel-card run-summary-card">
        <div>
          <small>Current Algorithm</small>
          <strong>{algorithmLabel(config.algorithm)}</strong>
        </div>
        <b className={`badge ${status.toLowerCase()}`}>{status}</b>
        <dl>
          <div><dt>Steps</dt><dd>{result?.steps ?? '-'}</dd></div>
          <div><dt>Reward</dt><dd>{fmt(result?.total_reward)}</dd></div>
          <div><dt>Risk</dt><dd>{fmt(result?.total_risk_exposure)}</dd></div>
        </dl>
      </section>

      <section className="panel-card">
        <h2><Activity size={18} /> Live Metrics</h2>
        <div className="status-row">
          <span>{algorithmLabel(config.algorithm)}</span>
          <b className={`badge ${status.toLowerCase()}`}>{status}</b>
        </div>
        <div className="metric-grid">
          <div><small>Steps</small><strong>{result?.steps ?? '-'}</strong></div>
          <div><small>Total reward</small><strong>{fmt(result?.total_reward)}</strong></div>
          <div><small>Total cost</small><strong>{fmt(result?.total_cost)}</strong></div>
          <div><small>Risk exposure</small><strong>{fmt(result?.total_risk_exposure)}</strong></div>
          <div><small>Collisions</small><strong>{result?.collisions ?? '-'}</strong></div>
          <div><small>Danger entries</small><strong>{result?.danger_entries ?? '-'}</strong></div>
          <div><small>Path length</small><strong>{result?.path_length ?? '-'}</strong></div>
          <div><small>Runtime</small><strong>{fmt(result?.computation_time_ms, 2)} ms</strong></div>
        </div>
      </section>

      <section className="panel-card story-card">
        <h2><Route size={18} /> Experimental Story</h2>
        <p><CheckCircle2 size={15} /> Tabular Q-Learning memorizes one map well, then struggles when coordinates change.</p>
        <p><Gauge size={15} /> A* is fast on unseen maps, but optimizes distance more than safety.</p>
        <p><AlertTriangle size={15} /> Risk-Aware A* trades extra steps for lower exposure near danger.</p>
        <p><Activity size={15} /> Feature-Based Q-Learning learns local safety patterns that transfer better.</p>
      </section>
    </aside>
  );
}
