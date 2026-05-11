import { useMemo, useState } from 'react';
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { TooltipLabel } from '../TooltipLabel';
import type { MonteCarloResult } from '../types';
import {
  CHART_THEME,
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

const METRIC_TOOLTIPS: Record<MetricKey, string> = {
  total_reward: 'Recompensa totală a episodului, incluzând bonusuri și penalizări.',
  steps: 'Numărul de pași executați până la succes, eșec sau timeout.',
  total_risk_exposure: 'Suma riscului întâlnit pe traseu; valori mai mici indică rute mai sigure.',
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
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Distribuții per agent</h2>
          <p className="mc-card__caption">
            <TooltipLabel text="Q1-Q3: intervalul dintre percentila 25 și percentila 75, adică jumătatea centrală a episoadelor.">
              Cutia
            </TooltipLabel>: cuartilele 25-75.{' '}
            <TooltipLabel text="Whisker-ele arată percentilele 5-95, reducând efectul episoadelor extreme.">
              Whisker-ele
            </TooltipLabel>: percentilele 5-95.{' '}
            <TooltipLabel text="Media aritmetică a valorilor pe toate episoadele agentului.">
              Punctul portocaliu
            </TooltipLabel>: media.
          </p>
        </div>
        <select
          className="mc-select"
          value={metric}
          onChange={(event) => setMetric(event.target.value as MetricKey)}
        >
          {Object.entries(METRIC_LABELS).map(([value, label]) => (
            <option value={value} key={value}>{label}</option>
          ))}
        </select>
      </header>

      <div className="mc-chart">
        <ResponsiveContainer>
          <ComposedChart data={data} margin={{ top: 10, right: 24, bottom: 24, left: 16 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis
              dataKey="label"
              tick={{ fill: CHART_THEME.axis, fontSize: 12 }}
              interval={0}
              angle={-12}
              dy={10}
              height={70}
            />
            <YAxis
              tick={{ fill: CHART_THEME.axis, fontSize: 12 }}
              label={{ value: METRIC_LABELS[metric], angle: -90, position: 'insideLeft', fill: CHART_THEME.axisLabel, fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: 8, color: CHART_THEME.tooltipText }}
              formatter={(value, name) => [formatNumber(Number(value)), String(name)]}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: CHART_THEME.axis }} />
            <Bar dataKey="whiskerLow" stackId="box" fill="transparent" name="p5" legendType="none" />
            <Bar dataKey="boxLow" stackId="box" fill="transparent" name="p25" legendType="none" />
            <Bar dataKey="boxHigh" stackId="box" name="p25-p75 (cutie)" fill="#bae6fd" stroke="#0284c7" />
            <Bar dataKey="whiskerHigh" stackId="box" name="p75-p95" fill="#e0f2fe" stroke="#38bdf8" strokeDasharray="3 2" />
            <Line type="monotone" dataKey="p50" stroke={CHART_THEME.median} strokeWidth={0} dot={{ r: 4, fill: CHART_THEME.median }} name="Mediană" />
            <Line type="monotone" dataKey="mean" stroke={CHART_THEME.mean} strokeWidth={0} dot={{ r: 5, fill: CHART_THEME.mean }} name="Medie" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mc-stat-grid">
        {data.map((row) => (
          <div key={row.algorithm} className="mc-stat-card" style={{ borderLeftColor: row.color }}>
            <div className="mc-stat-card__title">{row.label}</div>
            <div className="mc-stat-card__row">
              <TooltipLabel text={METRIC_TOOLTIPS[metric]}>media</TooltipLabel> {formatNumber(row.mean)} ·{' '}
              <TooltipLabel text="Mediana este percentila 50: jumătate din episoade au valori sub acest prag.">mediană</TooltipLabel> {formatNumber(row.p50)}
            </div>
            <div className="mc-stat-card__row">
              <TooltipLabel text="Intervalul intercuartilic: percentila 25 până la percentila 75.">p25-p75</TooltipLabel>: {formatNumber(row.p25)} … {formatNumber(row.p75)}
            </div>
            <div className="mc-stat-card__row">min {formatNumber(row.min)} · max {formatNumber(row.max)}</div>
            <div className="mc-stat-card__row">n = {row.count}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
