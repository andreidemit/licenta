import { type FormEvent, useState } from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Dice5,
  Lightbulb,
  Loader2,
  Play,
  RefreshCw,
  Send,
  Settings2,
  Shuffle,
  X,
} from 'lucide-react';
import { ExperimentDashboard } from './ExperimentDashboard';
import { GridWorldView } from './GridWorldView';
import { AiAnalystPanel } from './AiAnalystPanel';
import { ScenarioConfigDialog } from './ScenarioConfigDialog';
import { TooltipLabel } from './TooltipLabel';
import { ExportPanel } from './analysis/ExportPanel';
import { FailureBreakdown } from './analysis/FailureBreakdown';
import { MetricCIBars } from './analysis/MetricCIBars';
import { OccupancyHeatmap } from './analysis/OccupancyHeatmap';
import { PerMapHeatmap } from './analysis/PerMapHeatmap';
import { RewardDistribution } from './analysis/RewardDistribution';
import { RiskRewardScatter } from './analysis/RiskRewardScatter';
import { getExperimentProfile } from './experimentProfiles';
import type {
  MonteCarloResult,
  MonteCarloLiveEvent,
  MonteCarloLiveState,
  LlmConfigResponse,
  SafeEnvironment,
  SafeEpisodeResult,
  SafeNavigationConfig,
  SafeScenarioPreset,
} from './types';

const algorithms = [
  ['random', 'Aleator'],
  ['rule_based', 'Bazat pe reguli'],
  ['astar', 'A*'],
  ['risk_aware_astar', 'A* conștient de risc'],
  ['tabular_q', 'Q-Learning tabular'],
  ['feature_q', 'Q-Learning pe trăsături'],
  ['feature_risk_astar', 'Feature-Risk A* experimental'],
];

const learningAlgorithms = new Set(['tabular_q', 'feature_q', 'feature_risk_astar']);

const objectiveLabels: Record<SafeNavigationConfig['optimization_objective'], string> = {
  balanced: 'Echilibrat',
  safety_first: 'Siguranță',
  efficiency_first: 'Eficiență',
  robustness_first: 'Robustețe',
};

const objectiveDescriptions: Record<SafeNavigationConfig['optimization_objective'], string> = {
  balanced: 'Combină succes, risc, cost, pași și erori operaționale.',
  safety_first: 'Prioritizează risc mic, coliziuni puține și evitarea pericolului.',
  efficiency_first: 'Prioritizează trasee scurte și cost total mic, fără a ignora succesul.',
  robustness_first: 'Prioritizează succes stabil, timeout mic și comportament consistent.',
};

const scenarios = [
  ['easy', 'Ușor', 'Hartă mică, puține obstacole și risc redus.'],
  ['medium', 'Mediu', 'Echilibru între obstacole, pericole și spațiu de navigare.'],
  ['hard', 'Dificil', 'Hartă mare, densitate ridicată și expunere mai mare la risc.'],
  ['custom', 'Personalizat', 'Configurează dimensiunea, densitățile și seed-ul.'],
];

const monteCarloTabs = [
  { id: 'distributions', label: 'Distribuții', tooltip: 'Arată variabilitatea metricilor pe episoade pentru fiecare agent.' },
  { id: 'ci-bars', label: 'Intervale 95%', tooltip: 'CI 95% = interval de încredere 95%, estimat prin bootstrap.' },
  { id: 'pareto', label: 'Risc / Recompensă', tooltip: 'Scatter plot pentru compromis între siguranță și scorul total.' },
  { id: 'per-map', label: 'Per-hartă', tooltip: 'Compară performanța fiecărui agent pe fiecare seed de hartă.' },
  { id: 'failures', label: 'Eșecuri', tooltip: 'Descompune finalizările în succes, pericol, coliziune, timeout sau alte cazuri.' },
  { id: 'occupancy', label: 'Ocupare', tooltip: 'Heatmap cu celulele vizitate de traseele agenților.' },
  { id: 'export', label: 'Export', tooltip: 'Descarcă rezultatele și graficele pentru raport sau prezentare.' },
];

export type WizardStage = 'scenario' | 'run' | 'results';

type Props = {
  activeStage: WizardStage;
  config: SafeNavigationConfig;
  scenarioPresets: SafeScenarioPreset[];
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
  liveMonteCarlo?: MonteCarloLiveState;
  busy: boolean;
  busyAction?: 'map' | 'episode' | 'monte-carlo' | 'config';
  pendingMapConfig: boolean;
  showPath: boolean;
  showRisk: boolean;
  showCoordinates: boolean;
  onStageChange: (stage: WizardStage) => void;
  onChange: (config: SafeNavigationConfig) => void;
  onDescribeConfig: (prompt: string) => Promise<LlmConfigResponse | undefined>;
  onPreview: (config?: SafeNavigationConfig) => void;
  onMonteCarlo: () => void;
  onTogglePath: () => void;
  onToggleRisk: () => void;
  onToggleCoordinates: () => void;
};

function createRandomSeed() {
  return Math.floor(Math.random() * 1_000_000);
}

function fmtProbability(value: number) {
  return `${Math.round(value * 100)}%`;
}

function presetFor(scenario: string, presets: SafeScenarioPreset[]) {
  return presets.find((preset) => preset.id === scenario);
}

function scenarioConfig(config: SafeNavigationConfig, presets: SafeScenarioPreset[]) {
  if (config.scenario === 'custom') return config;
  return presetFor(config.scenario, presets) ?? config;
}

