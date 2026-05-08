import { Eye, Flame, Footprints, Hash } from 'lucide-react';
import type { SafeEnvironment, SafeEpisodeResult } from './types';

const colors: Record<number, string> = {
  0: '#f8fafc',
  1: '#1f2937',
  2: '#ef4444',
  3: '#2563eb',
  4: '#22c55e',
};

type Props = {
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  showPath: boolean;
  showRisk: boolean;
  showCoordinates: boolean;
  onTogglePath: () => void;
  onToggleRisk: () => void;
  onToggleCoordinates: () => void;
};

export function GridWorldView({
  environment,
  result,
  showPath,
  showRisk,
  showCoordinates,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
}: Props) {
  if (!environment) {
    return <main className="visualization empty-stage">Generate a map to begin.</main>;
  }

  const pathSet = new Set((result?.path ?? []).map(([row, col]) => `${row}-${col}`));
  const finalPosition = result?.path?.length ? result.path[result.path.length - 1] : undefined;
  const maxRisk = Math.max(1, ...((environment.risk_map ?? []).flat()));

  return (
    <main className="visualization">
      <div className="stage-toolbar">
        <button className={showPath ? 'toggle active' : 'toggle'} onClick={onTogglePath}><Footprints size={15} /> Path</button>
        <button className={showRisk ? 'toggle active' : 'toggle'} onClick={onToggleRisk}><Flame size={15} /> Risk Heatmap</button>
        <button className={showCoordinates ? 'toggle active' : 'toggle'} onClick={onToggleCoordinates}><Hash size={15} /> Coordinates</button>
        <span><Eye size={15} /> {environment.rows}x{environment.cols}</span>
      </div>
      <div
        className="grid-world"
        style={{ gridTemplateColumns: `repeat(${environment.cols}, minmax(14px, 1fr))` }}
      >
        {environment.grid.flatMap((row, rowIndex) =>
          row.map((cell, colIndex) => {
            const key = `${rowIndex}-${colIndex}`;
            const isPath = showPath && pathSet.has(key);
            const isAgent = finalPosition?.[0] === rowIndex && finalPosition?.[1] === colIndex;
            const risk = environment.risk_map?.[rowIndex]?.[colIndex] ?? 0;
            const riskAlpha = showRisk ? Math.min(0.72, risk / maxRisk) : 0;
            return (
              <div
                key={key}
                className={`grid-cell ${isPath ? 'path-cell' : ''} ${isAgent ? 'agent-cell' : ''}`}
                style={{
                  background: `linear-gradient(rgba(248,113,113,${riskAlpha}), rgba(248,113,113,${riskAlpha})), ${colors[cell] ?? '#f8fafc'}`,
                }}
                title={`row ${rowIndex}, col ${colIndex}, risk ${risk.toFixed(1)}`}
              >
                {showCoordinates && <span>{rowIndex},{colIndex}</span>}
                {isAgent && <b />}
              </div>
            );
          }),
        )}
      </div>
      <div className="legend">
        <span><i style={{ background: colors[0] }} /> Empty</span>
        <span><i style={{ background: colors[1] }} /> Wall</span>
        <span><i style={{ background: colors[2] }} /> Danger</span>
        <span><i style={{ background: colors[3] }} /> Start</span>
        <span><i style={{ background: colors[4] }} /> Goal</span>
      </div>
    </main>
  );
}
