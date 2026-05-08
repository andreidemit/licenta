import { Activity, AlertTriangle, CheckCircle2, Gauge, Route } from 'lucide-react';
import type { SafeEpisodeResult, SafeNavigationConfig } from './types';

function fmt(value?: number, digits = 1) {
  return value === undefined || Number.isNaN(value) ? '-' : value.toFixed(digits);
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
      <section className="panel-card">
        <h2><Activity size={18} /> Live Metrics</h2>
        <div className="status-row">
          <span>{config.algorithm.replace(/_/g, ' ')}</span>
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