function algorithmLabel(value: string) {
  const backendLabels: Record<string, string> = {
    Random: 'Aleator',
    'Rule-Based': 'Bazat pe reguli',
    'Risk-Aware A*': 'A* conștient de risc',
    'Tabular Q-Learning': 'Q-Learning tabular',
    'Feature-Based Q-Learning': 'Q-Learning pe trăsături',
    'Feature-Risk A*': 'Feature-Risk A* experimental',
  };
  return algorithms.find(([id]) => id === value)?.[1] ?? backendLabels[value] ?? value;
}

function objectiveLabel(value: SafeNavigationConfig['optimization_objective']) {
  return objectiveLabels[value] ?? value;
}

function scenarioLabel(value: string) {
  const labels: Record<string, string> = {
    easy: 'ușor',
    medium: 'mediu',
    hard: 'dificil',
    custom: 'personalizat',
  };
  return labels[value] ?? value;
}

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function fixed(value: number, digits = 1) {
  return Number.isFinite(value) ? value.toFixed(digits) : '-';
}

function unsafeRate(row: MonteCarloResult['summary']['agents'][number]) {
  return row.collision_rate + row.danger_entry_rate + row.timeout_rate;
}

function buildDynamicInterpretation(monteCarlo?: MonteCarloResult) {
  const rows = monteCarlo?.summary.agents ?? [];
  if (!rows.length) {
    return {
      title: 'Interpretarea rezultatelor',
      summary: 'Rulează comparația Monte Carlo pentru a primi o concluzie adaptată la rezultate.',
      bullets: ['Dashboard-ul va evidenția succesul, riscul, eficiența și robustețea fiecărui agent.'],
    };
  }

  const bySuccess = [...rows].sort((a, b) => {
    if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
    return a.average_risk_exposure - b.average_risk_exposure;
  });
  const best = bySuccess[0];
  const worst = bySuccess[bySuccess.length - 1];
  const safest = [...rows].sort((a, b) => a.average_risk_exposure - b.average_risk_exposure)[0];
  const fastest = [...rows].sort((a, b) => a.average_steps - b.average_steps)[0];
  const bestReward = [...rows].sort((a, b) => b.average_reward - a.average_reward)[0];
  const robust = [...rows].sort((a, b) => {
    const unsafeDiff = unsafeRate(a) - unsafeRate(b);
    if (unsafeDiff !== 0) return unsafeDiff;
    return b.success_rate - a.success_rate;
  })[0];

  let title = `${algorithmLabel(best.algorithm)} conduce comparația`;
  let summary = `${algorithmLabel(best.algorithm)} are cea mai bună rată de succes (${pct(best.success_rate)}).`;

  if (best.success_rate < 0.35) {
    title = 'Niciun agent nu este robust în această configurație';
    summary = `Cel mai bun rezultat este doar ${pct(best.success_rate)} succes (${algorithmLabel(best.algorithm)}), deci scenariul este prea dificil sau bugetul de antrenare/evaluare este insuficient.`;
  } else if (best.algorithm === safest.algorithm && best.algorithm === robust.algorithm) {
    title = `${algorithmLabel(best.algorithm)} este recomandarea principală`;
    summary = `${algorithmLabel(best.algorithm)} combină cel mai bun succes cu cel mai mic risc și cele mai puține evenimente nesigure. Este cel mai echilibrat rezultat al acestei rulări.`;
  } else if (best.algorithm === safest.algorithm) {
    title = `${algorithmLabel(best.algorithm)} câștigă și la succes, și la siguranță`;
    summary = `${algorithmLabel(best.algorithm)} ajunge cel mai des la obiectiv și are cea mai mică expunere la risc. Diferența de eficiență trebuie verificată în raport cu ${algorithmLabel(fastest.algorithm)}.`;
  } else if (safest.success_rate >= best.success_rate - 0.1) {
    title = `Alegerea depinde de compromisul succes-risc`;
    summary = `${algorithmLabel(best.algorithm)} conduce la succes (${pct(best.success_rate)}), dar ${algorithmLabel(safest.algorithm)} reduce riscul cu o rată de succes apropiată (${pct(safest.success_rate)}). Pentru navigare sigură, ${algorithmLabel(safest.algorithm)} poate fi preferabil.`;
  } else if (best.success_rate - worst.success_rate > 0.4) {
    title = `${algorithmLabel(best.algorithm)} domină clar la robustețe`;
    summary = `Diferența dintre cel mai bun și cel mai slab agent este mare (${pct(best.success_rate)} vs ${pct(worst.success_rate)} succes), deci alegerea algoritmului contează semnificativ în acest scenariu.`;
  } else {
    summary = `${algorithmLabel(best.algorithm)} conduce la succes, însă ${algorithmLabel(safest.algorithm)} minimizează riscul și ${algorithmLabel(fastest.algorithm)} produce cele mai scurte trasee.`;
  }

  return {
    title,
    summary,
    bullets: [
      `Lider succes: ${algorithmLabel(best.algorithm)} (${pct(best.success_rate)} succes, risc mediu ${fixed(best.average_risk_exposure)}).`,
      `Cel mai sigur: ${algorithmLabel(safest.algorithm)} (risc mediu ${fixed(safest.average_risk_exposure)}).`,
      `Cel mai eficient: ${algorithmLabel(fastest.algorithm)} (${fixed(fastest.average_steps)} pași medii).`,
      `Cel mai bun scor/recompensă: ${algorithmLabel(bestReward.algorithm)} (${fixed(bestReward.average_reward)} recompensă medie).`,
      `Profil operațional stabil: ${algorithmLabel(robust.algorithm)} (${pct(unsafeRate(robust))} rată combinată de coliziuni/pericol/timeout).`,
    ],
  };
}

