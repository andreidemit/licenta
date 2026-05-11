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
import { TooltipLabel } from '../TooltipLabel';
import type { MonteCarloResult } from '../types';
import { CHART_THEME, algorithmLabel, formatPercent, groupEpisodesByAlgorithm } from './analysisHelpers';

const SEGMENT_COLORS = {
  success: '#16a34a',
  collision: '#ea580c',
  danger: '#dc2626',
  timeout: '#7c3aed',
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
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Distribuția evenimentelor de finalizare</h2>
          <p className="mc-card__caption">
            Procent din episoadele unui agent:{' '}
            <TooltipLabel text="Agentul ajunge la obiectiv.">succes</TooltipLabel> vs{' '}
            <TooltipLabel text="Agentul intră într-o celulă periculoasă.">intrare în pericol</TooltipLabel> vs{' '}
            <TooltipLabel text="Agentul încearcă să intre într-un perete sau obstacol.">coliziune</TooltipLabel> vs{' '}
            <TooltipLabel text="Agentul atinge limita maximă de pași fără finalizare.">timeout</TooltipLabel>.
          </p>
        </div>
      </header>
      <div className="mc-chart mc-chart--short">
        <ResponsiveContainer>
          <BarChart data={data} layout="vertical" margin={{ top: 10, right: 24, bottom: 10, left: 80 }} stackOffset="expand">
            <CartesianGrid strokeDasharray="3 3" stroke={CHART_THEME.grid} />
            <XAxis type="number" tickFormatter={(value) => formatPercent(Number(value))} tick={{ fill: CHART_THEME.axis, fontSize: 12 }} domain={[0, 1]} />
            <YAxis type="category" dataKey="label" tick={{ fill: CHART_THEME.axis, fontSize: 12 }} width={140} />
            <Tooltip
              contentStyle={{ background: CHART_THEME.tooltipBg, border: `1px solid ${CHART_THEME.tooltipBorder}`, borderRadius: 8, color: CHART_THEME.tooltipText }}
              formatter={(value, name) => [formatPercent(Number(value)), String(name)]}
            />
            <Legend wrapperStyle={{ fontSize: 12, color: CHART_THEME.axis }} />
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
