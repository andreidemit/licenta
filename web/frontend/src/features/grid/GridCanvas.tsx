import * as React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cellColors, cellLabels } from '../../lib/formatters';
import type { GridPayload, EnvironmentPayload, TrajectoryStep } from '../../lib/types';
import { cn } from '../../lib/cn';

type AnyGrid = GridPayload | EnvironmentPayload;

export type AgentMarker = {
  row: number;
  col: number;
  energyPct?: number;
  reachedTarget?: boolean;
  alive?: boolean;
};

export function GridCanvas({
  grid,
  agent,
  trail,
  lastAction,
  editable = false,
  selectedTool,
  onCellClick,
  showCoords = false,
  className,
}: {
  grid?: AnyGrid;
  agent?: AgentMarker;
  trail?: TrajectoryStep[];
  lastAction?: number;
  editable?: boolean;
  selectedTool?: number;
  onCellClick?: (row: number, col: number) => void;
  showCoords?: boolean;
  className?: string;
}) {
  if (!grid) {
    return (
      <div
        className={cn(
          'grid place-items-center text-ink-muted text-sm rounded-xl border border-dashed border-border/60 bg-surface/30 p-10',
          className,
        )}
      >
        Niciun mediu încărcat încă.
      </div>
    );
  }

  const trailKeys = React.useMemo(() => {
    const set = new Set<string>();
    (trail ?? []).forEach((s) => set.add(`${s.row}-${s.col}`));
    return set;
  }, [trail]);

  return (
    <div
      className={cn(
        'relative mx-auto w-full max-w-full',
        'rounded-2xl border border-border/60 bg-surface/70 backdrop-blur p-3',
        'shadow-soft',
        className,
      )}
    >
      <div
        className={cn('grid gap-[2px] aspect-square w-full max-h-[min(72vh,900px)] mx-auto')}
        style={{
          gridTemplateColumns: `repeat(${grid.cols}, minmax(0, 1fr))`,
        }}
      >
        {grid.grid.flatMap((row, r) =>
          row.map((cell, c) => {
            const isAgent = agent?.row === r && agent?.col === c;
            const isTrail = trailKeys.has(`${r}-${c}`);
            const baseColor = cellColors[cell] ?? cellColors[0];
            const interactive = editable;
            const isStartCell = cell === 6;
            const isTargetCell = cell === 5;
            return (
              <button
                type="button"
                key={`${r}-${c}`}
                onClick={() => interactive && onCellClick?.(r, c)}
                disabled={!interactive}
                className={cn(
                  'relative rounded-[3px] transition-all duration-150',
                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent',
                  interactive ? 'cursor-pointer hover:scale-105 hover:z-10' : 'cursor-default',
                  isTargetCell && 'shadow-[0_0_12px_-2px_rgba(167,139,250,0.8)]',
                  isStartCell && 'shadow-[0_0_10px_-2px_rgba(56,189,248,0.6)]',
                )}
                style={{ backgroundColor: baseColor }}
                title={
                  showCoords
                    ? `(${r}, ${c}) · ${cellLabels[cell] ?? cell}`
                    : cellLabels[cell] ?? String(cell)
                }
                aria-label={`Celulă rând ${r}, coloană ${c}, ${cellLabels[cell] ?? cell}`}
              >
                {isTrail && !isAgent ? (
                  <span className="absolute inset-1 rounded-full bg-white/30 mix-blend-overlay" />
                ) : null}
                {editable && selectedTool === cell ? (
                  <span className="absolute inset-1 rounded-[2px] border border-white/40" />
                ) : null}
                <AnimatePresence>
                  {isAgent ? (
                    <motion.span
                      layoutId="agent"
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      exit={{ scale: 0.5, opacity: 0 }}
                      transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                      className={cn(
                        'absolute inset-[12%] rounded-full',
                        agent?.reachedTarget
                          ? 'bg-accent-success shadow-[0_0_18px_2px_rgba(52,211,153,0.7)]'
                          : agent?.alive === false
                          ? 'bg-accent-danger shadow-[0_0_18px_2px_rgba(244,63,94,0.7)]'
                          : 'bg-white shadow-[0_0_18px_2px_rgba(255,255,255,0.6)] animate-pulse-soft',
                      )}
                    />
                  ) : null}
                </AnimatePresence>
              </button>
            );
          }),
        )}
      </div>
      {agent && lastAction !== undefined ? (
        <div className="absolute top-3 right-3">
          <ActionGhost action={lastAction} />
        </div>
      ) : null}
    </div>
  );
}

function ActionGhost({ action }: { action: number }) {
  const icons = ['↑', '↓', '←', '→', '•'];
  const labels = ['SUS', 'JOS', 'STÂNGA', 'DREAPTA', 'STAI'];
  return (
    <motion.div
      key={action}
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="flex items-center gap-2 rounded-full border border-border/60 bg-elevated/80 px-3 py-1 text-xs text-ink-muted backdrop-blur"
    >
      <span className="text-base text-accent">{icons[action]}</span>
      <span>{labels[action]}</span>
    </motion.div>
  );
}