function liveEventLabel(event: MonteCarloLiveEvent) {
  if (event.type === 'map_started') {
    return `Hartă ${(event.map_index ?? 0) + 1}/${event.map_count ?? '?'} · seed ${event.map_seed ?? '-'}`;
  }
  if (event.type === 'agent_started') {
    return `Agent ${algorithmLabel(event.agent ?? '-')}`;
  }
  if (event.type === 'training_progress') {
    return `Training ${algorithmLabel(event.agent ?? 'Q')} · ${typeof event.episode === 'number' ? event.episode : '?'}/${event.total_episodes ?? '?'} ep.`;
  }
  if (event.type === 'episode_finished') {
    const episode = typeof event.episode === 'object' ? event.episode : undefined;
    return `${algorithmLabel(episode?.algorithm ?? event.agent ?? '-')} · ${episode?.success ? 'succes' : 'fără succes'} · ${episode?.steps ?? '-'} pași`;
  }
  if (event.type === 'partial_summary') return 'Dashboard live actualizat';
  if (event.type === 'job_finished') return 'Rulare finalizată';
  if (event.type === 'job_failed') return event.message ?? 'Rulare eșuată';
  return event.message ?? event.type;
}

function liveMetricRows(live: MonteCarloLiveState) {
  return [...(live.summary?.agents ?? [])].sort((a, b) => {
    if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
    return a.average_risk_exposure - b.average_risk_exposure;
  });
}

