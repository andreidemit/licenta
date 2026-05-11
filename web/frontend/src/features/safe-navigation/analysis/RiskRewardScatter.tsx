import { useMemo } from 'react';
import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts';
import type { MonteCarloResult } from '../types';
import { algorithmLabel, colorFor, formatNumber, groupEpisodesByAlgorithm } from './analysisHelpers';

export function RiskRewardScatter({ result }: { result: MonteCarloResult }) {
  const series = useMemo(() => {
    const grouped = groupEpisodesByAlgorithm(result);
    return Object.entries(grouped).map(([algorithm, episodes]) => ({
      algorithm,
      label: algorithmLabel(algorithm),
      color: colorFor(algorithm),
      data: episodes.map((episode) => ({
        risk: episode.total_risk_exposure,
        reward: episode.total_reward,
        steps: episode.steps,
        success: episode.success ? 'Reușit' : episode.timeout ? 'Timeout' : 'Eșec',
        algorithm,
      })),
    }));
  }, [result]);

  return (
    <section className="panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <header>
        <h2 style={{ margin: 0 }}>Trade-off risc vs recompensă</h2>
        <p className="muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
          Un punct = un episod. Sus-stânga = bun (risc mic, recompensă mare). Jos-dreapta = costisitor.
        </p>
      </header>
      <div style={{ width: '100%', height: 380 }}>
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 16, right: 24, bottom: 24, left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.18)" />
            <XAxis
              type="number"
              dataKey="risk"
              name="Risc cumulat"
              tick={{ fill: '#cbd5f5', fontSize: 12 }}
              label={{ value: 'Expunere la risc', position: 'insideBottom', dy: 16, fill: '#cbd5f5' }}
            />
            <YAxis
              type="number"
              dataKey="reward"
              name="Recompensă"
              tick={{ fill: '#cbd5f5', fontSize: 12 }}
              label={{ value: 'Recompensă totală', angle: -90, position: 'insideLeft', fill: '#cbd5f5' }}
            />
            <ZAxis type="number" dataKey="steps" range={[40, 200]} name="Pași" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ background: '#0f172a', border: '1px solid #334155', borderRadius: 8, fontSize: 12 }}
              formatter={(value, name) => [formatNumber(Number(value)), String(name)]}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {series.map((entry) => (
              <Scatter
                key={entry.algorithm}
                name={entry.label}
                data={entry.data}
                fill={entry.color}
                fillOpacity={0.7}
                stroke={entry.color}
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
