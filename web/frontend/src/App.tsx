import { useEffect, useMemo, useState } from 'react';
import './styles.css';
import {
  Activity,
  BarChart3,
  Boxes,
  Brain,
  Download,
  HelpCircle,
  Map,
  MousePointer2,
  Pause,
  Play,
  RefreshCw,
  Route,
  Save,
  SkipBack,
  SkipForward,
} from 'lucide-react';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

type GridPayload = {
  id?: string | null;
  name?: string | null;
  rows: number;
  cols: number;
  start: number[];
  target: number[];
  bfs_distance: number | null;
  grid: number[][];
};

type EnvironmentPayload = {
  id?: string | null;
  name: string;
  rows: number;
  cols: number;
  start: number[];
  target: number[];
  grid: number[][];
};

type JobSnapshot = {
  id: string;
  status: string;
  scenario: string;
  progress: number;
  message: string;
  artifacts: Record<string, string>;
  latest_event?: LiveEvent;
  created_at?: string;
  updated_at?: string;
};

type LiveEvent = {
  type: string;
  environment?: GridPayload;
  agent?: {
    position: number[];
    energy: number;
    energy_percent: number;
    steps: number;
    reward: number;
    alive: boolean;
    reached_target: boolean;
  };
  info?: {
    feedback?: {
      action?: number;
      reward?: number;
      energy_delta?: number;
      previous_pos?: number[];
      new_pos?: number[];
      terminal_reason?: string | null;
      cell_type?: string;
    };
    live?: {
      step: number;
      max_steps: number;
      action_counts: number[];
      collisions: number;
      food_collected: number;
      mud_steps: number;
    };
    learning?: {
      knowledge?: {
        fill_pct: number;
        coverage_pct: number;
        mean_abs_q: number;
        mean_recent_td: number;
      };
    };
  };
};

type QTableItem = {
  path: string;
  run_id: string;
  download_url?: string;
};

type StoredEnvironment = {
  id: string;
  name: string;
  rows: number;
  cols: number;
  bfs_distance: number | null;
  path: string;
};

type EvaluationScenario = {
  id: string;
  name: string;
  description: string;
  environment: GridPayload;
};

type TrajectoryStep = {
  step: number;
  previous_row: number;
  previous_col: number;
  row: number;
  col: number;
  energy: number;
  reward: number;
  total_reward: number;
  action: number;
  cell_type: string;
  terminal_reason?: string | null;
};

type EvaluationResult = {
  environment: GridPayload;
  outcome: string;
  steps: number;
  reward: number;
  energy_remaining: number;
  bfs_distance: number | null;
  bfs_overhead: number | null;
  trajectory: TrajectoryStep[];
};

const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

const cellColors: Record<number, string> = {
  0: '#7ddf88',
  1: '#5f6673',
  2: '#a98467',
  3: '#ffd166',
  4: '#ef476f',
  5: '#4cc9f0',
  6: '#06d6a0',
};

const cellLabels: Record<number, string> = {
  0: 'Liber',
  1: 'Obstacol',
  2: 'Noroi',
  3: 'Hrană',
  4: 'Pericol',
  5: 'Țintă',
  6: 'Pornire',
};
const cellDescriptions: Record<number, string> = {
  0: 'Celulă traversabilă normală. Agentul poate trece prin ea cu cost energetic standard.',
  1: 'Zid sau obstacol. Agentul nu poate intra aici și primește penalizare dacă lovește obstacolul.',
  2: 'Teren dificil. Agentul poate trece, dar consumă mai multă energie.',
  3: 'Resursă de hrană. Agentul câștigă energie și recompensă când o colectează.',
  4: 'Zonă periculoasă. Intrarea aici termină episodul negativ.',
  5: 'Obiectivul final. Agentul încearcă să ajungă aici pentru succes.',
  6: 'Poziția de pornire a agentului la începutul episodului.',
};

const paintTools = [0, 1, 2, 3, 4, 6, 5];
const actionNames = ['SUS', 'JOS', 'STÂNGA', 'DREAPTA', 'STAI'];
const statusLabels: Record<string, string> = {
  queued: 'În așteptare',
  running: 'În rulare',
  completed: 'Finalizat',
  failed: 'Eșuat',
  cancelled: 'Anulat',
};
const outcomeLabels: Record<string, string> = {
  target_reached: 'Țintă atinsă',
  energy_depleted: 'Energie epuizată',
  danger: 'Agent pierdut în pericol',
  timeout: 'Limită de pași',
};
const backendCellLabels: Record<string, string> = {
  EMPTY: 'Liber',
  OBSTACLE: 'Obstacol',
  MUD: 'Noroi',
  FOOD: 'Hrană',
  DANGER: 'Pericol',
  TARGET: 'Țintă',
  START: 'Pornire',
};
const artifactLabels: Record<string, string> = {
  results_csv: 'Rezultate CSV',
  convergence_png: 'Grafic convergență',
  epsilon_png: 'Grafic epsilon',
  success_png: 'Grafic succes',
  qtable_path: 'Tabel Q',
  greedy_trajectory_csv: 'Traseu lacom CSV',
  greedy_trajectory_json: 'Traseu lacom JSON',
  manifest_json: 'Manifest JSON',
  environment_map_png: 'Hartă mediu',
  q_heatmap_png: 'Hartă valori Q',
  policy_png: 'Politică învățată',
  visits_png: 'Vizite stări',
  td_error_png: 'Eroare TD',
  greedy_path_png: 'Traseu lacom',
};