function MonteCarloLiveRun({
  live,
  fallbackEnvironment,
  showPath,
  showRisk,
  showCoordinates,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
}: {
  live: MonteCarloLiveState;
  fallbackEnvironment?: SafeEnvironment;
  showPath: boolean;
  showRisk: boolean;
  showCoordinates: boolean;
  onTogglePath: () => void;
  onToggleRisk: () => void;
  onToggleCoordinates: () => void;
}) {
  const rows = liveMetricRows(live);
  const progressPercent = Math.round(Math.min(1, Math.max(0, live.progress)) * 100);
  const currentMap = typeof live.currentMapIndex === 'number' ? live.currentMapIndex + 1 : '-';
  const currentAgent = live.currentAgent ? algorithmLabel(live.currentAgent) : '-';
  const latestEpisode = live.latestEpisode;

  return (
    <div className="mc-live-layout">
      <section className="panel-card mc-live-status">
        <div className="mc-live-status__heading">
          <div>
            <p className="eyebrow">Rulare live</p>
            <h3>Monte Carlo în desfășurare</h3>
          </div>
          <strong>{progressPercent}%</strong>
        </div>
        <div className="mc-live-progress">
          <i style={{ width: `${progressPercent}%` }} />
        </div>
        <div className="mc-live-kpis">
          <span><b>{live.completedEpisodes}</b><small>episoade terminate</small></span>
          <span><b>{live.totalEpisodes || '-'}</b><small>episoade totale</small></span>
          <span><b>{currentMap}/{live.mapCount ?? '-'}</b><small>hartă curentă</small></span>
          <span><b>{currentAgent}</b><small>agent curent</small></span>
        </div>
        <p>{live.message}</p>
      </section>

      <section className="mc-live-map">
        <GridWorldView
          environment={live.environment ?? fallbackEnvironment}
          result={latestEpisode}
          showPath={showPath}
          showRisk={showRisk}
          showCoordinates={showCoordinates}
          onTogglePath={onTogglePath}
          onToggleRisk={onToggleRisk}
          onToggleCoordinates={onToggleCoordinates}
        />
      </section>

      <section className="panel-card mc-live-table">
        <h3><Activity size={17} /> Dashboard live provizoriu</h3>
        {rows.length ? (
          <div className="comparison-table live-comparison-table">
            <div className="table-head">
              <span>Agent</span>
              <span>Ep.</span>
              <span>Succes</span>
              <span>Risc</span>
              <span>Pași</span>
            </div>
            {rows.map((row) => (
              <div className="table-row" key={row.algorithm}>
                <div className="algorithm-cell">
                  <strong>{algorithmLabel(row.algorithm)}</strong>
                  <small>{row.episodes} episoade agregate până acum</small>
                </div>
                <span>{row.episodes}</span>
                <span>{pct(row.success_rate)}</span>
                <span>{fixed(row.average_risk_exposure)}</span>
                <span>{fixed(row.average_steps)}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="muted">Dashboard-ul se populează după primele episoade finalizate.</p>
        )}
      </section>

      <section className="panel-card mc-live-events">
        <h3><CheckCircle2 size={17} /> Evenimente recente</h3>
        <div>
          {[...live.events].reverse().slice(0, 8).map((event, index) => (
            <span key={`${event.type}-${index}`}>{liveEventLabel(event)}</span>
          ))}
        </div>
      </section>
    </div>
  );
}

function stageState(stage: WizardStage, activeStage: WizardStage, scenarioReady: boolean, hasResults: boolean) {
  if (stage === activeStage) return 'active';
  if (stage === 'scenario' && scenarioReady) return 'complete';
  if (stage === 'run' && !scenarioReady) return 'locked';
  if (stage === 'run' && hasResults) return 'complete';
  if (stage === 'results' && !hasResults) return 'locked';
  return 'available';
}

function StageNavigation({
  activeStage,
  scenarioReady,
  hasResults,
  onStageChange,
}: {
  activeStage: WizardStage;
  scenarioReady: boolean;
  hasResults: boolean;
  onStageChange: (stage: WizardStage) => void;
}) {
  const steps: { id: WizardStage; label: string; description: string }[] = [
    { id: 'scenario', label: 'Configurare scenariu', description: 'Alege sau creează harta.' },
    { id: 'run', label: 'Rulare experiment', description: 'Rulează comparația Monte Carlo.' },
    { id: 'results', label: 'Rezultate', description: 'Analizează traseul și comparațiile.' },
  ];
  return (
    <aside className="stage-nav">
      <div className="stage-brand">
        <Dice5 size={24} />
        <div>
          <strong>Experiment</strong>
          <span>Flux în 3 etape</span>
        </div>
      </div>
      <nav>
        {steps.map((step, index) => {
          const state = stageState(step.id, activeStage, scenarioReady, hasResults);
          const disabled = state === 'locked';
          return (
            <button
              key={step.id}
              type="button"
              className={`stage-nav-item ${state}`}
              disabled={disabled}
              onClick={() => onStageChange(step.id)}
            >
              <span>{state === 'complete' ? <CheckCircle2 size={14} /> : index + 1}</span>
              <b>{step.label}</b>
              <small>{step.description}</small>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}

function StageNarrativePanel({
  stage,
  config,
  environment,
  result,
  monteCarlo,
}: {
  stage: WizardStage;
  config: SafeNavigationConfig;
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
}) {
  const algorithm = algorithmLabel(config.algorithm);
  const profile = getExperimentProfile(config.experiment_profile);
  const hasComparison = !!monteCarlo?.summary.agents.length;
  const interpretation = buildDynamicInterpretation(monteCarlo);

  if (stage === 'scenario') {
    return (
      <section className="panel-card stage-narrative-card">
        <h3><Lightbulb size={16} /> Povestea experimentului</h3>
        <p>Stabilim mediul și ipoteza testată: <b>{profile.label}</b>. {profile.assumption}</p>
        <div className="narrative-pills">
          <span>{profile.shortLabel}</span>
          <span>Alegem mediul</span>
          <span>Comparăm ipoteze</span>
        </div>
      </section>
    );
  }

  if (stage === 'run') {
    return (
      <section className="panel-card stage-narrative-card">
        <h3><BarChart3 size={16} /> Ipoteza de rulare</h3>
        <p>Experimentul compară strategiile pe același set de hărți generate. Profilul Monte Carlo urmărește: {profile.expectedTakeaway}</p>
        <ul>
          <li>Agenți comparați: <b>{algorithms.map(([, label]) => label).join(', ')}</b>.</li>
          <li>Hartă: <b>{environment ? `${environment.rows}x${environment.cols}` : 'negenerată'}</b>, scenariu {scenarioLabel(config.scenario)}.</li>
          <li>Obiectiv recomandare: <b>{objectiveLabel(config.optimization_objective)}</b> - {objectiveDescriptions[config.optimization_objective]}</li>
          <li>Profil: <b>{profile.shortLabel}</b> - {profile.protocol}</li>
          <li>Buget Monte Carlo: <b>{config.number_of_maps}</b> hărți × <b>{config.episodes_per_map}</b> episoade/hartă × <b>{algorithms.length}</b> agenți.</li>
          <li>Agenții Q sunt antrenați {config.training_episodes} episoade înainte de evaluarea Monte Carlo.</li>
        </ul>
      </section>
    );
  }

  return (
    <section className="panel-card stage-narrative-card results-narrative">
      <h3><Activity size={16} /> Interpretarea rezultatelor</h3>
      {monteCarlo ? (
        <p><b>{interpretation.title}.</b> {interpretation.summary}</p>
      ) : result ? (
        <p>
          {algorithm} {result.success ? 'a atins obiectivul' : result.timeout ? 'a intrat în timeout' : 'nu a finalizat cu succes'} în {result.steps} pași,
          cu risc {result.total_risk_exposure.toFixed(1)} și recompensă {result.total_reward.toFixed(1)}.
        </p>
      ) : (
        <p>Rulează comparația Monte Carlo pentru a vedea interpretarea statistică pe hărți generate.</p>
      )}
      <ul>
        {(hasComparison ? interpretation.bullets : [
          'Comparația separă eficiența de siguranță.',
          'Rezultatele sunt agregate, nu bazate pe un singur episod norocos.',
          'Monte Carlo va arăta robustețea pe hărți generate.',
        ]).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

const configQuickPrompts = [
  'Configurează un scenariu dificil, cu multe pericole, unde siguranța contează mai mult decât viteza.',
  'Vreau un demo rapid, stabil, potrivit pentru prezentare în clasă.',
  'Testează robustețea agenților când execuția mișcărilor este zgomotoasă.',
];

function NaturalLanguageConfigAssistant({
  busy,
  onDescribeConfig,
}: {
  busy: boolean;
  onDescribeConfig: (prompt: string) => Promise<LlmConfigResponse | undefined>;
}) {
  const [prompt, setPrompt] = useState(configQuickPrompts[0]);
  const [suggestion, setSuggestion] = useState<LlmConfigResponse>();

  async function submit(event?: FormEvent<HTMLFormElement>, nextPrompt = prompt) {
    event?.preventDefault();
    const cleanPrompt = nextPrompt.trim();
    if (!cleanPrompt || busy) return;
    setSuggestion(undefined);
    const response = await onDescribeConfig(cleanPrompt);
    if (response) setSuggestion(response);
  }

  return (
    <section className="panel-card nl-config-card">
      <div className="nl-config-card__heading">
        <div>
          <p className="eyebrow"><Bot size={14} /> Asistent configurare AI</p>
          <h3>Descrie experimentul în limbaj natural</h3>
        </div>
      </div>
      <p>
        LLM-ul propune valori pentru formular, iar backend-ul le validează strict înainte să fie aplicate.
      </p>
      <div className="nl-config-card__prompts">
        {configQuickPrompts.map((item) => (
          <button
            type="button"
            key={item}
            disabled={busy}
            onClick={() => {
              setPrompt(item);
              void submit(undefined, item);
            }}
          >
            {item}
          </button>
        ))}
      </div>
      <form className="nl-config-card__form" onSubmit={(event) => submit(event)}>
        <textarea
          value={prompt}
          disabled={busy}
          rows={4}
          onChange={(event) => setPrompt(event.target.value)}
        />
        <button type="submit" className="primary-button" disabled={busy || !prompt.trim()}>
          {busy ? <Loader2 size={15} className="mc-spin" /> : <Send size={15} />} Aplică propunerea
        </button>
      </form>
      {suggestion ? (
        <div className="nl-config-card__result">
          <strong>{suggestion.fallback ? 'Fallback controlat' : 'Configurație aplicată'}</strong>
          <p>{suggestion.rationale}</p>
          {suggestion.applied_fields.length ? (
            <small>Câmpuri modificate: {suggestion.applied_fields.join(', ')}</small>
          ) : null}
          {suggestion.warnings.length ? (
            <ul>{suggestion.warnings.map((warning) => <li key={warning}>{warning}</li>)}</ul>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

function ScenarioStage({
  config,
  scenarioPresets,
  environment,
  busy,
  pendingMapConfig,
  showPath,
  showRisk,
  showCoordinates,
  onChange,
  onDescribeConfig,
  onPreview,
  onContinue,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
}: Pick<Props, 'config' | 'scenarioPresets' | 'environment' | 'busy' | 'pendingMapConfig' | 'showPath' | 'showRisk' | 'showCoordinates' | 'onChange' | 'onDescribeConfig' | 'onPreview' | 'onTogglePath' | 'onToggleRisk' | 'onToggleCoordinates'> & {
  onContinue: () => void;
}) {
  const [dialogOpen, setDialogOpen] = useState(false);
  const activeScenario = scenarioConfig(config, scenarioPresets);

  const changeScenario = (scenario: string) => {
    const preset = presetFor(scenario, scenarioPresets);
    onChange({
      ...config,
      scenario,
      ...(preset
        ? {
            rows: preset.rows,
            cols: preset.cols,
            wall_probability: preset.wall_probability,
            danger_probability: preset.danger_probability,
          }
        : {}),
    });
  };

  const generateRandomMap = () => onPreview({ ...config, random_seed: createRandomSeed() });

  return (
    <section className="wizard-stage scenario-stage">
      <div className="stage-heading">
        <div>
          <p className="eyebrow">1. Configurare scenariu</p>
          <h2>Alege harta pe care vor naviga agenții</h2>
          <p>Generează o hartă reproductibilă pe seed-ul curent sau creează rapid o variantă aleatoare.</p>
        </div>
      </div>

      <div className="scenario-stage-grid">
        <div className="scenario-left-stack">
          <NaturalLanguageConfigAssistant
            busy={busy}
            onDescribeConfig={onDescribeConfig}
          />
          <section className="panel-card preset-list-card">
            <h3>Scenarii presetate</h3>
            <div className="scenario-options">
              {scenarios.map(([id, label, description]) => {
                const preset = presetFor(id, scenarioPresets);
                const isActive = config.scenario === id;
                return (
                  <button
                    type="button"
                    key={id}
                    className={isActive ? 'scenario-option active' : 'scenario-option'}
                    onClick={() => changeScenario(id)}
                  >
                    <strong>{label}</strong>
                    <span>{description}</span>
                    <small>
                      {id === 'custom' || !preset
                        ? `${config.rows}x${config.cols} · configurabil`
                        : `${preset.rows}x${preset.cols} · pereți ${fmtProbability(preset.wall_probability)} · pericole ${fmtProbability(preset.danger_probability)}`}
                    </small>
                  </button>
                );
              })}
            </div>
          </section>
        </div>

        <section className="scenario-preview-stack">
          <div className="scenario-info-row">
            <div className="panel-card scenario-context-card">
              <h3>Rezumat scenariu</h3>
              <div className="scenario-summary wide">
                <span><CheckCircle2 size={14} /> {activeScenario.rows}x{activeScenario.cols}</span>
                <span>Pereți {fmtProbability(activeScenario.wall_probability)}</span>
                <span>Pericole {fmtProbability(activeScenario.danger_probability)}</span>
                <span>Seed {config.random_seed}</span>
              </div>
              <div className="active-profile-note">
                <b>{getExperimentProfile(config.experiment_profile).label}</b>
                <span>{getExperimentProfile(config.experiment_profile).expectedTakeaway}</span>
              </div>
              {pendingMapConfig ? (
                <p className="pending-note">Configurația s-a schimbat. Generează harta pentru a aplica noile setări.</p>
              ) : null}
            </div>
            <StageNarrativePanel stage="scenario" config={config} environment={environment} />
          </div>

          <GridWorldView
            environment={environment}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            onTogglePath={onTogglePath}
            onToggleRisk={onToggleRisk}
            onToggleCoordinates={onToggleCoordinates}
          />
        </section>
      </div>

      <div className="stage-actions">
        <button type="button" className="secondary-button" onClick={() => setDialogOpen(true)}>
          <Settings2 size={16} /> {config.scenario === 'custom' ? 'Configurează scenariul' : 'Setări experiment'}
        </button>
        <button className="secondary-button" disabled={busy} onClick={() => onPreview()}>
          <RefreshCw size={16} /> Generează hartă
        </button>
        <button className="secondary-button" disabled={busy} onClick={generateRandomMap}>
          <Shuffle size={16} /> Hartă aleatoare
        </button>
        <button className="primary-button" disabled={!environment || pendingMapConfig || busy} onClick={onContinue}>
          Continuă <ArrowRight size={16} />
        </button>
      </div>

      <ScenarioConfigDialog
        open={dialogOpen}
        busy={busy}
        config={config}
        scenarioPresets={scenarioPresets}
        onClose={() => setDialogOpen(false)}
        onApply={onChange}
        onGenerate={onPreview}
      />
    </section>
  );
}

function MonteCarloConfirmDialog({
  open,
  config,
  environment,
  totalEpisodes,
  estimatedTrainingEpisodes,
  busy,
  onClose,
  onConfirm,
}: {
  open: boolean;
  config: SafeNavigationConfig;
  environment?: SafeEnvironment;
  totalEpisodes: number;
  estimatedTrainingEpisodes: number;
  busy: boolean;
  onClose: () => void;
  onConfirm: () => void;
}) {
  if (!open) return null;

  const profile = getExperimentProfile(config.experiment_profile);
  const mapSize = environment ? `${environment.rows}×${environment.cols}` : `${config.rows}×${config.cols}`;
  const rows = [
    ['Profil', profile.label],
    ['Scenariu', scenarioLabel(config.scenario)],
    ['Hartă', `${mapSize}, seed ${config.random_seed}`],
    ['Pereți / pericole', `${fmtProbability(config.wall_probability)} / ${fmtProbability(config.danger_probability)}`],
    ['Zgomot mișcare', String(config.movement_noise)],
    ['Pondere risc', String(config.risk_weight)],
    ['Algoritmi', `${algorithms.length} strategii: ${algorithms.map(([, label]) => label).join(', ')}`],
    ['Obiectiv recomandare', objectiveLabel(config.optimization_objective)],
    ['Număr rulări/hărți MC', String(config.number_of_maps)],
    ['Episoade per hartă', String(config.episodes_per_map)],
    ['Total episoade evaluate', String(totalEpisodes)],
    ['Episoade antrenare Q', `${config.training_episodes} per agent/hartă`],
    ['Antrenare Q estimată', `${estimatedTrainingEpisodes} episoade`],
    ['Pași maximi / episod', String(config.max_steps)],
  ];

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="scenario-dialog mc-confirm-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="mc-confirm-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="dialog-header">
          <div>
            <p className="eyebrow">Confirmare rulare</p>
            <h2 id="mc-confirm-title"><BarChart3 size={18} /> Rulează Monte Carlo cu acești parametri?</h2>
          </div>
          <button type="button" className="icon-button" aria-label="Închide dialogul" onClick={onClose}>
            <X size={18} />
          </button>
        </header>

        <div className="dialog-section">
          <h3>Rezumatul experimentului</h3>
          <p>
            Vor fi evaluate {totalEpisodes} episoade, iar agenții Q vor fi antrenați înainte de evaluare.
            Dacă vrei alt buget statistic, modifică numărul de rulări/hărți sau episoadele per hartă înainte de confirmare.
          </p>
        </div>

        <div className="mc-confirm-grid">
          {rows.map(([label, value]) => (
            <div key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>

        <footer className="dialog-actions">
          <button type="button" className="ghost-button" onClick={onClose}>Anulează</button>
          <button type="button" className="primary-button" disabled={busy} onClick={onConfirm}>
            <Play size={16} /> Confirmă și rulează
          </button>
        </footer>
      </section>
    </div>
  );
}

function RunStage({
  config,
  environment,
  liveMonteCarlo,
  busy,
  pendingMapConfig,
  showPath,
  showRisk,
  showCoordinates,
  onChange,
  onMonteCarlo,
  onBack,
  onResults,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
  hasResults,
}: Pick<Props, 'config' | 'environment' | 'liveMonteCarlo' | 'busy' | 'pendingMapConfig' | 'showPath' | 'showRisk' | 'showCoordinates' | 'onChange' | 'onMonteCarlo' | 'onTogglePath' | 'onToggleRisk' | 'onToggleCoordinates'> & {
  onBack: () => void;
  onResults: () => void;
  hasResults: boolean;
}) {
  const [confirmOpen, setConfirmOpen] = useState(false);
  const patch = (next: Partial<SafeNavigationConfig>) => onChange({ ...config, ...next });
  const canRun = !!environment && !pendingMapConfig && !busy;
  const totalEpisodes = algorithms.length * config.number_of_maps * config.episodes_per_map;
  const qTrainingAgents = algorithms.filter(([id]) => learningAlgorithms.has(id)).length;
  const estimatedTrainingEpisodes = qTrainingAgents * config.number_of_maps * config.training_episodes;

  if (liveMonteCarlo && busy) {
    return (
      <section className="wizard-stage run-stage">
        <div className="stage-heading">
          <div>
            <p className="eyebrow">2. Rulare experiment</p>
            <h2>Urmărește rularea Monte Carlo live</h2>
            <p>Dashboard-ul provizoriu se actualizează pe măsură ce se termină episoadele; rezultatul final apare automat la sfârșit.</p>
          </div>
        </div>
        <MonteCarloLiveRun
          live={liveMonteCarlo}
          fallbackEnvironment={environment}
          showPath={showPath}
          showRisk={showRisk}
          showCoordinates={showCoordinates}
          onTogglePath={onTogglePath}
          onToggleRisk={onToggleRisk}
          onToggleCoordinates={onToggleCoordinates}
        />
        <div className="stage-actions">
          <button className="secondary-button" disabled><ArrowLeft size={16} /> Rularea este activă</button>
          <button className="primary-button" disabled><RefreshCw size={16} /> Se actualizează live...</button>
        </div>
      </section>
    );
  }

  return (
    <section className="wizard-stage run-stage">
      <div className="stage-heading">
        <div>
          <p className="eyebrow">2. Rulare experiment</p>
          <h2>Rulează comparația Monte Carlo</h2>
          <p>Etapa folosește harta și profilul alese anterior, apoi compară toate strategiile pe hărți generate.</p>
        </div>
      </div>

      <div className="run-stage-grid">
        <section className="panel-card run-config-card">
          <h3><BarChart3 size={17} /> Experiment Monte Carlo</h3>
          <div className="run-param-grid">
            <label>
              <TooltipLabel text="Limita maximă de pași pentru fiecare episod evaluat. Dacă agentul nu termină, episodul devine timeout.">
                Pași maximi / episod
              </TooltipLabel>
              <input type="number" min={1} max={5000} value={config.max_steps} onChange={(event) => patch({ max_steps: Number(event.target.value) })} />
            </label>
            <label>
              <TooltipLabel text="Câte hărți generate procedural intră în comparația Monte Carlo.">
                Număr rulări/hărți MC
              </TooltipLabel>
              <input type="number" min={1} max={100} value={config.number_of_maps} onChange={(event) => patch({ number_of_maps: Number(event.target.value) })} />
            </label>
            <label>
              <TooltipLabel text="De câte ori este evaluat fiecare agent pe fiecare hartă.">
                Episoade per hartă
              </TooltipLabel>
              <input type="number" min={1} max={100} value={config.episodes_per_map} onChange={(event) => patch({ episodes_per_map: Number(event.target.value) })} />
            </label>
            <label>
              <TooltipLabel text="Criteriul după care motorul de recomandare transformă metricile Monte Carlo într-un scor final.">
                Obiectiv recomandare
              </TooltipLabel>
              <select
                value={config.optimization_objective}
                onChange={(event) => patch({ optimization_objective: event.target.value as SafeNavigationConfig['optimization_objective'] })}
              >
                {(Object.keys(objectiveLabels) as SafeNavigationConfig['optimization_objective'][]).map((id) => (
                  <option key={id} value={id}>{objectiveLabels[id]}</option>
                ))}
              </select>
            </label>
            <label>
              <TooltipLabel text="Numărul de episoade de antrenare pentru agenții Q-Learning înainte de evaluarea Monte Carlo.">
                Episoade antrenare agenți learning
              </TooltipLabel>
              <input type="number" min={0} max={10000} value={config.training_episodes} onChange={(event) => patch({ training_episodes: Number(event.target.value) })} />
            </label>
          </div>
          <div className="run-summary-list">
            <span>Algoritmi: <b>{algorithms.length} strategii comparate</b></span>
            <span>Obiectiv: <b>{objectiveLabel(config.optimization_objective)}</b></span>
            <span>Profil: <b>{getExperimentProfile(config.experiment_profile).shortLabel}</b></span>
            <span>Evaluări totale: <b>{totalEpisodes} episoade</b></span>
            <span>Antrenare Q estimată: <b>{estimatedTrainingEpisodes} episoade</b></span>
            <span>Seed hartă: <b>{config.random_seed}</b></span>
            <span>Status hartă: <b>{pendingMapConfig ? 'neaplicată' : environment ? 'generată' : 'lipsă'}</b></span>
          </div>
          <StageNarrativePanel stage="run" config={config} environment={environment} />
          {pendingMapConfig ? (
            <p className="pending-note">Ai modificat configurația hărții. Revino la etapa 1 și generează harta înainte de rulare.</p>
          ) : null}
        </section>

        <section className="run-map-preview">
          <GridWorldView
            environment={environment}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            onTogglePath={onTogglePath}
            onToggleRisk={onToggleRisk}
            onToggleCoordinates={onToggleCoordinates}
          />
        </section>
      </div>

      <div className="stage-actions">
        <button className="secondary-button" onClick={onBack}><ArrowLeft size={16} /> Înapoi</button>
        <button className="primary-button" disabled={!canRun} onClick={() => setConfirmOpen(true)}><Play size={16} /> Rulează Monte Carlo</button>
        <button className="secondary-button" disabled={!hasResults} onClick={onResults}>Continuă la rezultate <ArrowRight size={16} /></button>
      </div>

      <MonteCarloConfirmDialog
        open={confirmOpen}
        config={config}
        environment={environment}
        totalEpisodes={totalEpisodes}
        estimatedTrainingEpisodes={estimatedTrainingEpisodes}
        busy={busy}
        onClose={() => setConfirmOpen(false)}
        onConfirm={() => {
          setConfirmOpen(false);
          onMonteCarlo();
        }}
      />
    </section>
  );
}

function ResultsStage({
  config,
  environment,
  result,
  monteCarlo,
  busy,
  busyAction,
  onChange,
  onBack,
  onScenario,
  onMonteCarlo,
}: Pick<Props, 'config' | 'environment' | 'result' | 'monteCarlo' | 'busy' | 'busyAction' | 'onChange' | 'onMonteCarlo'> & {
  onBack: () => void;
  onScenario: () => void;
}) {
  const [tab, setTab] = useState(monteCarloTabs[0].id);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const isMonteCarloBusy = busyAction === 'monte-carlo';

  return (
    <section className="wizard-stage results-stage">
      <div className="stage-heading">
        <div>
          <p className="eyebrow">3. Rezultate</p>
          <h2>Rezultatele comparației Monte Carlo</h2>
          <p>Analiza este agregată pe agenți, hărți și episoade; nu mai interpretăm un singur traseu izolat.</p>
        </div>
      </div>

      {monteCarlo || isMonteCarloBusy ? (
        <div className="mc-results-stage">
          <div className="mc-results-stage__overview">
            {monteCarlo ? (
              <AiAnalystPanel result={monteCarlo} autoTrigger />
            ) : (
              <StageNarrativePanel
                stage="results"
                config={config}
                environment={environment}
                result={result}
                monteCarlo={monteCarlo}
              />
            )}
            <ExperimentDashboard
              result={monteCarlo}
              busy={isMonteCarloBusy}
              selectedObjective={config.optimization_objective}
              onObjectiveChange={(objective) => onChange({ ...config, optimization_objective: objective })}
            />
          </div>

          {monteCarlo ? (
            <section className="mc-details-panel">
              <button
                type="button"
                className="mc-details-toggle"
                onClick={() => setDetailsOpen((value) => !value)}
                aria-expanded={detailsOpen}
              >
                <span>
                  <strong>More details</strong>
                  <small>Distribuții, intervale 95%, risc/recompensă și grafice suplimentare</small>
                </span>
                {detailsOpen ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
              </button>

              {detailsOpen ? (
                <Tabs.Root value={tab} onValueChange={setTab} className="mc-results-tabs">
                  <Tabs.List className="mc-page__tabs">
                    {monteCarloTabs.map((entry) => (
                      <Tabs.Trigger key={entry.id} value={entry.id} className="mc-tab">
                        <TooltipLabel text={entry.tooltip}>{entry.label}</TooltipLabel>
                      </Tabs.Trigger>
                    ))}
                  </Tabs.List>
                  <div className="mc-results-stage__content">
                    <Tabs.Content value="distributions"><RewardDistribution result={monteCarlo} /></Tabs.Content>
                    <Tabs.Content value="ci-bars"><MetricCIBars result={monteCarlo} /></Tabs.Content>
                    <Tabs.Content value="pareto"><RiskRewardScatter result={monteCarlo} /></Tabs.Content>
                    <Tabs.Content value="per-map"><PerMapHeatmap result={monteCarlo} /></Tabs.Content>
                    <Tabs.Content value="failures"><FailureBreakdown result={monteCarlo} /></Tabs.Content>
                    <Tabs.Content value="occupancy"><OccupancyHeatmap result={monteCarlo} /></Tabs.Content>
                    <Tabs.Content value="export"><ExportPanel result={monteCarlo} /></Tabs.Content>
                  </div>
                </Tabs.Root>
              ) : null}
            </section>
          ) : null}
        </div>
      ) : (
        <section className="panel-card mc-results-empty">
          <h3><BarChart3 size={17} /> Nu există încă o comparație Monte Carlo</h3>
          <p>Revino la etapa de rulare și pornește experimentul pentru a vedea dashboard-ul statistic.</p>
        </section>
      )}

      <div className="stage-actions">
        <button className="secondary-button" onClick={onBack}><ArrowLeft size={16} /> Înapoi la rulare</button>
        <button className="secondary-button" onClick={onScenario}>Schimbă scenariul</button>
        <button className="primary-button" disabled={!environment || busy} onClick={onMonteCarlo}><Play size={16} /> Rulează Monte Carlo din nou</button>
      </div>
    </section>
  );
}

export function ControlPanel({
  activeStage,
  config,
  scenarioPresets,
  environment,
  result,
  monteCarlo,
  liveMonteCarlo,
  busy,
  busyAction,
  pendingMapConfig,
  showPath,
  showRisk,
  showCoordinates,
  onStageChange,
  onChange,
  onDescribeConfig,
  onPreview,
  onMonteCarlo,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
}: Props) {
  const scenarioReady = !!environment && !pendingMapConfig;
  const hasResults = !!result || !!monteCarlo;

  return (
    <div className="wizard-workspace">
      <StageNavigation
        activeStage={activeStage}
        scenarioReady={scenarioReady}
        hasResults={hasResults}
        onStageChange={onStageChange}
      />
      <main className="wizard-content">
        {activeStage === 'scenario' ? (
          <ScenarioStage
            config={config}
            scenarioPresets={scenarioPresets}
            environment={environment}
            busy={busy}
            pendingMapConfig={pendingMapConfig}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            onChange={onChange}
            onDescribeConfig={onDescribeConfig}
            onPreview={onPreview}
            onContinue={() => onStageChange('run')}
            onTogglePath={onTogglePath}
            onToggleRisk={onToggleRisk}
            onToggleCoordinates={onToggleCoordinates}
          />
        ) : null}
        {activeStage === 'run' ? (
          <RunStage
            config={config}
            environment={environment}
            liveMonteCarlo={liveMonteCarlo}
            busy={busy}
            pendingMapConfig={pendingMapConfig}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            hasResults={hasResults}
            onChange={onChange}
            onMonteCarlo={onMonteCarlo}
            onBack={() => onStageChange('scenario')}
            onResults={() => onStageChange('results')}
            onTogglePath={onTogglePath}
            onToggleRisk={onToggleRisk}
            onToggleCoordinates={onToggleCoordinates}
          />
        ) : null}
        {activeStage === 'results' ? (
          <ResultsStage
            config={config}
            environment={environment}
            result={result}
            monteCarlo={monteCarlo}
            busy={busy}
            busyAction={busyAction}
            onChange={onChange}
            onBack={() => onStageChange('run')}
            onScenario={() => onStageChange('scenario')}
            onMonteCarlo={onMonteCarlo}
          />
        ) : null}
      </main>
    </div>
  );
}
