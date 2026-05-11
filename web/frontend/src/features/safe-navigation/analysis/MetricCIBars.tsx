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
import { TooltipLabel } from '../TooltipLabel';
import type { MonteCarloResult, MonteCarloSummaryRow } from '../types';
import { CHART_THEME, algorithmLabel, colorFor, formatNumber, formatPercent } from './analysisHelpers';

type MetricSpec = {
  id:
    | 'success_rate'
    | 'collision_rate'
    | 'danger_entry_rate'
    | 'timeout_rate'
    | 'average_steps'
    | 'average_risk_exposure'
    | 'average_reward';
  label: string;
  tooltip: string;
  format: 'percent' | 'number';
  ciLow?: keyof MonteCarloSummaryRow;
  ciHigh?: keyof MonteCarloSummaryRow;
  distribution?: 'reward_distribution' | 'steps_distribution' | 'risk_distribution';
};

const METRICS: MetricSpec[] = [
  { id: 'success_rate', label: 'Rată de succes', tooltip: 'Proporția episoadelor în care agentul ajunge la obiectiv.', format: 'percent', ciLow: 'success_rate_ci95_low', ciHigh: 'success_rate_ci95_high' },
  { id: 'collision_rate', label: 'Rată coliziuni', tooltip: 'Proporția episoadelor în care apar încercări de intrare în pereți.', format: 'percent', ciLow: 'collision_rate_ci95_low', ciHigh: 'collision_rate_ci95_high' },
  { id: 'danger_entry_rate', label: 'Rată intrări în pericol', tooltip: 'Proporția episoadelor în care agentul intră în celule periculoase.', format: 'percent', ciLow: 'danger_entry_rate_ci95_low', ciHigh: 'danger_entry_rate_ci95_high' },
  { id: 'timeout_rate', label: 'Rată timeout', tooltip: 'Proporția episoadelor care ating limita de pași fără să finalizeze.', format: 'percent', ciLow: 'timeout_rate_ci95_low', ciHigh: 'timeout_rate_ci95_high' },
  { id: 'average_reward', label: 'Recompensă medie', tooltip: 'Scorul mediu total al episodului, incluzând penalizări și bonusul de succes.', format: 'number', distribution: 'reward_distribution' },
  { id: 'average_steps', label: 'Pași medii', tooltip: 'Numărul mediu de pași executați per episod.', format: 'number', distribution: 'steps_distribution' },
  { id: 'average_risk_exposure', label: 'Expunere medie la risc', tooltip: 'Riscul acumulat mediu pe traseu; valori mai mici indică rute mai sigure.', format: 'number', distribution: 'risk_distribution' },
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
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Bare cu interval de încredere 95%</h2>
          <p className="mc-card__caption">
            <TooltipLabel text="CI = confidence interval / interval de încredere. Estimează plaja probabilă a mediei reale.">
              CI 95%
            </TooltipLabel>{' '}
            pentru <TooltipLabel text={metric.tooltip}>{metric.label}</TooltipLabel>. Bara reprezintă media;
            whisker-ele indică intervalul bootstrap (1000 re-eșantionări).
          </p>
        </div>
        <select
          className="mc-select"
          value={metricId}
          onChange={(event) => setMetricId(event.target.value as MetricSpec['id'])}
        >
          {METRICS.map((item) => (
            <option key={item.id} value={item.id}>{item.label}</option>
          ))}
        </select>
      </header>

      <div className="mc-chart mc-chart--short">
        <ResponsiveContainer>
          <BarChart data={data} margin={{ top: 10, right: 24, bottom: 24, left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis dataKey="label" tick={{ fill: CHART_THEME.axis, fontSize: 12 }} interval={0} angle={-12} dy={10} height={70} />
            <YAxis
              tick={{ fill: CHART_THEME.axis, fontSize: 12 }}
              tickFormatter={(value) => formatValue(Number(value))}
              label={{ value: metric.label, angle: -90, position: 'insideLeft', fill: CHART_THEME.axisLabel, fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: 8, color: CHART_THEME.tooltipText }}
              formatter={(value) => formatValue(Number(value))}
            />
            <Bar dataKey="value" name={metric.label} radius={[6, 6, 0, 0]}>
              {data.map((entry) => (
                <Cell key={entry.algorithm} fill={entry.color} />
              ))}
              <ErrorBar dataKey="error" width={6} stroke={CHART_THEME.errorBar} strokeWidth={1.5} direction="y" />
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table className="mc-table">
          <thead>
            <tr>
              <th><TooltipLabel text="Strategia evaluată în experimentul Monte Carlo.">Agent</TooltipLabel></th>
              <th className="mc-table__num"><TooltipLabel text={metric.tooltip}>Valoare</TooltipLabel></th>
              <th className="mc-table__num"><TooltipLabel text="Limita inferioară a intervalului de încredere 95%.">CI 95% jos</TooltipLabel></th>
              <th className="mc-table__num"><TooltipLabel text="Limita superioară a intervalului de încredere 95%.">CI 95% sus</TooltipLabel></th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.algorithm}>
                <td style={{ color: row.color, fontWeight: 800 }}>{row.label}</td>
                <td className="mc-table__num">{formatValue(row.value)}</td>
                <td className="mc-table__num">{formatValue(row.low)}</td>
                <td className="mc-table__num">{formatValue(row.high)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
