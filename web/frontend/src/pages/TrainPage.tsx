import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Play,
  Square,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';

import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input, Label, Select } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { StatCard } from '../components/common/StatCard';
import { InfoTip } from '../components/common/InfoTip';
import { RewardAreaChart } from '../components/common/SimpleCharts';
import { GridCanvas } from '../features/grid/GridCanvas';
import { GridLegend } from '../features/grid/GridLegend';
import { useTrainingStream } from '../hooks/useTrainingStream';
import { api } from '../lib/api';
import { actionNames, fmt, scenarioMeta, translateStatus } from '../lib/formatters';
import type { GridPayload } from '../lib/types';

export function TrainPage() {
  const navigate = useNavigate();
  const [scenario, setScenario] = useState('B');
  const [seed, setSeed] = useState(42);
  const [episodes, setEpisodes] = useState(200);
  const [rows, setRows] = useState(20);
  const [cols, setCols] = useState(20);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [preview, setPreview] = useState<GridPayload>();
  const [chartOpen, setChartOpen] = useState(true);

  const { job, live, chart, isStreaming, start, stop } = useTrainingStream();

  useEffect(() => {
    let cancelled = false;
    api
      .previewEnvironment({ scenario, rows, cols, seed })
      .then((p) => !cancelled && setPreview(p))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [scenario, rows, cols, seed]);

  const isRunning = isStreaming || job?.status === 'running';
  const progressPct = Math.round((job?.progress ?? 0) * 100);

  const launch = async () => {
    try {
      await start({ scenario, rows, cols, seed, episodes });
    } catch {
      /* error already in state */
    }
  };

  const knowledge = live?.info?.learning?.knowledge;
  const feedback = live?.info?.feedback;

  const meta = scenarioMeta[scenario] ?? scenarioMeta.B;

  // Toast on completion
  useEffect(() => {
    if (job?.status === 'completed') {
      const t = window.setTimeout(() => {
        // user-driven; just visual
      }, 0);
      return () => window.clearTimeout(t);
    }
  }, [job?.status]);

  if (isRunning || (job && live)) {
    return (
      <TrainingLiveView
        progress={progressPct}
        onStop={stop}
        scenario={scenario}
        live={live}
        chart={chart}
        chartOpen={chartOpen}
        onToggleChart={() => setChartOpen((v) => !v)}
        feedback={feedback}
        knowledge={knowledge}
        previewGrid={preview}
        statusLabel={translateStatus(job?.status)}
        completed={job?.status === 'completed'}
        onSeeRun={() => job && navigate(`/rulari/${job.id}`)}
      />
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Pasul 1"
        title="Configurează antrenarea"
        description="Alege scenariul, sămânța și numărul de episoade. Backend-ul va antrena agentul iar tu vei vedea harta și progresul live."
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_minmax(0,1.4fr)]">
        <Card>
          <CardHeader>
            <CardTitle>Parametri experiment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">
            <div>
              <Label>
                Scenariu
                <InfoTip text="A = navigare cu energie infinită, B = supraviețuire cu energie limitată, C = obstacole dinamice, Depozit = hartă fixă inspirată dintr-un depozit." />
              </Label>
              <Select value={scenario} onChange={(e) => setScenario(e.target.value)}>
                <option value="A">A · Navigare</option>
                <option value="B">B · Supraviețuire</option>
                <option value="C">C · Hartă dinamică</option>
                <option value="WAREHOUSE">Depozit industrial</option>
              </Select>
              <p className="mt-2 text-xs text-ink-muted">{meta.description}</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label>
                  Sămânță
                  <InfoTip text="Aceeași sămânță generează aceeași hartă — util pentru reproducibilitate." />
                </Label>
                <Input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(Number(e.target.value))}
                />
              </div>
              <div>
                <Label>
                  Episoade
                  <InfoTip text="Un episod = o încercare completă a agentului. Mai multe episoade înseamnă mai multă învățare." />
                </Label>
                <Input
                  type="number"
                  value={episodes}
                  onChange={(e) => setEpisodes(Number(e.target.value))}
                />
              </div>
            </div>

            <button
              type="button"
              onClick={() => setAdvancedOpen((v) => !v)}
              className="flex w-full items-center justify-between text-sm text-ink-muted hover:text-ink"
            >
              <span className="font-medium">Opțiuni avansate</span>
              {advancedOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>
            <AnimatePresence initial={false}>
              {advancedOpen ? (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="grid grid-cols-2 gap-3 overflow-hidden"
                >
                  <div>
                    <Label>Rânduri grid</Label>
                    <Input
                      type="number"
                      value={rows}
                      onChange={(e) => setRows(Number(e.target.value))}
                    />
                  </div>
                  <div>
                    <Label>Coloane grid</Label>
                    <Input
                      type="number"
                      value={cols}
                      onChange={(e) => setCols(Number(e.target.value))}
                    />
                  </div>
                </motion.div>
              ) : null}
            </AnimatePresence>

            <Button
              onClick={launch}
              size="lg"
              className="w-full"
              disabled={isStreaming}
            >
              <Play size={18} /> Pornește antrenarea
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Previzualizare hartă</CardTitle>
            <p className="text-xs text-ink-muted">
              Scenariu <Badge variant="accent" className="ml-1">{meta.label}</Badge>
              {' '}·{' '}sămânță <span className="font-mono">{seed}</span>
              {' '}· grid <span className="font-mono">{rows}×{cols}</span>
              {preview?.bfs_distance != null
                ? <> · BFS optim <span className="font-mono">{preview.bfs_distance} pași</span></>
                : null}
            </p>
          </CardHeader>
          <CardContent>
            <GridCanvas grid={preview} />
            <div className="mt-3">
              <GridLegend />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function TrainingLiveView({
  progress,
  onStop,
  scenario,
  live,
  chart,
  chartOpen,
  onToggleChart,
  feedback,
  knowledge,
  previewGrid,
  statusLabel,
  completed,
  onSeeRun,
}: {
  progress: number;
  onStop: () => void;
  scenario: string;
  live?: ReturnType<typeof useTrainingStream>['live'];
  chart: ReturnType<typeof useTrainingStream>['chart'];
  chartOpen: boolean;
  onToggleChart: () => void;
  feedback?: ReturnType<typeof useTrainingStream>['live'] extends infer T
    ? T extends { info?: { feedback?: infer F } }
      ? F
      : never
    : never;
  knowledge?: { fill_pct: number; coverage_pct: number; mean_abs_q: number; mean_recent_td: number };
  previewGrid?: GridPayload;
  statusLabel: string;
  completed: boolean;
  onSeeRun: () => void;
}) {
  const meta = scenarioMeta[scenario] ?? scenarioMeta.B;
  const grid = live?.environment ?? previewGrid;
  const chartWidth = Math.max(320, chart.length * 8);
  const agent = live?.agent
    ? {
        row: live.agent.position[0],
        col: live.agent.position[1],
        alive: live.agent.alive,
        reachedTarget: live.agent.reached_target,
        energyPct: live.agent.energy_percent,
      }
    : undefined;

  const actionCounts = live?.info?.live?.action_counts ?? [0, 0, 0, 0, 0];
  const totalActions = useMemo(
    () => Math.max(1, actionCounts.reduce((a, b) => a + b, 0)),
    [actionCounts],
  );

  return (
    <div className="space-y-4 animate-fade-in">
      {/* HUD topbar */}
      <Card className="overflow-hidden">
        <CardContent className="flex flex-wrap items-center justify-between gap-4 py-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent/15 text-accent">
              <Sparkles size={18} />
            </div>
            <div className="min-w-0">
              <p className="text-xs uppercase tracking-wider text-ink-muted">Antrenare în desfășurare</p>
              <p className="font-serif text-lg text-ink truncate">
                {meta.label} · sămânță {live?.environment ? '' : ''}{statusLabel}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4 flex-1 min-w-[280px] max-w-md">
            <div className="flex-1 h-2 rounded-full bg-elevated overflow-hidden">
              <motion.div
                className="h-full bg-accent shadow-glow"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
            <span className="font-mono text-sm text-ink-muted shrink-0">{progress}%</span>
          </div>
          <div className="flex items-center gap-2">
            {completed ? (
              <Button variant="success" onClick={onSeeRun}>
                <CheckCircle2 size={16} /> Vezi rezultatele
              </Button>
            ) : (
              <Button variant="danger" onClick={onStop}>
                <Square size={16} /> Oprește
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Stage */}
      <div className="grid gap-4 lg:grid-cols-[1fr_320px]">
        <div className="space-y-3">
          <GridCanvas grid={grid} agent={agent} lastAction={feedback?.action} />
          <GridLegend />
        </div>

        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              label="Energie"
              value={live?.agent ? fmt.number(live.agent.energy) : '—'}
              accent="success"
              hint="Energie rămasă a agentului. Sub 0 → episodul eșuează."
            />
            <StatCard
              label="Recompensă"
              value={live?.agent ? fmt.number(live.agent.reward) : '—'}
              accent="info"
              hint="Suma recompenselor primite în episodul curent."
            />
            <StatCard
              label="Pași"
              value={live?.agent?.steps ?? '—'}
              hint="Numărul de acțiuni executate în episodul curent."
            />
            <StatCard
              label="Q completat"
              value={knowledge ? `${knowledge.fill_pct.toFixed(1)}%` : '—'}
              accent="warning"
              hint="Procentul de intrări nenule din tabelul Q — cât de mult din spațiul stărilor a fost vizitat."
            />
          </div>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Distribuția acțiunilor</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 pt-0">
              {actionCounts.map((count, i) => (
                <div key={actionNames[i]} className="flex items-center gap-2">
                  <span className="w-16 text-xs text-ink-muted">{actionNames[i]}</span>
                  <div className="flex-1 h-2 rounded-full bg-elevated overflow-hidden">
                    <motion.div
                      className="h-full bg-accent/70"
                      initial={{ width: 0 }}
                      animate={{ width: `${(count / totalActions) * 100}%` }}
                      transition={{ duration: 0.4 }}
                    />
                  </div>
                  <span className="w-8 text-right font-mono text-xs text-ink">{count}</span>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2 flex-row items-center justify-between">
              <CardTitle className="text-sm">Evoluția recompensei</CardTitle>
              <button
                onClick={onToggleChart}
                className="text-ink-muted hover:text-ink"
                aria-label="Comută graficul"
              >
                {chartOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
              </button>
            </CardHeader>
            {chartOpen ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2 }}
              >
                <CardContent className="pt-0 pb-4">
                  <div className="overflow-x-auto overflow-y-hidden">
                    <RewardAreaChart data={chart} width={chartWidth} height={140} />
                  </div>
                </CardContent>
              </motion.div>
            ) : null}
          </Card>
        </div>
      </div>

      {completed && live?.agent && !live.agent.reached_target ? (
        <Card className="border-accent-secondary/30">
          <CardContent className="flex items-center gap-3 py-4 text-sm text-ink-muted">
            <AlertTriangle className="text-accent-secondary" size={18} />
            Antrenarea s-a încheiat dar ultimul episod nu a atins ținta. Verifică graficele de
            convergență pentru a vedea evoluția per ansamblu.
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