function absoluteUrl(path?: string) {
  if (!path) return '#';
  return path.startsWith('http') ? path : `${API}${path}`;
}

function translateStatus(status?: string) {
  return status ? statusLabels[status] ?? status : '-';
}

function translateOutcome(outcome?: string) {
  return outcome ? outcomeLabels[outcome] ?? outcome : '-';
}

function translateBackendCell(cell?: string) {
  return cell ? backendCellLabels[cell] ?? cell : 'Nicio celulă încă';
}

function InfoTip({ text }: { text: string }) {
  return (
    <span className="info-tip" tabIndex={0} aria-label={text}>
      <HelpCircle size={15} />
      <span className="tooltip" role="tooltip">{text}</span>
    </span>
  );
}

function SectionTitle({ children, tip }: { children: React.ReactNode; tip: string }) {
  return (
    <h2 className="section-title">
      {children}
      <InfoTip text={tip} />
    </h2>
  );
}

function FieldLabel({
  children,
  tip,
}: {
  children: React.ReactNode;
  tip: string;
}) {
  return (
    <span className="field-label">
      {children}
      <InfoTip text={tip} />
    </span>
  );
}

function CellLegend() {
  return (
    <div className="cell-legend" aria-label="Legendă tipuri de celule">
      {paintTools.map((cell) => (
        <div
          className="legend-item"
          key={cell}
          title={cellDescriptions[cell]}
        >
          <span style={{ background: cellColors[cell] }} />
          <b>{cellLabels[cell]}</b>
        </div>
      ))}
    </div>
  );
}

function environmentFromGrid(payload: GridPayload, name = 'Mediu personalizat'): EnvironmentPayload {
  return {
    id: payload.id ?? 'custom_preview',
    name: payload.name ?? name,
    rows: payload.rows,
    cols: payload.cols,
    start: payload.start,
    target: payload.target,
    grid: payload.grid,
  };
}

function MetricCard({
  title,
  value,
  icon,
  tip,
}: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  tip: string;
}) {
  return (
    <div className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span className="metric-title">{title}<InfoTip text={tip} /></span>
      <strong>{value}</strong>
    </div>
  );
}

function GridView({
  grid,
  live,
  trajectory,
  replayStep,
  editable = false,
  selectedTool,
  onCellClick,
}: {
  grid?: GridPayload | EnvironmentPayload;
  live?: LiveEvent;
  trajectory?: TrajectoryStep[];
  replayStep?: number;
  editable?: boolean;
  selectedTool?: number;
  onCellClick?: (row: number, col: number) => void;
}) {
  if (!grid) {
    return <div className="empty-grid">Alege un scenariu și pornește antrenarea pentru a vedea mediul.</div>;
  }

  const visibleTrajectory = trajectory && replayStep !== undefined
    ? trajectory.slice(0, replayStep + 1)
    : trajectory;
  const replayAgent = trajectory && replayStep !== undefined ? trajectory[replayStep] : undefined;
  const agentPos = live?.agent?.position ?? (
    replayAgent
      ? [replayAgent.row, replayAgent.col]
      : visibleTrajectory && visibleTrajectory.length > 0
        ? [visibleTrajectory[visibleTrajectory.length - 1].row, visibleTrajectory[visibleTrajectory.length - 1].col]
        : undefined
  );
  const feedback = live?.info?.feedback;
  const trail = new Set((visibleTrajectory ?? []).map((step) => `${step.row}-${step.col}`));

  return (
    <div
      className={`grid ${editable ? 'editable-grid' : ''}`}
      style={{ gridTemplateColumns: `repeat(${grid.cols}, minmax(12px, 1fr))` }}
    >
      {grid.grid.flatMap((row, r) =>
        row.map((cell, c) => {
          const isAgent = agentPos?.[0] === r && agentPos?.[1] === c;
          const isLast = feedback?.new_pos?.[0] === r && feedback?.new_pos?.[1] === c;
          const isTrail = trail.has(`${r}-${c}`);
          return (
            <button
              type="button"
              key={`${r}-${c}`}
              className={`cell ${isAgent ? 'agent-cell' : ''} ${isLast ? 'last-cell' : ''} ${isTrail ? 'trail-cell' : ''}`}
              style={{ background: cellColors[cell] ?? '#7ddf88' }}
              title={`Rând ${r}, coloană ${c}. Tip celulă: ${cellLabels[cell] ?? cell}. ${editable ? 'Click pentru a aplica unealta selectată.' : isTrail ? 'Celula face parte din traseul evaluării.' : 'Celulă din mediul curent.'}`}
              disabled={!editable}
              onClick={() => onCellClick?.(r, c)}
              aria-label={`celula ${r} ${c}`}
            >
              {editable && selectedTool === cell ? <span className="paint-hint" /> : null}
              {isAgent ? <span className="agent-dot" /> : null}
            </button>
          );
        }),
      )}
    </div>
  );
}

