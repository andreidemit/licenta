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
import { TooltipLabel } from '../TooltipLabel';
import type { MonteCarloResult } from '../types';
import { CHART_THEME, algorithmLabel, colorFor, formatNumber, groupEpisodesByAlgorithm } from './analysisHelpers';

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
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Trade-off risc vs recompensă</h2>
          <p className="mc-card__caption">
            Un punct = un episod.{' '}
            <TooltipLabel text="Recompensă mare și risc mic: traseu bun atât ca eficiență, cât și ca siguranță.">
              Sus-stânga
            </TooltipLabel>{' '}
            indică un agent eficient și sigur;{' '}
            <TooltipLabel text="Recompensă mică și risc mare: traseu costisitor sau nesigur.">
              jos-dreapta
            </TooltipLabel>{' '}
            este zona costisitoare.
          </p>
        </div>
      </header>
      <div className="mc-chart mc-chart--tall">
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 16, right: 24, bottom: 36, left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis
              type="number"
              dataKey="risk"
              name="Risc cumulat"
              tick={{ fill: CHART_THEME.axis, fontSize: 12 }}
              label={{ value: 'Expunere la risc', position: 'insideBottom', dy: 16, fill: CHART_THEME.axisLabel, fontSize: 12 }}
            />
            <YAxis
              type="number"
              dataKey="reward"
              name="Recompensă"
              tick={{ fill: CHART_THEME.axis, fontSize: 12 }}
              label={{ value: 'Recompensă totală', angle: -90, position: 'insideLeft', fill: CHART_THEME.axisLabel, fontSize: 12 }}
            />
            <ZAxis type="number" dataKey="steps" range={[40, 200]} name="Pași" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: 8, color: CHART_THEME.tooltipText, fontSize: 12 }}
              formatter={(value, name) => [formatNumber(Number(value)), String(name)]}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: CHART_THEME.axis }} />
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
