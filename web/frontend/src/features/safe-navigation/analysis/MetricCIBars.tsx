import { useMemo, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ErrorBar,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { MonteCarloResult, MonteCarloSummaryRow } from '../types';
import { algorithmLabel, colorFor, formatNumber, formatPercent } from './analysisHelpers';

type MetricSpec = {
  id: 'success_rate' | 'collision_rate' | 'danger_entry_rate' | 'timeout_rate' | 'average_steps' | 'average_risk_exposure' | 'average_reward';
  label: string;
  format: 'percent' | 'number';
  ciLow?: keyof MonteCarloSummaryRow;
  ciHigh?: keyof MonteCarloSummaryRow;
  distribution?: 'reward_distribution' | 'steps_distribution' | 'risk_distribution';
};

const METRICS: MetricSpec[] = [
  {
    id: 'success_rate',
    label: 'Rată de succes',
    format: 'percent',
    ciLow: 'success_rate_ci95_low',
    ciHigh: 'success_rate_ci95_high',
  },
  {
    id: 'collision_rate',
    label: 'Rată coliziuni',
    format: 'percent',
    ciLow: 'collision_rate_ci95_low',
    ciHigh: 'collision_rate_ci95_high',
  },
  {
    id: 'danger_entry_rate',
    label: 'Rată intrări în pericol',
    format: 'percent',
    ciLow: 'danger_entry_rate_ci95_low',
    ciHigh: 'danger_entry_rate_ci95_high',
  },
  {
    id: 'timeout_rate',
    label: 'Rată timeout',
    format: 'percent',
    ciLow: 'timeout_rate_ci95_low',
    ciHigh: 'timeout_rate_ci95_high',
  },
  { id: 'average_reward', label: 'Recompensă medie', format: 'number', distribution: 'reward_distribution' },
  { id: 'average_steps', label: 'Pași medii', format: 'number', distribution: 'steps_distribution' },
  { id: 'average_risk_exposure', label: 'Expunere medie la risc', format: 'number', distribution: 'risk_distribution' },
];

export function MetricCIBars({ result }: { result: MonteCarloResult }) {
  const [metricId, setMetricId] = useState<MetricSpec['id']>('success_rate');
  const metric = METRICS.find((item) => item.id === metricId) ?? METRICS[0];

  const data = useMemo(() => {
    return result.summary.agents.map((row) => {
      const value = Number(row[metric.id] ?? 0);
      let low = value;
      let high = value;
      if (metric.ciLow && metric.ciHigh) {
        low = Number(row[metric.ciLow] ?? value);
        high = Number(row[metric.ciHigh] ?? value);
      } else if (metric.distribution && row[metric.distribution]) {
        low = row[metric.distribution]!.ci95_low;
        high = row[metric.distribution]!.ci95_high;
      }
      const errorBelow = Math.max(0, value - low);
      const errorAbove = Math.max(0, high - value);
      return {
        algorithm: row.algorithm,
        label: algorithmLabel(row.algorithm),
        color: colorFor(row.algorithm),
        value,
        low,
        high,
        error: [errorBelow, errorAbove] as [number, number],
      };
    });
  }, [result, metric]);

  const formatValue = (value: number) =>
    metric.format === 'percent' ? formatPercent(value) : formatNumber(value);

  return (
    <section className="panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
        <div>
          <h2 style={{ margin: 0 }}>Bare cu interval de încredere 95%</h2>
          <p className="muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
            Bara este media; whisker-ul este intervalul de încredere bootstrap (1000 resample-uri).
          </p>
        </div>
        <select
          value={metricId}
          onChange={(event) => setMetricId(event.target.value as MetricSpec['id'])}
          style={{
            background: 'var(--surface-strong, #1f2937)',
            color: 'inherit',
            border: '1px solid var(--border, #334155)',
            borderRadius: 8,
            padding: '0.4rem 0.6rem',
          }}
        >
          {METRICS.map((item) => (
            <option key={item.id} value={item.id}>{item.label}</option>
          ))}
        </select>
      </header>

      <div style={{ width: '100%', height: 320 }}>
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 24, bottom: 24, left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
            <XAxis dataKey="label" tick={{ fill: '#cbd5f5', fontSize: 12 }} interval={0} angle={-12} dy={8} height={70} />
            <YAxis
              tick={{ fill: '#cbd5f5', fontSize: 12 }}
              tickFormatter={(value) => formatValue(Number(value))}
              label={{ value: metric.label, angle: -90, position: 'insideLeft', fill: '#cbd5f5' }}
            />
            <Tooltip
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8 }}
              formatter={(value) => formatValue(Number(value))}
              labelFormatter={(label) => String(label)}
            />
            <Bar dataKey="value" name={metric.label} radius={[6, 6, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.algorithm} fill={entry.color} />
              ))}
              <ErrorBar dataKey="error" width={6} stroke="#facc15" strokeWidth={1.5} direction="y" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ textAlign: 'left', color: 'rgba(148,163,184,0.85)' }}>
              <th style={{ padding: '0.4rem 0.5rem' }}>Agent</th>
              <th style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>Valoare</th>
              <th style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>CI 95% jos</th>
              <th style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>CI 95% sus</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.algorithm} style={{ borderTop: '1px solid rgba(148,163,184,0.15)' }}>
                <td style={{ padding: '0.4rem 0.5rem', color: row.color, fontWeight: 600 }}>{row.label}</td>
                <td style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>{formatValue(row.value)}</td>
                <td style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>{formatValue(row.low)}</td>
                <td style={{ padding: '0.4rem 0.5rem', textAlign: 'right' }}>{formatValue(row.high)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
