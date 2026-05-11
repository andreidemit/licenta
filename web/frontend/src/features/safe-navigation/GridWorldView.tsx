import { CircleDot, Eye, Flame, Footprints, Hash } from 'lucide-react';
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
    return <main className="visualization empty-stage">Generează o hartă pentru început.</main>;
  }

  const pathSet = new Set((result?.path ?? []).map(([row, col]) => `${row}-${col}`));
  const finalPosition = result?.path?.length ? result.path[result.path.length - 1] : undefined;
  const maxRisk = Math.max(1, ...((environment.risk_map ?? []).flat()));

  return (
    <main className="visualization">
      <div className="stage-toolbar">
        <button className={showPath ? 'toggle active' : 'toggle'} onClick={onTogglePath}><Footprints size={15} /> Traseu</button>
        <button className={showRisk ? 'toggle active' : 'toggle'} onClick={onToggleRisk}><Flame size={15} /> Hartă risc</button>
        <button className={showCoordinates ? 'toggle active' : 'toggle'} onClick={onToggleCoordinates}><Hash size={15} /> Coordonate</button>
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
            const riskRatio = maxRisk > 0 ? Math.min(1, risk / maxRisk) : 0;
            const riskAlpha = showRisk ? Math.sqrt(riskRatio) * 0.85 : 0;
            const riskBoxShadow = showRisk && riskRatio > 0.6
              ? `inset 0 0 0 2px rgba(127, 29, 29, ${0.45 + riskRatio * 0.4})`
              : undefined;
            return (
              <div
                key={key}
                className={`grid-cell ${isPath ? 'path-cell' : ''} ${isAgent ? 'agent-cell' : ''}`}
                style={{
                  background: `linear-gradient(rgba(220,38,38,${riskAlpha}), rgba(153,27,27,${riskAlpha})), ${colors[cell] ?? '#f8fafc'}`,
                  boxShadow: riskBoxShadow,
                }}
                title={`rând ${rowIndex}, coloană ${colIndex}, risc ${risk.toFixed(1)}`}
              >
                {showCoordinates && <span>{rowIndex},{colIndex}</span>}
                {isAgent && <b />}
              </div>
            );
          }),
        )}
      </div>
      <div className="legend">
        <span><i style={{ background: colors[0] }} /> Liber</span>
        <span><i style={{ background: colors[1] }} /> Perete</span>
        <span><i style={{ background: colors[2] }} /> Pericol</span>
        <span><i style={{ background: colors[3] }} /> Pornire</span>
        <span><i style={{ background: colors[4] }} /> Obiectiv</span>
        <span><i className="legend-path" /> Traseu</span>
        <span><i className="legend-agent"><CircleDot size={10} /></i> Agent</span>
        <span><i className="legend-risk" /> Risc</span>
      </div>
    </main>
  );
}
