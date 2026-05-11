import { useMemo } from 'react';
import type { MonteCarloResult } from '../types';
import { algorithmLabel, colorFor, formatPercent } from './analysisHelpers';

function colorScale(value: number) {
  const clamped = Math.max(0, Math.min(1, value));
  const hue = clamped * 130; // 0=red, 130=green
  return `hsl(${hue}, 65%, ${65 - clamped * 12}%)`;
}

export function PerMapHeatmap({ result }: { result: MonteCarloResult }) {
  const data = useMemo(() => {
    const perMap = result.summary.per_map ?? [];
    const seeds = Array.from(new Set(perMap.map((row) => row.map_seed))).sort((a, b) => a - b);
    const algorithms = Array.from(new Set(perMap.map((row) => row.algorithm))).sort();
    const lookup = new Map<string, (typeof perMap)[number]>();
    for (const row of perMap) lookup.set(`${row.algorithm}::${row.map_seed}`, row);
    return { seeds, algorithms, lookup };
  }, [result]);

  if (!data.seeds.length) {
    return (
      <section className="mc-card">
        <header className="mc-card__header">
          <div>
            <h2>Heatmap per hartă</h2>
            <p className="mc-card__caption">
              Nu sunt informații per-hartă disponibile. Re-rulează Monte Carlo după actualizarea backend-ului.
            </p>
          </div>
        </header>
      </section>
    );
  }

  return (
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Heatmap per hartă (rată de succes)</h2>
          <p className="mc-card__caption">
            Verde = succes ridicat, roșu = eșec frecvent. Ajută la identificarea hărților pe care un agent specific eșuează.
          </p>
        </div>
      </header>

      <div style={{ overflowX: 'auto' }}>
        <table className="mc-heatmap">
          <thead>
            <tr>
              <th className="mc-heatmap__row-label">Agent \\ Seed</th>
              {data.seeds.map((seed) => (
                <th key={seed}>{seed}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.algorithms.map((algorithm) => (
              <tr key={algorithm}>
                <td className="mc-heatmap__row-label" style={{ color: colorFor(algorithm) }}>
                  {algorithmLabel(algorithm)}
                </td>
                {data.seeds.map((seed) => {
                  const cell = data.lookup.get(`${algorithm}::${seed}`);
                  if (!cell) {
                    return <td key={seed} className="mc-heatmap__missing">-</td>;
                  }
                  return (
                    <td
                      key={seed}
                      title={`Seed ${seed} · ${cell.episodes} episoade · succes ${formatPercent(cell.success_rate)} · risc ${cell.average_risk_exposure.toFixed(1)}`}
                      style={{ background: colorScale(cell.success_rate) }}
                    >
                      {Math.round(cell.success_rate * 100)}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mc-legend-bar">
        <span>0% succes</span>
        <div className="mc-legend-bar__track" />
        <span>100% succes</span>
      </div>
    </section>
  );
}
