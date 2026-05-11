import { useMemo, useState } from 'react';
import type { MonteCarloResult } from '../types';
import { algorithmLabel, buildOccupancyHeatmap, colorFor, groupEpisodesByAlgorithm } from './analysisHelpers';

function inferGridSize(result: MonteCarloResult): { rows: number; cols: number } {
  const config = result.config ?? {};
  const fromConfig = {
    rows: Number((config as Record<string, unknown>).rows ?? 0),
    cols: Number((config as Record<string, unknown>).cols ?? 0),
  };
  if (fromConfig.rows > 0 && fromConfig.cols > 0) return fromConfig;

  let maxRow = 0;
  let maxCol = 0;
  for (const episode of result.episodes) {
    for (const position of episode.path ?? []) {
      if (position[0] > maxRow) maxRow = position[0];
      if (position[1] > maxCol) maxCol = position[1];
    }
  }
  return { rows: maxRow + 1, cols: maxCol + 1 };
}

export function OccupancyHeatmap({ result }: { result: MonteCarloResult }) {
  const grouped = useMemo(() => groupEpisodesByAlgorithm(result), [result]);
  const algorithms = useMemo(() => Object.keys(grouped).sort(), [grouped]);
  const [active, setActive] = useState<string>(algorithms[0] ?? '');
  const { rows, cols } = useMemo(() => inferGridSize(result), [result]);

  const heatmap = useMemo(() => {
    if (!active) return { matrix: [], max: 0 };
    return buildOccupancyHeatmap(grouped[active] ?? [], rows, cols);
  }, [active, grouped, rows, cols]);

  if (!algorithms.length) {
    return (
      <section className="mc-card">
        <header className="mc-card__header">
          <div>
            <h2>Heatmap de ocupare</h2>
            <p className="mc-card__caption">Nu există episoade înregistrate.</p>
          </div>
        </header>
      </section>
    );
  }

  const cellSize = Math.max(8, Math.min(28, Math.floor(520 / Math.max(rows, cols))));
  const accent = colorFor(active);

  return (
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Heatmap de ocupare a grilei</h2>
          <p className="mc-card__caption">
            Frecvența cu care fiecare celulă este vizitată de agentul selectat, agregat pe toate episoadele MC.
          </p>
        </div>
        <select
          className="mc-select"
          value={active}
          onChange={(event) => setActive(event.target.value)}
        >
          {algorithms.map((algorithm) => (
            <option key={algorithm} value={algorithm}>{algorithmLabel(algorithm)}</option>
          ))}
        </select>
      </header>

      <div className="mc-occupancy">
        <svg
          className="mc-occupancy__svg"
          width={cols * cellSize + 2}
          height={rows * cellSize + 2}
        >
          {heatmap.matrix.map((row, rowIndex) => (
            row.map((value, colIndex) => {
              const intensity = heatmap.max > 0 ? value / heatmap.max : 0;
              return (
                <rect
                  key={`${rowIndex}-${colIndex}`}
                  x={colIndex * cellSize + 1}
                  y={rowIndex * cellSize + 1}
                  width={cellSize - 1}
                  height={cellSize - 1}
                  fill={accent}
                  fillOpacity={intensity}
                  stroke="rgba(15,23,42,0.08)"
                >
                  <title>{`(${rowIndex}, ${colIndex}): ${value} vizite`}</title>
                </rect>
              );
            })
          ))}
        </svg>
        <div className="mc-occupancy__footer">
          <span>0 vizite</span>
          <span>maxim: {heatmap.max} vizite</span>
        </div>
      </div>
    </section>
  );
}