export function App() {
  const [scenario, setScenario] = useState('B');
  const [episodes, setEpisodes] = useState(200);
  const [seed, setSeed] = useState(42);
  const [preview, setPreview] = useState<GridPayload>();
  const [builderEnvironment, setBuilderEnvironment] = useState<EnvironmentPayload>();
  const [builderTool, setBuilderTool] = useState(1);
  const [builderMessage, setBuilderMessage] = useState('Editează harta, apoi valideaz-o înainte de evaluare.');
  const [job, setJob] = useState<JobSnapshot>();
  const [runs, setRuns] = useState<JobSnapshot[]>([]);
  const [live, setLive] = useState<LiveEvent>();
  const [chart, setChart] = useState<{ step: number; reward: number; energy: number }[]>([]);
  const [qtables, setQTables] = useState<QTableItem[]>([]);
  const [evaluationScenarios, setEvaluationScenarios] = useState<EvaluationScenario[]>([]);
  const [qtablePath, setQtablePath] = useState('');
  const [environmentJson, setEnvironmentJson] = useState('');
  const [storedEnvironments, setStoredEnvironments] = useState<StoredEnvironment[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationResult[]>([]);
  const [selectedEvaluationIndex, setSelectedEvaluationIndex] = useState(0);
  const [replayStep, setReplayStep] = useState(0);
  const [replayPlaying, setReplayPlaying] = useState(false);
  const [replaySpeedMs, setReplaySpeedMs] = useState(350);

  const loadQTables = async () => {
    const response = await fetch(`${API}/api/qtables`);
    const payload = await response.json();
    setQTables(payload.qtables ?? []);
  };

  const loadRuns = async () => {
    const response = await fetch(`${API}/api/runs`);
    const payload = await response.json();
    setRuns(payload.runs ?? []);
  };

  const loadStoredEnvironments = async () => {
    const response = await fetch(`${API}/api/environments`);
    const payload = await response.json();
    setStoredEnvironments(payload.environments ?? []);
  };

  const loadEvaluationScenarios = async () => {
    const response = await fetch(`${API}/api/evaluation-scenarios`);
    const payload = await response.json();
    setEvaluationScenarios(payload.scenarios ?? []);
  };

  useEffect(() => {
    fetch(`${API}/api/environments/preview?scenario=${scenario}&rows=20&cols=20&seed=${seed}`)
      .then((res) => res.json())
      .then((payload: GridPayload) => {
        const nextEnvironment = environmentFromGrid(payload, 'Mediu de previzualizare');
        setPreview(payload);
        setBuilderEnvironment(nextEnvironment);
        setEnvironmentJson(JSON.stringify(nextEnvironment, null, 2));
        setBuilderMessage(`Previzualizare încărcată. Drum BFS optim: ${payload.bfs_distance ?? 'indisponibil'} pași.`);
      })
      .catch(() => undefined);
  }, [scenario, seed]);

  useEffect(() => {
    void loadQTables();
    void loadRuns();
    void loadStoredEnvironments();
    void loadEvaluationScenarios();
  }, []);

  const startTraining = async () => {
    setChart([]);
    setEvaluation([]);
    const response = await fetch(`${API}/api/train`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario, rows: 20, cols: 20, seed, episodes }),
    });
    const created: JobSnapshot = await response.json();
    setJob(created);
    void loadRuns();

    const source = new EventSource(`${API}/api/stream/${created.id}`);
    source.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.type === 'step') {
        setLive(payload);
        setChart((items) => [
          ...items.slice(-120),
          {
            step: payload.agent?.steps ?? 0,
            reward: payload.agent?.reward ?? 0,
            energy: payload.agent?.energy ?? 0,
          },
        ]);
      }
      if (payload.type === 'job_status') {
        setJob(payload);
        if (payload.artifacts?.qtable_path) {
          setQtablePath(payload.artifacts.qtable_path);
        }
        if (['completed', 'failed', 'cancelled'].includes(payload.status)) {
          source.close();
          void loadQTables();
          void loadRuns();
        }
      }
    };
  };

  const parseEnvironmentBatch = () => {
    const payload = JSON.parse(environmentJson);
    return Array.isArray(payload) ? payload : [payload];
  };

  const runEvaluation = async () => {
    const environments = parseEnvironmentBatch();
    const response = await fetch(`${API}/api/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        qtable_path: qtablePath,
        environments,
        energy: 100,
      }),
    });
    const payload = await response.json();
    setEvaluation(payload.results ?? []);
    setSelectedEvaluationIndex(0);
    setReplayStep(0);
    setReplayPlaying((payload.results ?? []).length > 0);
  };

  const paintCell = (row: number, col: number) => {
    if (!builderEnvironment) return;
    const nextGrid = builderEnvironment.grid.map((gridRow) => [...gridRow]);
    const isStart = builderEnvironment.start[0] === row && builderEnvironment.start[1] === col;
    const isTarget = builderEnvironment.target[0] === row && builderEnvironment.target[1] === col;

    if (builderTool === 6) {
      nextGrid[builderEnvironment.start[0]][builderEnvironment.start[1]] = 0;
      nextGrid[row][col] = 6;
      updateBuilder({ ...builderEnvironment, start: [row, col], grid: nextGrid });
      return;
    }
    if (builderTool === 5) {
      nextGrid[builderEnvironment.target[0]][builderEnvironment.target[1]] = 0;
      nextGrid[row][col] = 5;
      updateBuilder({ ...builderEnvironment, target: [row, col], grid: nextGrid });
      return;
    }
    if (isStart || isTarget) {
      setBuilderMessage('Mută mai întâi startul/ținta, apoi revopsește acea celulă.');
      return;
    }
    nextGrid[row][col] = builderTool;
    updateBuilder({ ...builderEnvironment, grid: nextGrid });
  };

  const updateBuilder = (environment: EnvironmentPayload) => {
    setBuilderEnvironment(environment);
    setEnvironmentJson(JSON.stringify(environment, null, 2));
    setBuilderMessage('Harta a fost modificată. Valideaz-o înainte să o folosești la testare.');
  };

  const validateBuilder = async () => {
    if (!builderEnvironment) return;
    const response = await fetch(`${API}/api/environments/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(builderEnvironment),
    });
    const payload = await response.json();
    if (!response.ok) {
      setBuilderMessage(payload.detail ?? 'Mediul nu este valid.');
      return;
    }
    setBuilderMessage(`Hartă validă. Drum BFS optim: ${payload.environment.bfs_distance ?? 'indisponibil'} pași.`);
  };

  const saveBuilder = async () => {
    if (!builderEnvironment) return;
    const response = await fetch(`${API}/api/environments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(builderEnvironment),
    });
    const payload = await response.json();
    if (!response.ok) {
      setBuilderMessage(payload.detail ?? 'Mediul nu a putut fi salvat.');
      return;
    }
    setBuilderMessage(`Salvat ca ${payload.environment.id}.`);
    void loadStoredEnvironments();
  };

  const loadStoredEnvironment = async (environmentId: string) => {
    const response = await fetch(`${API}/api/environments/${environmentId}`);
    const payload: GridPayload = await response.json();
    const nextEnvironment = environmentFromGrid(payload, payload.name ?? environmentId);
    setBuilderEnvironment(nextEnvironment);
    setEnvironmentJson(JSON.stringify(nextEnvironment, null, 2));
    setPreview(payload);
  };

  const useBuilderForEvaluation = () => {
    if (!builderEnvironment) return;
    setEnvironmentJson(JSON.stringify(builderEnvironment, null, 2));
    setBuilderMessage('Harta din editor a fost copiată în payload-ul de evaluare.');
  };

  const loadEvaluationScenario = (scenarioPreset: EvaluationScenario) => {
    const environment = environmentFromGrid(scenarioPreset.environment, scenarioPreset.name);
    setEnvironmentJson(JSON.stringify(environment, null, 2));
    setPreview(scenarioPreset.environment);
    setBuilderEnvironment(environment);
    setReplayPlaying(false);
    setReplayStep(0);
  };

  const loadAllEvaluationScenarios = () => {
    const environments = evaluationScenarios.map((scenarioPreset) =>
      environmentFromGrid(scenarioPreset.environment, scenarioPreset.name),
    );
    setEnvironmentJson(JSON.stringify(environments, null, 2));
    setReplayPlaying(false);
    setReplayStep(0);
  };

  const selectedEvaluation = evaluation[selectedEvaluationIndex];
  const replayCurrentStep = selectedEvaluation?.trajectory?.[replayStep];
  const replayLive: LiveEvent | undefined = selectedEvaluation && replayCurrentStep
    ? {
        type: 'replay',
        agent: {
          position: [replayCurrentStep.row, replayCurrentStep.col],
          energy: replayCurrentStep.energy,
          energy_percent: replayCurrentStep.energy,
          steps: replayCurrentStep.step + 1,
          reward: replayCurrentStep.total_reward,
          alive: !replayCurrentStep.terminal_reason,
          reached_target: replayCurrentStep.terminal_reason === 'target_reached',
        },
        info: {
          feedback: {
            action: replayCurrentStep.action,
            reward: replayCurrentStep.reward,
            energy_delta: undefined,
            previous_pos: [replayCurrentStep.previous_row, replayCurrentStep.previous_col],
            new_pos: [replayCurrentStep.row, replayCurrentStep.col],
            terminal_reason: replayCurrentStep.terminal_reason,
            cell_type: replayCurrentStep.cell_type,
          },
        },
      }
    : undefined;
  const displayGrid = selectedEvaluation?.environment ?? live?.environment ?? preview ?? builderEnvironment;
  const displayTrajectory = selectedEvaluation?.trajectory;
  const displayLive = replayLive ?? live;
  const knowledge = live?.info?.learning?.knowledge;
  const feedback = displayLive?.info?.feedback;
  const actionCounts = live?.info?.live?.action_counts ?? [0, 0, 0, 0, 0];
  const totalActions = Math.max(1, actionCounts.reduce((sum, value) => sum + value, 0));
  const progressPct = Math.round((job?.progress ?? 0) * 100);
  const maxReplayStep = Math.max(0, (selectedEvaluation?.trajectory?.length ?? 1) - 1);

  const statusLabel = useMemo(() => {
    if (!job) return 'Inactiv';
    return `${translateStatus(job.status)} · ${progressPct}%`;
  }, [job, progressPct]);

  useEffect(() => {
    setReplayStep(0);
    setReplayPlaying(false);
  }, [selectedEvaluationIndex]);

  useEffect(() => {
    if (!replayPlaying || !selectedEvaluation || maxReplayStep <= 0) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      setReplayStep((currentStep) => {
        if (currentStep >= maxReplayStep) {
          setReplayPlaying(false);
          return currentStep;
        }
        return currentStep + 1;
      });
    }, replaySpeedMs);
    return () => window.clearInterval(timer);
  }, [replayPlaying, selectedEvaluation, maxReplayStep, replaySpeedMs]);

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Navigare autonomă cu Q-Learning</p>
          <h1>Antrenează, observă și testează agentul pe medii noi.</h1>
          <p className="hero-help">Treci cu mouse-ul peste iconițele „?” sau peste elementele din hartă pentru explicații.</p>
        </div>
        <div
          className="status-pill"
          title="Arată starea jobului de antrenare curent și procentul aproximativ de progres."
        >
          {statusLabel}
        </div>
      </section>

      <section className="workspace">
        <aside className="control-panel">
          <div className="panel-card">
            <SectionTitle tip="Aici alegi tipul experimentului, sămânța de generare și câte episoade de antrenare rulează agentul.">
              Configurare antrenare
            </SectionTitle>
            <label>
              <FieldLabel tip="Scenariul schimbă regulile problemei: navigare simplă, supraviețuire cu energie, hartă dinamică sau depozit fix.">
                Scenariu
              </FieldLabel>
              <select value={scenario} onChange={(event) => setScenario(event.target.value)}>
                <option value="A">A · Navigare</option>
                <option value="B">B · Supraviețuire</option>
                <option value="C">C · Hartă dinamică</option>
                <option value="WAREHOUSE">Depozit</option>
              </select>
            </label>
            <label>
              <FieldLabel tip="Sămânța controlează generarea hărții. Aceeași valoare produce aceeași hartă, util pentru experimente reproductibile.">
                Sămânță aleatoare
              </FieldLabel>
              <input type="number" value={seed} onChange={(event) => setSeed(Number(event.target.value))} />
            </label>
            <label>
              <FieldLabel tip="Un episod este o încercare completă a agentului de la start până la țintă, moarte sau timeout. Mai multe episoade înseamnă mai multă învățare.">
                Episoade
              </FieldLabel>
              <input type="number" value={episodes} onChange={(event) => setEpisodes(Number(event.target.value))} />
            </label>
            <button
              className="primary-button"
              onClick={startTraining}
              title="Pornește un job de antrenare în backend și începe transmiterea progresului live către interfață."
            >
              <Play size={18} /> Pornește antrenarea
            </button>
          </div>

          <div className="panel-card">
            <SectionTitle tip="Editorul îți permite să creezi sau să modifici o hartă de test prin click pe celule. Harta poate fi validată și salvată.">
              Editor de medii
            </SectionTitle>
            <div className="tool-grid">
              {paintTools.map((tool) => (
                <button
                  type="button"
                  className={builderTool === tool ? 'tool active-tool' : 'tool'}
                  key={tool}
                  onClick={() => setBuilderTool(tool)}
                  title={`Selectează unealta ${cellLabels[tool]}. După selectare, click pe hartă aplică acest tip de celulă.`}
                >
                  <span style={{ background: cellColors[tool] }} />
                  {cellLabels[tool]}
                </button>
              ))}
            </div>
            <div className="builder-grid-wrap">
              <GridView
                grid={builderEnvironment}
                editable
                selectedTool={builderTool}
                onCellClick={paintCell}
              />
            </div>
            <p className="builder-message">{builderMessage}</p>
            <div className="button-row">
              <button
                className="secondary-button"
                onClick={validateBuilder}
                title="Verifică dacă există un drum valid de la pornire la țintă folosind BFS."
              >
                <MousePointer2 size={16} /> Validează
              </button>
              <button
                className="secondary-button"
                onClick={saveBuilder}
                title="Salvează harta curentă ca fișier JSON în data/environments, ca să o poți reutiliza ulterior."
              >
                <Save size={16} /> Salvează
              </button>
            </div>
            <button
              className="secondary-button quiet-button"
              onClick={useBuilderForEvaluation}
              title="Copiază harta construită în câmpul de evaluare, pentru a testa tabelul Q pe ea."
            >
              Folosește harta editorului la evaluare
            </button>
          </div>

          <div className="panel-card">
            <SectionTitle tip="Evaluarea folosește o politică deja învățată, salvată într-un tabel Q, și o rulează lacom pe una sau mai multe hărți.">
              Evaluare pe lot
            </SectionTitle>
            <div className="preset-list">
              <div className="preset-header">
                <b>Scenarii de test</b>
                <button
                  type="button"
                  onClick={loadAllEvaluationScenarios}
                  disabled={evaluationScenarios.length === 0}
                  title="Încarcă toate scenariile predefinite ca listă JSON, pentru comparație rapidă."
                >
                  Toate
                </button>
              </div>
              {evaluationScenarios.map((scenarioPreset) => (
                <button
                  type="button"
                  className="preset-card"
                  key={scenarioPreset.id}
                  onClick={() => loadEvaluationScenario(scenarioPreset)}
                  title={scenarioPreset.description}
                >
                  <strong>{scenarioPreset.name}</strong>
                  <span>{scenarioPreset.description}</span>
                  <small>BFS optim: {scenarioPreset.environment.bfs_distance ?? 'indisponibil'} pași</small>
                </button>
              ))}
            </div>
            <label>
              <FieldLabel tip="Tabelul Q conține ce a învățat agentul: valoarea fiecărei acțiuni pentru fiecare stare discretă.">
                Tabel Q
              </FieldLabel>
              <select value={qtablePath} onChange={(event) => setQtablePath(event.target.value)}>
                <option value="">Selectează un tabel Q salvat</option>
                {qtables.map((item) => (
                  <option key={item.path} value={item.path}>
                    {item.run_id} · {item.path}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <FieldLabel tip="Poți introduce manual calea către un fișier .npy dacă nu apare în lista de mai sus.">
                Cale manuală către tabelul Q
              </FieldLabel>
              <input value={qtablePath} onChange={(event) => setQtablePath(event.target.value)} placeholder="data/runs/<id>/qtable.npy" />
            </label>
            <label>
              <FieldLabel tip="Aici se află harta de test. Poate fi un singur obiect JSON sau o listă de obiecte JSON pentru evaluare pe lot.">
                Mediu JSON sau listă JSON de medii
              </FieldLabel>
              <textarea value={environmentJson} onChange={(event) => setEnvironmentJson(event.target.value)} rows={8} />
            </label>
            <button
              className="secondary-button"
              onClick={runEvaluation}
              disabled={!qtablePath || !environmentJson}
              title="Rulează agentul fără explorare: la fiecare pas alege acțiunea cu valoarea Q cea mai mare."
            >
              <Route size={16} /> Rulează evaluarea lacomă
            </button>
          </div>

          <div className="panel-card">
            <SectionTitle tip="Lista hărților personalizate salvate local. Selectarea uneia o încarcă în editor și în previzualizare.">
              Hărți salvate
            </SectionTitle>
            <button
              className="secondary-button quiet-button"
              onClick={loadStoredEnvironments}
              title="Reîncarcă lista de hărți JSON salvate în data/environments."
            >
              <RefreshCw size={16} /> Reîncarcă hărțile
            </button>
            {storedEnvironments.length === 0 ? (
              <p className="muted">Nu există încă hărți personalizate salvate.</p>
            ) : (
              <div className="compact-list">
                {storedEnvironments.map((environment) => (
                  <button
                    key={environment.id}
                    onClick={() => loadStoredEnvironment(environment.id)}
                    title={`Încarcă harta ${environment.name}. Drum BFS optim: ${environment.bfs_distance ?? 'indisponibil'} pași.`}
                  >
                    <Map size={15} />
                    <span>{environment.name}</span>
                    <b>{environment.rows}×{environment.cols}</b>
                  </button>
                ))}
              </div>
            )}
          </div>
        </aside>

        <section className="simulation-stage">
          <div className="stage-help">
            <InfoTip text="Grila centrală arată mediul curent. Punctul alb este agentul, conturul galben marchează ultima poziție, iar punctele albe mici arată traseul unei evaluări selectate." />
            <span>Hartă și traseu agent</span>
          </div>
          <GridView
            grid={displayGrid}
            live={selectedEvaluation ? undefined : live}
            trajectory={displayTrajectory}
            replayStep={selectedEvaluation ? replayStep : undefined}
          />
          {selectedEvaluation ? (
            <div className="replay-panel">
              <div className="replay-summary">
                <strong>{selectedEvaluation.environment.name ?? selectedEvaluation.environment.id ?? 'Evaluare'}</strong>
                <span>
                  Pas {Math.min(replayStep + 1, selectedEvaluation.trajectory.length)} / {selectedEvaluation.trajectory.length}
                  {' · '}
                  Acțiune {replayCurrentStep ? actionNames[replayCurrentStep.action] : '-'}
                  {' · '}
                  Energie {replayCurrentStep?.energy.toFixed(0) ?? '-'}
                </span>
              </div>
              <div className="replay-controls">
                <button
                  type="button"
                  onClick={() => setReplayStep(0)}
                  title="Revino la primul pas al traseului."
                >
                  <SkipBack size={16} /> Resetare
                </button>
                <button
                  type="button"
                  onClick={() => setReplayStep((step) => Math.max(0, step - 1))}
                  title="Mergi cu un pas înapoi în replay."
                >
                  -1
                </button>
                <button
                  type="button"
                  onClick={() => setReplayPlaying((playing) => !playing)}
                  title="Pornește sau oprește animația traseului greedy."
                >
                  {replayPlaying ? <Pause size={16} /> : <Play size={16} />}
                  {replayPlaying ? 'Pauză' : 'Redare'}
                </button>
                <button
                  type="button"
                  onClick={() => setReplayStep((step) => Math.min(maxReplayStep, step + 1))}
                  title="Avansează cu un pas în replay."
                >
                  +1
                </button>
                <button
                  type="button"
                  onClick={() => setReplayStep(maxReplayStep)}
                  title="Sari direct la ultimul pas al evaluării."
                >
                  Final <SkipForward size={16} />
                </button>
              </div>
              <label className="speed-control">
                Viteză replay
                <select value={replaySpeedMs} onChange={(event) => setReplaySpeedMs(Number(event.target.value))}>
                  <option value={700}>Lent</option>
                  <option value={350}>Normal</option>
                  <option value={140}>Rapid</option>
                </select>
              </label>
            </div>
          ) : null}
          <CellLegend />
          {selectedEvaluation ? (
            <div className="stage-caption">
              Traseu lacom pentru {selectedEvaluation.environment.name ?? selectedEvaluation.environment.id ?? 'evaluare'}.
            </div>
          ) : null}
        </section>

        <aside className="dashboard">
          <div className="panel-card dashboard-card">
            <SectionTitle tip="Rezumatul stării curente a agentului în timpul antrenării sau al evaluării selectate.">
              Starea agentului
            </SectionTitle>
            <div className="metrics-grid">
              <MetricCard
                title="Energie"
                value={displayLive?.agent ? displayLive.agent.energy.toFixed(0) : '-'}
                icon={<Activity size={18} />}
                tip="Nivelul de energie rămas. Dacă ajunge la zero, episodul se termină cu eșec."
              />
              <MetricCard
                title="Recompensă"
                value={displayLive?.agent ? displayLive.agent.reward.toFixed(1) : '-'}
                icon={<BarChart3 size={18} />}
                tip="Suma recompenselor primite în episodul curent. Crește la hrană/țintă și scade la pași, noroi, obstacole sau moarte."
              />
              <MetricCard
                title="Pași"
                value={displayLive?.agent?.steps ?? selectedEvaluation?.steps ?? '-'}
                icon={<Route size={18} />}
                tip="Numărul de acțiuni executate de agent în episod sau în evaluarea selectată."
              />
              <MetricCard
                title="Q completat"
                value={knowledge ? `${knowledge.fill_pct.toFixed(1)}%` : '-'}
                icon={<Brain size={18} />}
                tip="Procentul de intrări nenule din tabelul Q. Indică cât de mult din spațiul stărilor a fost influențat de învățare."
              />
            </div>
          </div>

          <div className="panel-card dashboard-card">
            <SectionTitle tip="Arată ultima acțiune executată și feedback-ul imediat primit din mediu.">
              Ultima decizie
            </SectionTitle>
            <div
              className="decision-card"
              title="Acest card ajută la înțelegerea pas-cu-pas a comportamentului agentului."
            >
              <strong>{feedback?.action !== undefined ? actionNames[feedback.action] : 'Așteptare'}</strong>
              <span>Recompensă {feedback?.reward?.toFixed(1) ?? '-'}</span>
              <span>Energie {feedback?.energy_delta ?? '-'}</span>
              <span>{translateBackendCell(feedback?.cell_type)}</span>
            </div>
          </div>

          <div className="panel-card dashboard-card">
            <SectionTitle tip="Numără de câte ori agentul a ales fiecare acțiune în episodul curent. Ajută la observarea blocajelor sau preferințelor.">
              Distribuția acțiunilor
            </SectionTitle>
            {actionCounts.map((count, index) => (
              <div
                className="action-row"
                key={actionNames[index]}
                title={`Acțiunea ${actionNames[index]} a fost aleasă de ${count} ori în episodul curent.`}
              >
                <span>{actionNames[index]}</span>
                <div className="action-bar">
                  <div style={{ width: `${(count / totalActions) * 100}%` }} />
                </div>
                <b>{count}</b>
              </div>
            ))}
          </div>

          <div className="panel-card dashboard-card chart-card">
            <SectionTitle tip="Graficul urmărește recompensa agentului în ultimele momente transmise de backend.">
              Evoluție în timp real
            </SectionTitle>
            <ResponsiveContainer width="100%" height={170}>
              <AreaChart data={chart}>
                <defs>
                  <linearGradient id="reward" x1="0" x2="0" y1="0" y2="1">
                    <stop offset="5%" stopColor="#5eead4" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#5eead4" stopOpacity={0.05} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="step" hide />
                <YAxis hide />
                <Tooltip />
                <Area type="monotone" dataKey="reward" stroke="#5eead4" fill="url(#reward)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="panel-card dashboard-card">
            <SectionTitle tip="Comparația rulărilor greedy pe hărți de test. Diferența față de BFS arată cât de departe este traseul agentului de drumul minim topologic.">
              Rezultate evaluare
            </SectionTitle>
            {evaluation.length === 0 ? (
              <p className="muted">Selectează un tabel Q, lipește o hartă sau o listă JSON, apoi rulează evaluarea lacomă.</p>
            ) : (
              <div className="evaluation-list">
                {evaluation.map((result, index) => (
                  <button
                    className={index === selectedEvaluationIndex ? 'evaluation-result active-evaluation' : 'evaluation-result'}
                    key={`${result.environment?.id ?? index}`}
                    onClick={() => setSelectedEvaluationIndex(index)}
                    title="Click pentru a afișa traseul acestei evaluări pe grila centrală."
                  >
                    <strong>{translateOutcome(result.outcome)}</strong>
                    <span>{result.environment?.name ?? result.environment?.id ?? `Hartă ${index + 1}`}</span>
                    <span>Pași: {result.steps} · Recompensă: {result.reward?.toFixed?.(1) ?? result.reward}</span>
                    <span>Diferență față de BFS: {result.bfs_overhead ?? '-'}</span>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="panel-card dashboard-card">
            <SectionTitle tip="Rulările de antrenare salvate de backend. Alegerea unei rulări recuperează artefactele și tabelul Q asociat.">
              Rulări recente
            </SectionTitle>
            <button
              className="secondary-button quiet-button"
              onClick={loadRuns}
              title="Reîncarcă indexul local al rulărilor din data/runs/index.json."
            >
              <RefreshCw size={16} /> Reîncarcă rulările
            </button>
            <div className="compact-list">
              {runs.slice(0, 5).map((run) => (
                <button
                  key={run.id}
                  onClick={() => {
                    setJob(run);
                    if (run.artifacts?.qtable_path) setQtablePath(run.artifacts.qtable_path);
                  }}
                  title="Selectează această rulare pentru a vedea artefactele și pentru a reutiliza tabelul Q la evaluare."
                >
                  <span>{run.id}</span>
                  <b>{translateStatus(run.status)}</b>
                </button>
              ))}
            </div>
          </div>

          <div className="panel-card dashboard-card">
            <SectionTitle tip="Fișierele produse după antrenare: rezultate CSV, grafice PNG, manifest JSON, traseu lacom și tabel Q.">
              Artefacte rulare
            </SectionTitle>
            {job?.artifacts && Object.keys(job.artifacts).length > 0 ? (
              <div className="artifact-list">
                {Object.entries(job.artifacts).map(([key, value]) => (
                  <div
                    key={key}
                    title="Artefact generat automat pentru analiză, reproducibilitate sau reutilizare în evaluări."
                  >
                    <b>{artifactLabels[key] ?? key}</b>
                    <code>{value}</code>
                    <a
                      href={absoluteUrl(`/api/runs/${job.id}/artifacts/${key}/download`)}
                      title="Descarcă acest fișier din directorul rulării."
                    >
                      <Download size={14} /> Descarcă
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">Artefactele apar aici după finalizarea antrenării.</p>
            )}
          </div>
        </aside>
      </section>
    </main>
  );
}
