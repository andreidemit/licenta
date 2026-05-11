import { useState } from 'react';
import {
  Activity,
  ArrowLeft,
  ArrowRight,
  BarChart3,
  Bot,
  CheckCircle2,
  Dice5,
  GraduationCap,
  Lightbulb,
  Play,
  RefreshCw,
  Settings2,
  Shuffle,
} from 'lucide-react';
import { ExperimentDashboard } from './ExperimentDashboard';
import { ExplanationPanel } from './ExplanationPanel';
import { GridWorldView } from './GridWorldView';
import { MetricsPanel } from './MetricsPanel';
import { ScenarioConfigDialog } from './ScenarioConfigDialog';
import type {
  MonteCarloResult,
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
  ['sarsa', 'SARSA tabular'],
];

const scenarios = [
  ['easy', 'Ușor', 'Hartă mică, puține obstacole și risc redus.'],
  ['medium', 'Mediu', 'Echilibru între obstacole, pericole și spațiu de navigare.'],
  ['hard', 'Dificil', 'Hartă mare, densitate ridicată și expunere mai mare la risc.'],
  ['custom', 'Personalizat', 'Configurează dimensiunea, densitățile și seed-ul.'],
];

const learningAlgorithms = new Set(['tabular_q', 'feature_q', 'sarsa']);

export type WizardStage = 'scenario' | 'run' | 'results';

type Props = {
  activeStage: WizardStage;
  config: SafeNavigationConfig;
  scenarioPresets: SafeScenarioPreset[];
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
  explanation: string;
  busy: boolean;
  busyAction?: 'map' | 'episode' | 'monte-carlo';
  pendingMapConfig: boolean;
  showPath: boolean;
  showRisk: boolean;
  showCoordinates: boolean;
  onStageChange: (stage: WizardStage) => void;
  onChange: (config: SafeNavigationConfig) => void;
  onPreview: (config?: SafeNavigationConfig) => void;
  onEpisode: () => void;
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
  };
  return algorithms.find(([id]) => id === value)?.[1] ?? backendLabels[value] ?? value;
}

