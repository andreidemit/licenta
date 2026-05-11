import { useMemo } from 'react';
import type { MonteCarloResult } from '../types';
import { algorithmLabel, colorFor, formatPercent } from './analysisHelpers';

function colorScale(value: number) {
  const clamped = Math.max(0, Math.min(1, value));
  const hue = clamped * 130; // 0=red, 130=green
  return `hsl(${hue}, 70%, ${30 + clamped * 25}%)`;
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
      <section className="panel-card">
        <h2 style={{ margin: 0 }}>Heatmap per hartă</h2>
        <p className="muted" style={{ marginTop: '0.5rem' }}>
          Nu sunt informații per-hartă disponibile. Re-rulează Monte Carlo după actualizarea backend-ului.
        </p>
      </section>
    );
  }

  return (
    <section className="panel-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <header>
        <h2 style={{ margin: 0 }}>Heatmap per hartă (rată de succes)</h2>
        <p className="muted" style={{ margin: '0.25rem 0 0', fontSize: '0.85rem' }}>
          Verde = succes ridicat, roșu = eșec frecvent. Identifică pe ce hărți specifice un agent eșuează.
        </p>
      </header>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ borderCollapse: 'separate', borderSpacing: 4, fontSize: 12 }}>
          <thead>
            <tr>
              <th style={{ textAlign: 'left', padding: '0 0.5rem', color: 'rgba(148,163,184,0.85)' }}>Agent \\ Seed</th>
              {data.seeds.map((seed) => (
                <th key={seed} style={{ padding: '0 0.4rem', color: 'rgba(148,163,184,0.85)', fontWeight: 500 }}>
                  {seed}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.algorithms.map((algorithm) => (
              <tr key={algorithm}>
                <td
                  style={{
                    padding: '0.3rem 0.6rem',
                    color: colorFor(algorithm),
                    fontWeight: 600,
                    whiteSpace: 'nowrap',
                  }}
                >
                  {algorithmLabel(algorithm)}
                </td>
                {data.seeds.map((seed) => {
                  const cell = data.lookup.get(`${algorithm}::${seed}`);
                  if (!cell) {
                    return (
                      <td
                        key={seed}
                        style={{
                          width: 56,
                          height: 36,
                          background: 'rgba(148,163,184,0.1)',
                          borderRadius: 6,
                          textAlign: 'center',
                          color: 'rgba(148,163,184,0.5)',
                        }}
                      >
                        -
                      </td>
                    );
                  }
                  return (
                    <td
                      key={seed}
                      title={`Seed ${seed} · ${cell.episodes} episoade · succes ${formatPercent(cell.success_rate)} · risc ${cell.average_risk_exposure.toFixed(1)}`}
                      style={{
                        width: 56,
                        height: 36,
                        background: colorScale(cell.success_rate),
                        borderRadius: 6,
                        textAlign: 'center',
                        color: '#0b1220',
                        fontWeight: 600,
                      }}
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

      <footer style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.78rem', color: 'rgba(148,163,184,0.85)' }}>
        <span>0%</span>
        <div
          style={{
            flex: 1,
            height: 12,
            borderRadius: 6,
            background: 'linear-gradient(to right, hsl(0,70%,30%), hsl(65,70%,42%), hsl(130,70%,55%))',
          }}
        />
        <span>100%</span>
      </footer>
    </section>
  );
}
