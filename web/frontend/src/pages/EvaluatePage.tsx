import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useMemo, useState } from 'react';
import {
  ChevronRight,
  Database,
  Map as MapIcon,
  Pause,
  Play,
  RotateCcw,
  SkipBack,
  SkipForward,
  Star,
  Target,
  Trophy,
  AlertOctagon,
  Loader2,
} from 'lucide-react';

import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { EmptyState } from '../components/common/EmptyState';
import { GridCanvas } from '../features/grid/GridCanvas';
import { GridLegend } from '../features/grid/GridLegend';
import { useEvaluationScenarios, useQTables } from '../hooks/useRunsApi';
import { useReplayPlayer } from '../hooks/useReplayPlayer';
import { api } from '../lib/api';
import {
  actionNames,
  fmt,
  scenarioMeta,
  translateBackendCell,
  translateOutcome,
} from '../lib/formatters';
import type { EvaluationResult, EvaluationScenario, QTableItem } from '../lib/types';
import { cn } from '../lib/cn';

type Step = 1 | 2 | 3;

export function EvaluatePage() {
  const [step, setStep] = useState<Step>(1);
  const [qtable, setQtable] = useState<QTableItem | null>(null);
  const [scenario, setScenario] = useState<EvaluationScenario | null>(null);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { items: qtables } = useQTables();
  const scenarios = useEvaluationScenarios();

  const launch = async () => {
    if (!qtable || !scenario) return;
    setLoading(true);
    setError(null);
    try {
      const env = {
        id: scenario.environment.id ?? scenario.id,
        name: scenario.environment.name ?? scenario.name,
        rows: scenario.environment.rows,
        cols: scenario.environment.cols,
        start: scenario.environment.start,
        target: scenario.environment.target,
        grid: scenario.environment.grid,
      };
      const payload = await api.evaluate({
        qtable_path: qtable.path,
        environments: [env],
        energy: 100,
      });
      const first = payload.results?.[0];
      if (!first) {
        setError('Backend-ul nu a returnat niciun rezultat de evaluare.');
        return;
      }
      setResult(first);
      setStep(3);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Eroare la evaluare');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Test pe medii noi"
        title="Pune agentul la probă"
        description="În trei pași: alegi ce a învățat, alegi unde îl trimiți, și-l urmărești cum se descurcă."
      />

      <Stepper step={step} onSelect={setStep} qtableSelected={!!qtable} scenarioSelected={!!scenario} />

      <AnimatePresence mode="wait">
        {step === 1 ? (
          <motion.div
            key="step-1"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25 }}
          >
            <QTableStep
              items={qtables}
              selected={qtable}
              onSelect={setQtable}
              onNext={() => setStep(2)}
            />
          </motion.div>
        ) : step === 2 ? (
          <motion.div
            key="step-2"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25 }}
          >
            <ScenarioStep
              scenarios={scenarios}
              selected={scenario}
              onSelect={setScenario}
              onBack={() => setStep(1)}
              onLaunch={launch}
              loading={loading}
              error={error}
            />
          </motion.div>
        ) : (
          <motion.div
            key="step-3"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25 }}
          >
            {result ? (
              <ReplayStep
                result={result}
                qtable={qtable}
                scenario={scenario}
                onRestart={() => {
                  setResult(null);
                  setStep(2);
                }}
                onChangeQTable={() => {
                  setResult(null);
                  setStep(1);
                }}
              />
            ) : (
              <EmptyState
                title="Nu există un rezultat de afișat"
                description="Întoarce-te și pornește o evaluare."
                action={
                  <Button onClick={() => setStep(1)} variant="secondary">
                    Înapoi la pasul 1
                  </Button>
                }
              />
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ---------- Stepper ---------- */

function Stepper({
  step,
  onSelect,
  qtableSelected,
  scenarioSelected,
}: {
  step: Step;
  onSelect: (s: Step) => void;
  qtableSelected: boolean;
  scenarioSelected: boolean;
}) {
  const items: { id: Step; label: string; icon: React.ElementType; available: boolean }[] = [
    { id: 1, label: 'Tabel Q', icon: Database, available: true },
    { id: 2, label: 'Scenariu', icon: MapIcon, available: qtableSelected },
    { id: 3, label: 'Replay', icon: Target, available: qtableSelected && scenarioSelected },
  ];
  return (
    <ol className="flex items-center gap-2 text-sm">
      {items.map((it, i) => {
        const Icon = it.icon;
        const active = step === it.id;
        return (
          <li key={it.id} className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => it.available && onSelect(it.id)}
              disabled={!it.available}
              className={cn(
                'inline-flex items-center gap-2 rounded-full border px-3 py-1.5 transition-all',
                active
                  ? 'border-accent bg-accent/15 text-accent shadow-glow'
                  : 'border-border/60 bg-elevated/60 text-ink-muted hover:text-ink',
                !it.available && 'opacity-40 cursor-not-allowed',
              )}
            >
              <span
                className={cn(
                  'flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-semibold',
                  active ? 'bg-accent text-canvas' : 'bg-elevated text-ink-muted',
                )}
              >
                {it.id}
              </span>
              <Icon size={14} />
              <span>{it.label}</span>
            </button>
            {i < items.length - 1 ? (
              <ChevronRight size={14} className="text-ink-subtle" />
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}

/* ---------- Step 1: Q-table picker ---------- */

function QTableStep({
  items,
  selected,
  onSelect,
  onNext,
}: {
  items: QTableItem[];
  selected: QTableItem | null;
  onSelect: (q: QTableItem) => void;
  onNext: () => void;
}) {
  if (items.length === 0) {
    return (
      <EmptyState
        icon={<Database size={28} />}
        title="Niciun tabel Q salvat"
        description="Antrenează mai întâi agentul. Tabelul Q rezultat va apărea automat aici."
      />
    );
  }
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {items.map((q) => {
          const isActive = selected?.path === q.path;
          return (
            <button
              key={q.path}
              type="button"
              onClick={() => onSelect(q)}
              className={cn(
                'group text-left rounded-xl border p-5 transition-all',
                isActive
                  ? 'border-accent/60 bg-accent/10 shadow-glow'
                  : 'border-border/60 bg-surface/70 hover:-translate-y-0.5 hover:border-accent/40',
              )}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-elevated/80 text-accent">
                  <Database size={18} />
                </div>
                {isActive ? <Badge variant="accent">Selectat</Badge> : null}
              </div>
              <h3 className="mt-3 font-serif text-base text-ink">
                Rulare <span className="font-mono text-sm">{q.run_id}</span>
              </h3>
              <p className="mt-1 text-xs text-ink-muted truncate" title={q.path}>
                {q.path}
              </p>
            </button>
          );
        })}
      </div>
      <div className="flex justify-end">
        <Button onClick={onNext} disabled={!selected}>
          Continuă <ChevronRight size={16} />
        </Button>
      </div>
    </div>
  );
}

/* ---------- Step 2: Scenario picker ---------- */

function ScenarioStep({
  scenarios,
  selected,
  onSelect,
  onBack,
  onLaunch,
  loading,
  error,
}: {
  scenarios: EvaluationScenario[];
  selected: EvaluationScenario | null;
  onSelect: (s: EvaluationScenario) => void;
  onBack: () => void;
  onLaunch: () => void;
  loading: boolean;
  error: string | null;
}) {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2">
        {scenarios.map((s) => {
          const isActive = selected?.id === s.id;
          const distance = s.environment.bfs_distance;
          const stars = difficultyStars(s, distance);
          return (
            <button
              key={s.id}
              type="button"
              onClick={() => onSelect(s)}
              className={cn(
                'group text-left overflow-hidden rounded-xl border transition-all',
                isActive
                  ? 'border-accent/60 shadow-glow bg-accent/5'
                  : 'border-border/60 bg-surface/70 hover:-translate-y-0.5 hover:border-accent/40',
              )}
            >
              <div className="aspect-[5/3] bg-canvas/60 p-3 border-b border-border/40">
                <MiniMap grid={s.environment} />
              </div>
              <div className="p-4 space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="font-serif text-base text-ink">{s.name}</h3>
                  <div className="flex items-center gap-0.5 text-accent-secondary">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <Star
                        key={i}
                        size={12}
                        className={i < stars ? 'fill-accent-secondary' : 'opacity-30'}
                      />
                    ))}
                  </div>
                </div>
                <p className="text-xs text-ink-muted leading-relaxed">{s.description}</p>
                <div className="flex flex-wrap gap-1.5">
                  <Badge>{s.environment.rows}×{s.environment.cols}</Badge>
                  {distance != null ? <Badge variant="info">BFS {distance}</Badge> : null}
                  {isActive ? <Badge variant="accent">Selectat</Badge> : null}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {error ? (
        <Card className="border-accent-danger/40">
          <CardContent className="py-3 text-sm text-accent-danger flex items-center gap-2">
            <AlertOctagon size={16} /> {error}
          </CardContent>
        </Card>
      ) : null}

      <div className="flex justify-between">
        <Button variant="ghost" onClick={onBack}>
          Înapoi
        </Button>
        <Button onClick={onLaunch} disabled={!selected || loading} size="lg">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
          {loading ? 'Pornesc evaluarea…' : 'Pornește evaluarea'}
        </Button>
      </div>
    </div>
  );
}

function difficultyStars(s: EvaluationScenario, bfs: number | null): number {
  // Heuristic: bigger BFS distance + more obstacles = more stars
  const cells = s.environment.grid.flat();
  const obstacles = cells.filter((c) => c === 1 || c === 2 || c === 4).length;
  const ratio = obstacles / cells.length;
  const distScore = (bfs ?? 0) / Math.max(s.environment.rows + s.environment.cols, 1);
  const score = ratio * 2 + distScore;
  if (score > 1.0) return 3;
  if (score > 0.55) return 2;
  return 1;
}

function MiniMap({ grid }: { grid: EvaluationScenario['environment'] }) {
  return (
    <div
      className="grid gap-[1px] w-full h-full"
      style={{ gridTemplateColumns: `repeat(${grid.cols}, 1fr)` }}
    >
      {grid.grid.flatMap((row, r) =>
        row.map((cell, c) => (
          <div
            key={`${r}-${c}`}
            className="rounded-[1px]"
            style={{
              backgroundColor:
                {
                  0: '#1e293b',
                  1: '#52525b',
                  2: '#a16207',
                  3: '#10b981',
                  4: '#e11d48',
                  5: '#a78bfa',
                  6: '#38bdf8',
                }[cell] ?? '#1e293b',
            }}
          />
        )),
      )}
    </div>
  );
}

/* ---------- Step 3: Replay ---------- */

function ReplayStep({
  result,
  qtable,
  scenario,
  onRestart,
  onChangeQTable,
}: {
  result: EvaluationResult;
  qtable: QTableItem | null;
  scenario: EvaluationScenario | null;
  onRestart: () => void;
  onChangeQTable: () => void;
}) {
  const trajectory = result.trajectory ?? [];
  const maxStep = Math.max(0, trajectory.length - 1);
  const player = useReplayPlayer(maxStep, { speedMs: 320 });
  const current = trajectory[player.step];
  const visibleTrail = useMemo(
    () => trajectory.slice(0, player.step + 1),
    [trajectory, player.step],
  );

  // Auto-play once when result lands
  useEffect(() => {
    if (maxStep > 0) player.setPlaying(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result]);

  const isFinalStep = player.step >= maxStep && maxStep > 0;
  const success = result.outcome === 'target_reached';

  const agent = current
    ? {
        row: current.row,
        col: current.col,
        alive: !current.terminal_reason || current.terminal_reason === 'target_reached',
        reachedTarget: current.terminal_reason === 'target_reached',
      }
    : undefined;

  return (
    <div className="space-y-4">
      {/* Context bar */}
      <Card>
        <CardContent className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="accent">
              {scenario ? scenarioMeta[scenario.id]?.label ?? scenario.name : 'Scenariu'}
            </Badge>
            <span className="text-ink-muted">
              Tabel Q · <span className="font-mono">{qtable?.run_id}</span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={onChangeQTable}>
              Schimbă tabelul Q
            </Button>
            <Button variant="secondary" size="sm" onClick={onRestart}>
              Alt scenariu
            </Button>
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        {/* Stage */}
        <div className="space-y-3">
          <div className="relative">
            <GridCanvas
              grid={result.environment}
              agent={agent}
              trail={visibleTrail}
              lastAction={current?.action}
            />
            {/* Energy bar over grid */}
            {current ? (
              <div className="absolute left-3 top-3 flex flex-col items-center gap-1.5">
                <div className="h-32 w-2.5 rounded-full bg-elevated/60 overflow-hidden border border-border/50">
                  <motion.div
                    className="w-full bg-gradient-to-t from-accent-success to-accent-secondary origin-bottom"
                    initial={false}
                    animate={{ height: `${Math.max(0, Math.min(100, current.energy))}%` }}
                    style={{ position: 'relative', top: 'auto', bottom: 0 }}
                  />
                </div>
                <span className="font-mono text-[10px] text-ink-muted">
                  {fmt.number(current.energy)}
                </span>
              </div>
            ) : null}

            {/* Reward float */}
            <AnimatePresence>
              {current && current.reward !== 0 ? (
                <motion.div
                  key={`${player.step}-${current.reward}`}
                  initial={{ opacity: 0, y: 0, scale: 0.9 }}
                  animate={{ opacity: 1, y: -16, scale: 1 }}
                  exit={{ opacity: 0, y: -32 }}
                  transition={{ duration: 0.5 }}
                  className={cn(
                    'absolute right-4 bottom-4 rounded-full border px-3 py-1 text-sm font-mono backdrop-blur',
                    current.reward > 0
                      ? 'border-accent-success/40 bg-accent-success/15 text-accent-success'
                      : 'border-accent-danger/40 bg-accent-danger/15 text-accent-danger',
                  )}
                >
                  {current.reward > 0 ? '+' : ''}{current.reward.toFixed(1)}
                </motion.div>
              ) : null}
            </AnimatePresence>
          </div>

          <ReplayControls player={player} maxStep={maxStep} />
          <GridLegend />
        </div>

        {/* Side panel */}
        <div className="space-y-3">
          <Card className={cn(success ? 'border-accent-success/40' : isFinalStep ? 'border-accent-danger/40' : '')}>
            <CardContent className="space-y-3 py-4">
              <div className="flex items-center gap-3">
                <div
                  className={cn(
                    'flex h-12 w-12 items-center justify-center rounded-xl',
                    success
                      ? 'bg-accent-success/15 text-accent-success'
                      : 'bg-accent-danger/15 text-accent-danger',
                  )}
                >
                  {success ? <Trophy size={22} /> : <AlertOctagon size={22} />}
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wider text-ink-muted">Rezultat final</p>
                  <p className="font-serif text-lg text-ink">{translateOutcome(result.outcome)}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <Stat label="Pași" value={fmt.integer(result.steps)} />
                <Stat label="Recompensă" value={fmt.number(result.reward)} />
                <Stat label="Energie rămasă" value={fmt.number(result.energy_remaining)} />
                <Stat
                  label="vs BFS optim"
                  value={
                    result.bfs_overhead != null
                      ? `${result.bfs_overhead > 0 ? '+' : ''}${result.bfs_overhead}`
                      : '—'
                  }
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Pasul curent</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <Row label="Pas">
                {player.step + 1} / {trajectory.length}
              </Row>
              <Row label="Acțiune">
                {current ? actionNames[current.action] : '—'}
              </Row>
              <Row label="Recompensă">
                {current ? fmt.number(current.reward) : '—'}
              </Row>
              <Row label="Energie">
                {current ? fmt.number(current.energy) : '—'}
              </Row>
              <Row label="Celulă">
                {translateBackendCell(current?.cell_type)}
              </Row>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

function ReplayControls({
  player,
  maxStep,
}: {
  player: ReturnType<typeof useReplayPlayer>;
  maxStep: number;
}) {
  return (
    <Card>
      <CardContent className="py-3 space-y-3">
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={player.reset} aria-label="Reset">
            <RotateCcw size={16} />
          </Button>
          <Button variant="ghost" size="icon" onClick={player.prev} aria-label="Înapoi un pas">
            <SkipBack size={16} />
          </Button>
          <Button
            variant="primary"
            size="icon"
            onClick={() => player.setPlaying((p) => !p)}
            aria-label={player.playing ? 'Pauză' : 'Redare'}
          >
            {player.playing ? <Pause size={16} /> : <Play size={16} />}
          </Button>
          <Button variant="ghost" size="icon" onClick={player.next} aria-label="Următorul pas">
            <SkipForward size={16} />
          </Button>
          <Button variant="ghost" size="icon" onClick={player.end} aria-label="Final">
            <SkipForward size={16} className="opacity-60" />
          </Button>

          <div className="ml-3 flex items-center gap-2 text-xs text-ink-muted">
            <span>Viteză</span>
            {[
              { ms: 600, label: '0.5×' },
              { ms: 320, label: '1×' },
              { ms: 160, label: '2×' },
              { ms: 80, label: '4×' },
            ].map((opt) => (
              <button
                key={opt.ms}
                onClick={() => player.setSpeedMs(opt.ms)}
                className={cn(
                  'rounded-full border px-2 py-0.5 text-xs',
                  player.speedMs === opt.ms
                    ? 'border-accent text-accent bg-accent/10'
                    : 'border-border/60 text-ink-muted hover:text-ink',
                )}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <input
          type="range"
          min={0}
          max={maxStep}
          value={player.step}
          onChange={(e) => player.setStep(Number(e.target.value))}
          className="w-full accent-[hsl(var(--accent-primary))]"
          aria-label="Timeline"
        />
      </CardContent>
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-elevated/60 border border-border/60 px-3 py-2">
      <p className="text-[10px] uppercase tracking-wider text-ink-subtle">{label}</p>
      <p className="font-mono text-base text-ink mt-0.5">{value}</p>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-ink-muted">{label}</span>
      <span className="font-mono text-ink">{children}</span>
    </div>
  );
}
