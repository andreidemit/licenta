import { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { MonteCarloResult } from '../types';
import {
  algorithmLabel,
  colorFor,
  computeBoxStats,
  formatNumber,
  groupEpisodesByAlgorithm,
} from './analysisHelpers';

type MetricKey = 'total_reward' | 'steps' | 'total_risk_exposure';

const METRIC_LABELS: Record<MetricKey, string> = {
  total_reward: 'Recompensă totală',
  steps: 'Pași per episod',
  total_risk_exposure: 'Expunere la risc',
};

export function RewardDistribution({ result }: { result: MonteCarloResult }) {
  const [metric, setMetric] = useState<MetricKey>('total_reward');

  const data = useMemo(() => {
    const grouped = groupEpisodesByAlgorithm(result);
    return Object.entries(grouped).map(([algorithm, episodes]) => {
      const values = episodes.map((episode) => Number(episode[metric] ?? 0));
      const stats = computeBoxStats(values);
      return {
        algorithm,
        label: algorithmLabel(algorithm),
        color: colorFor(algorithm),
        ...stats,
        whiskerLow: stats.p05,
        boxLow: stats.p25,
        boxHigh: stats.p75 - stats.p25,
        whiskerHigh: stats.p95 - stats.p75,
      };
    });
  }, [result, metric]);

  return (
    <section className="panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div>
          <h2 style={{ margin: 0 }}>Distribuții per agent</h2>
          <p className="muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
            Cutia: cuartile 25-75. Whisker-ele: percentile 5-95. Punctul: media.
          </p>
        </div>
        <select
          value={metric}
          onChange={(event) => setMetric(event.target.value as MetricKey)}
          style={{
            background: 'var(--surface-strong, #1f2937)',
            color: 'inherit',
            border: '1px solid var(--border, #334155)',
            borderRadius: 8,
            padding: '0.4rem 0.6rem',
          }}
        >
          {Object.entries(METRIC_LABELS).map(([value, label]) => (
            <option value={value} key={value}>{label}</option>
          ))}
        </select>
      </header>

      <div style={{ width: '100%', height: 360 }}>
        <ResponsiveContainer>
          <ComposedChart data={data} margin={{ top: 10, right: 24, bottom: 10, left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
            <XAxis dataKey="label" tick={{ fill: '#cbd5f5', fontSize: 12 }} interval={0} angle={-12} dy={8} height={70} />
            <YAxis tick={{ fill: '#cbd5f5', fontSize: 12 }} label={{ value: METRIC_LABELS[metric], angle: -90, position: 'insideLeft', fill: '#cbd5f5' }} />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
              formatter={(value, name) => [formatNumber(Number(value)), String(name)]}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Bar dataKey="whiskerLow" stackId="box" fill="transparent" name="p5" />
            <Bar dataKey="boxLow" stackId="box" fill="transparent" name="p25" />
            <Bar dataKey="boxHigh" stackId="box" name="p25-p75 (cutie)" fill="#38bdf8" fillOpacity={0.55} stroke="#38bdf8" />
            <Bar dataKey="whiskerHigh" stackId="box" name="p75-p95" fill="#38bdf8" fillOpacity={0.18} stroke="#38bdf8" strokeDasharray="3 2" />
            <Line type="monotone" dataKey="p50" stroke="#facc15" strokeWidth={2} dot={{ r: 4, fill: '#facc15' }} name="Mediană" />
            <Line type="monotone" dataKey="mean" stroke="#f97316" strokeWidth={0} dot={{ r: 5, fill: '#f97316' }} name="Medie" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
        {data.map((row) => (
          <div
            key={row.algorithm}
            style={{
              border: `1px solid ${row.color}55`,
              borderRadius: 10,
              padding: '0.7rem 0.85rem',
              background: 'rgba(15,23,42,0.4)',
            }}
          >
            <strong style={{ color: row.color }}>{row.label}</strong>
            <div style={{ fontSize: '0.78rem', color: 'rgba(203,213,245,0.85)', marginTop: 4, lineHeight: 1.5 }}>
              <div>media {formatNumber(row.mean)} · mediană {formatNumber(row.p50)}</div>
              <div>p25-p75: {formatNumber(row.p25)} … {formatNumber(row.p75)}</div>
              <div>min {formatNumber(row.min)} · max {formatNumber(row.max)}</div>
              <div>n = {row.count}</div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