function algorithmNarrative(value: string) {
  const notes: Record<string, string> = {
    random: 'Baseline-ul aleator arată cât de dificil este mediul fără planificare sau învățare.',
    rule_based: 'Agentul pe reguli testează dacă reguli locale simple pot evita riscul imediat.',
    astar: 'A* verifică eficiența planificării pe hărți noi, optimizând în principal distanța.',
    risk_aware_astar: 'A* conștient de risc testează compromisul dintre traseu mai lung și expunere mai mică.',
    tabular_q: 'Q-Learning tabular testează cât de bine se învață o hartă fixă prin coordonate absolute.',
    feature_q: 'Q-Learning pe trăsături testează transferul unor tipare locale pe hărți noi.',
  };
  return notes[value] ?? 'Strategia selectată va fi evaluată pe aceeași hartă și aceleași metrici.';
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
    { id: 'run', label: 'Rulare experiment', description: 'Alege agentul și pornește simularea.' },
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
  const hasComparison = !!monteCarlo?.summary.agents.length;
  const bestComparison = hasComparison
    ? [...monteCarlo.summary.agents].sort((a, b) => {
        if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
        return a.average_risk_exposure - b.average_risk_exposure;
      })[0]
    : undefined;

  if (stage === 'scenario') {
    return (
      <section className="panel-card stage-narrative-card">
        <h3><Lightbulb size={16} /> Povestea experimentului</h3>
        <p>Stabilim mediul necunoscut și dificultatea: grilă, obstacole, pericole și seed reproductibil.</p>
        <div className="narrative-pills">
          <span>Alegem mediul</span>
          <span>Rulăm strategia</span>
          <span>Comparăm robustețea</span>
        </div>
      </section>
    );
  }

  if (stage === 'run') {
    return (
      <section className="panel-card stage-narrative-card">
        <h3><GraduationCap size={16} /> Ipoteza de rulare</h3>
        <p>{algorithmNarrative(config.algorithm)}</p>
        <ul>
          <li>Agent curent: <b>{algorithm}</b>.</li>
          <li>Hartă: <b>{environment ? `${environment.rows}x${environment.cols}` : 'negenerată'}</b>, scenariu {scenarioLabel(config.scenario)}.</li>
          <li>{learningAlgorithms.has(config.algorithm) ? `Se antrenează ${config.training_episodes} episoade înainte de test.` : 'Se rulează direct, fără fază de antrenare.'}</li>
        </ul>
      </section>
    );
  }

  return (
    <section className="panel-card stage-narrative-card results-narrative">
      <h3><Activity size={16} /> Interpretarea rezultatelor</h3>
      {result ? (
        <p>
          {algorithm} {result.success ? 'a atins obiectivul' : result.timeout ? 'a intrat în timeout' : 'nu a finalizat cu succes'} în {result.steps} pași,
          cu risc {result.total_risk_exposure.toFixed(1)} și recompensă {result.total_reward.toFixed(1)}.
        </p>
      ) : (
        <p>Rulează un episod pentru a vedea traseul și explicația metricilor pe harta curentă.</p>
      )}
      <ul>
        <li>Traseul arată decizia pas cu pas.</li>
        <li>Metricile separă eficiența de siguranță.</li>
        <li>
          {bestComparison
            ? `Monte Carlo indică momentan ${algorithmLabel(bestComparison.algorithm)} ca lider la succes.`
            : 'Monte Carlo va arăta robustețea pe hărți generate.'}
        </li>
      </ul>
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
  onPreview,
  onContinue,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
}: Pick<Props, 'config' | 'scenarioPresets' | 'environment' | 'busy' | 'pendingMapConfig' | 'showPath' | 'showRisk' | 'showCoordinates' | 'onChange' | 'onPreview' | 'onTogglePath' | 'onToggleRisk' | 'onToggleCoordinates'> & {
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

function RunStage({
  config,
  environment,
  busy,
  pendingMapConfig,
  showPath,
  showRisk,
  showCoordinates,
  onChange,
  onEpisode,
  onMonteCarlo,
  onBack,
  onResults,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
  hasResults,
}: Pick<Props, 'config' | 'environment' | 'busy' | 'pendingMapConfig' | 'showPath' | 'showRisk' | 'showCoordinates' | 'onChange' | 'onEpisode' | 'onMonteCarlo' | 'onTogglePath' | 'onToggleRisk' | 'onToggleCoordinates'> & {
  onBack: () => void;
  onResults: () => void;
  hasResults: boolean;
}) {
  const isLearningAgent = learningAlgorithms.has(config.algorithm);
  const patch = (next: Partial<SafeNavigationConfig>) => onChange({ ...config, ...next });
  const canRun = !!environment && !pendingMapConfig && !busy;

  return (
    <section className="wizard-stage run-stage">
      <div className="stage-heading">
        <div>
          <p className="eyebrow">2. Rulare experiment</p>
          <h2>Configurează agentul și pornește simularea</h2>
          <p>Etapa folosește harta generată în pasul anterior. Schimbările de scenariu trebuie aplicate înainte de rulare.</p>
        </div>
      </div>

      <div className="run-stage-grid">
        <section className="panel-card run-config-card">
          <h3><Bot size={17} /> Strategie agent</h3>
          <label>
            Alege algoritmul
            <select value={config.algorithm} onChange={(event) => patch({ algorithm: event.target.value })}>
              {algorithms.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
            </select>
          </label>
          <div className="run-param-grid">
            <label>Pași maximi<input type="number" value={config.max_steps} onChange={(event) => patch({ max_steps: Number(event.target.value) })} /></label>
            {isLearningAgent ? (
              <label>Episoade antrenare<input type="number" value={config.training_episodes} onChange={(event) => patch({ training_episodes: Number(event.target.value) })} /></label>
            ) : (
              <div className="run-info-box">
                <GraduationCap size={16} />
                <span>Acest agent este evaluat direct, fără antrenare.</span>
              </div>
            )}
          </div>
          <div className="run-summary-list">
            <span>Algoritm: <b>{algorithmLabel(config.algorithm)}</b></span>
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
        <button className="primary-button" disabled={!canRun} onClick={onEpisode}><Play size={16} /> Rulează episod</button>
        <button className="secondary-button" disabled={!canRun} onClick={onMonteCarlo}><BarChart3 size={16} /> Compară Monte Carlo</button>
        <button className="secondary-button" disabled={!hasResults} onClick={onResults}>Continuă la rezultate <ArrowRight size={16} /></button>
      </div>
    </section>
  );
}

function ResultsStage({
  config,
  environment,
  result,
  monteCarlo,
  explanation,
  busy,
  busyAction,
  showPath,
  showRisk,
  showCoordinates,
  onBack,
  onScenario,
  onEpisode,
  onTogglePath,
  onToggleRisk,
  onToggleCoordinates,
}: Pick<Props, 'config' | 'environment' | 'result' | 'monteCarlo' | 'explanation' | 'busy' | 'busyAction' | 'showPath' | 'showRisk' | 'showCoordinates' | 'onEpisode' | 'onTogglePath' | 'onToggleRisk' | 'onToggleCoordinates'> & {
  onBack: () => void;
  onScenario: () => void;
}) {
  return (
    <section className="wizard-stage results-stage">
      <div className="stage-heading">
        <div>
          <p className="eyebrow">3. Rezultate</p>
          <h2>Analizează traseul, metricile și comparațiile</h2>
          <p>Rezultatele combină traseul vizual, metricile episodului și comparația Monte Carlo dacă a fost rulată.</p>
        </div>
      </div>

      <div className="results-stage-grid">
        <div className="results-main">
          <GridWorldView
            environment={environment}
            result={result}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            onTogglePath={onTogglePath}
            onToggleRisk={onToggleRisk}
            onToggleCoordinates={onToggleCoordinates}
          />
          <ExperimentDashboard result={monteCarlo} busy={busyAction === 'monte-carlo'} />
        </div>
        <div className="results-side">
          <StageNarrativePanel
            stage="results"
            config={config}
            environment={environment}
            result={result}
            monteCarlo={monteCarlo}
          />
          <MetricsPanel config={config} environment={environment} result={result} monteCarlo={monteCarlo} compact showStory={false} />
          <ExplanationPanel
            config={config}
            environment={environment}
            result={result}
            monteCarlo={monteCarlo}
            text={explanation}
            compact
          />
        </div>
      </div>

      <div className="stage-actions">
        <button className="secondary-button" onClick={onBack}><ArrowLeft size={16} /> Înapoi la rulare</button>
        <button className="secondary-button" onClick={onScenario}>Schimbă scenariul</button>
        <button className="primary-button" disabled={!environment || busy} onClick={onEpisode}><Play size={16} /> Rulează din nou</button>
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
  explanation,
  busy,
  busyAction,
  pendingMapConfig,
  showPath,
  showRisk,
  showCoordinates,
  onStageChange,
  onChange,
  onPreview,
  onEpisode,
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
            busy={busy}
            pendingMapConfig={pendingMapConfig}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            hasResults={hasResults}
            onChange={onChange}
            onEpisode={onEpisode}
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
            explanation={explanation}
            busy={busy}
            busyAction={busyAction}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            onBack={() => onStageChange('run')}
            onScenario={() => onStageChange('scenario')}
            onEpisode={onEpisode}
            onTogglePath={onTogglePath}
            onToggleRisk={onToggleRisk}
            onToggleCoordinates={onToggleCoordinates}
          />
        ) : null}
      </main>
    </div>
  );
}
