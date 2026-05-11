import { useMemo } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { MonteCarloResult } from '../types';
import { algorithmLabel, formatPercent, groupEpisodesByAlgorithm } from './analysisHelpers';

const SEGMENT_COLORS = {
  success: '#22c55e',
  collision: '#f97316',
  danger: '#ef4444',
  timeout: '#a855f7',
  other: '#64748b',
};

export function FailureBreakdown({ result }: { result: MonteCarloResult }) {
  const data = useMemo(() => {
    const grouped = groupEpisodesByAlgorithm(result);
    return Object.entries(grouped).map(([algorithm, episodes]) => {
      const total = episodes.length || 1;
      let success = 0;
      let collision = 0;
      let danger = 0;
      let timeout = 0;
      let other = 0;
      for (const episode of episodes) {
        if (episode.success) {
          success += 1;
          continue;
        }
        if (episode.timeout) {
          timeout += 1;
          continue;
        }
        if (episode.danger_entries > 0) {
          danger += 1;
          continue;
        }
        if (episode.collisions > 0) {
          collision += 1;
          continue;
        }
        other += 1;
      }
      return {
        algorithm,
        label: algorithmLabel(algorithm),
        success: success / total,
        collision: collision / total,
        danger: danger / total,
        timeout: timeout / total,
        other: other / total,
        total,
      };
    });
  }, [result]);

  return (
    <section className="panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <header>
        <h2 style={{ margin: 0 }}>Distribuția evenimentelor de finalizare</h2>
        <p className="muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
          Procentaj din episoadele unui agent: succes vs intrare în pericol vs coliziune vs timeout.
        </p>
      </header>
      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer>
          <BarChart data={data} layout="vertical" margin={{ top: 10, right: 24, bottom: 10, left: 80 }} stackOffset="expand">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
            <XAxis type="number" tickFormatter={(value) => formatPercent(Number(value))} tick={{ fill: '#cbd5f5', fontSize: 12 }} domain={[0, 1]} />
            <YAxis type="category" dataKey="label" tick={{ fill: '#cbd5f5', fontSize: 12 }} width={140} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
              formatter={(value, name) => [formatPercent(Number(value)), String(name)]}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="success" stackId="a" fill={SEGMENT_COLORS.success} name="Succes" />
            <Bar dataKey="danger" stackId="a" fill={SEGMENT_COLORS.danger} name="Intrare în pericol" />
            <Bar dataKey="collision" stackId="a" fill={SEGMENT_COLORS.collision} name="Coliziune" />
            <Bar dataKey="timeout" stackId="a" fill={SEGMENT_COLORS.timeout} name="Timeout" />
            <Bar dataKey="other" stackId="a" fill={SEGMENT_COLORS.other} name="Altă încheiere" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
