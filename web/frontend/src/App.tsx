import { useCallback, useEffect, useRef, useState } from 'react';
import { Server, ShieldAlert, ShieldCheck } from 'lucide-react';
import './styles.css';
import { safeNavigationApi } from './features/safe-navigation/api';
import { ControlPanel, type WizardStage } from './features/safe-navigation/ControlPanel';
import { setLatestMonteCarlo } from './features/safe-navigation/monteCarloStore';
import type {
  MonteCarloResult,
  MonteCarloJobSnapshot,
  MonteCarloLiveEvent,
  MonteCarloLiveState,
  SafeEnvironment,
  SafeEpisodeResult,
  SafeNavigationConfig,
  SafeScenarioPreset,
} from './features/safe-navigation/types';

const initialConfig: SafeNavigationConfig = {
  algorithm: 'risk_aware_astar',
  optimization_objective: 'balanced',
  experiment_profile: 'known_static',
  scenario: 'medium',
  rows: 15,
  cols: 15,
  wall_probability: 0.2,
  danger_probability: 0.1,
  movement_noise: 0,
  risk_weight: 1,
  max_steps: 300,
  training_episodes: 150,
  number_of_maps: 6,
  episodes_per_map: 2,
  random_seed: 42,
};

type BusyAction = 'map' | 'episode' | 'monte-carlo';

const monteCarloAlgorithms = [
  'random',
  'rule_based',
  'astar',
  'risk_aware_astar',
  'tabular_q',
  'feature_q',
  'feature_risk_astar',
];

function liveStateFromJob(job: MonteCarloJobSnapshot): MonteCarloLiveState {
  return {
    jobId: job.id,
    status: job.status,
    message: job.message,
    progress: job.progress,
    totalEpisodes: 0,
    completedEpisodes: 0,
    summary: job.result?.summary,
    events: job.latest_event ? [job.latest_event] : [],
  };
}

function updateLiveState(
  current: MonteCarloLiveState | undefined,
  event: MonteCarloLiveEvent,
): MonteCarloLiveState | undefined {
  if (!current) return current;
  const progressPayload = typeof event.progress === 'object' ? event.progress : undefined;
  const snapshotProgress = typeof event.progress === 'number' ? event.progress : undefined;
  const episode = typeof event.episode === 'object' ? event.episode : undefined;
  const nextEvents = event.type === 'job_status'
    ? current.events
    : [...current.events, event].slice(-40);
  return {
    ...current,
    status: event.status ?? current.status,
    message: event.message ?? current.message,
    progress: event.type === 'job_finished'
      ? 1
      : typeof progressPayload?.total === 'number' && progressPayload.total > 0
        ? progressPayload.completed / progressPayload.total
        : snapshotProgress ?? current.progress,
    totalEpisodes: event.totals?.evaluation_episodes ?? progressPayload?.total ?? current.totalEpisodes,
    completedEpisodes: progressPayload?.completed ?? current.completedEpisodes,
    currentAgent: event.agent ?? progressPayload?.agent ?? current.currentAgent,
    currentMapIndex: event.map_index ?? progressPayload?.map_index ?? current.currentMapIndex,
    mapCount: event.map_count ?? progressPayload?.map_count ?? current.mapCount,
    mapSeed: event.map_seed ?? progressPayload?.map_seed ?? current.mapSeed,
    environment: event.environment ?? current.environment,
    latestEpisode: episode ?? current.latestEpisode,
    summary: event.summary ?? event.result?.summary ?? current.summary,
    events: nextEvents,
  };
}

export function App() {
  const [config, setConfig] = useState(initialConfig);
  const [environment, setEnvironment] = useState<SafeEnvironment>();
  const [episodeResult, setEpisodeResult] = useState<SafeEpisodeResult>();
  const [monteCarlo, setMonteCarlo] = useState<MonteCarloResult>();
  const [liveMonteCarlo, setLiveMonteCarlo] = useState<MonteCarloLiveState>();
  const [scenarioPresets, setScenarioPresets] = useState<SafeScenarioPreset[]>([]);
  const [explanation, setExplanation] = useState('');
  const [busy, setBusy] = useState(false);
  const [busyAction, setBusyAction] = useState<BusyAction>();
  const [activeStage, setActiveStage] = useState<WizardStage>('scenario');
  const [pendingMapConfig, setPendingMapConfig] = useState(false);
  const [message, setMessage] = useState('Gata');
  const [errorMessage, setErrorMessage] = useState('');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [showPath, setShowPath] = useState(true);
  const [showRisk, setShowRisk] = useState(true);
  const [showCoordinates, setShowCoordinates] = useState(false);
  const requestId = useRef(0);
  const monteCarloStreamCleanup = useRef<(() => void) | undefined>(undefined);

  const runRequest = useCallback(async <T,>(
    action: BusyAction,
    statusMessage: string,
    task: () => Promise<T>,
    onSuccess: (response: T) => void,
  ) => {
    const id = ++requestId.current;
    setBusy(true);
    setBusyAction(action);
    setMessage(statusMessage);
    setErrorMessage('');
    try {
      const response = await task();
      if (id !== requestId.current) return;
      setBackendStatus('online');
      onSuccess(response);
    } catch (error) {
      if (id !== requestId.current) return;
      const detail = error instanceof Error ? error.message : 'Eroare neașteptată la cerere';
      setBackendStatus('offline');
      setErrorMessage(detail);
      setMessage('Problemă de conectare la backend');
    } finally {
      if (id === requestId.current) {
        setBusy(false);
        setBusyAction(undefined);
      }
    }
  }, []);

  const generateMap = useCallback(async (nextConfig = config) => {
    await runRequest(
      'map',
      'Se generează o hartă rezolvabilă...',
      () => safeNavigationApi.preview(nextConfig),
      (response) => {
        setConfig(nextConfig);
        setEnvironment(response.environment);
        setEpisodeResult(undefined);
        setMonteCarlo(undefined);
        setPendingMapConfig(false);
        setActiveStage('scenario');
        setExplanation(response.algorithm_explanation);
        setMessage(`Hartă generată cu sămânța ${nextConfig.random_seed}`);
      },
    );
  }, [config, runRequest]);

  const updateConfig = useCallback((nextConfig: SafeNavigationConfig) => {
    const mapFields: (keyof SafeNavigationConfig)[] = [
      'scenario',
      'rows',
      'cols',
      'wall_probability',
      'danger_probability',
      'movement_noise',
      'risk_weight',
      'experiment_profile',
      'random_seed',
    ];
    const mapChanged = mapFields.some((key) => nextConfig[key] !== config[key]);
    const runChanged = nextConfig.algorithm !== config.algorithm
      || nextConfig.max_steps !== config.max_steps
      || nextConfig.training_episodes !== config.training_episodes
      || nextConfig.number_of_maps !== config.number_of_maps
      || nextConfig.episodes_per_map !== config.episodes_per_map
      || nextConfig.optimization_objective !== config.optimization_objective;
    setConfig(nextConfig);
    if (mapChanged) {
      setPendingMapConfig(true);
      setActiveStage('scenario');
      setMessage('Configurație actualizată. Generează harta pentru a o aplica.');
    } else if (runChanged) {
      setEpisodeResult(undefined);
      setMonteCarlo(undefined);
      if (activeStage === 'results') setActiveStage('run');
      setMessage('Configurație de rulare actualizată.');
    }
  }, [activeStage, config]);

  const runEpisode = useCallback(async () => {
    await runRequest(
      'episode',
      'Se rulează episodul...',
      () => safeNavigationApi.runEpisode(config),
      (response) => {
        setEnvironment(response.environment);
        setEpisodeResult(response.result);
        setPendingMapConfig(false);
        setActiveStage('results');
        setExplanation(response.algorithm_explanation);
        setMessage(response.result.success ? 'Episod reușit' : 'Episod finalizat fără succes');
      },
    );
  }, [config, runRequest]);

  const runMonteCarlo = useCallback(async () => {
    const id = ++requestId.current;
    monteCarloStreamCleanup.current?.();
    setBusy(true);
    setBusyAction('monte-carlo');
    setMessage('Se pornește rularea Monte Carlo live...');
    setErrorMessage('');
    setMonteCarlo(undefined);
    setLiveMonteCarlo(undefined);
    setActiveStage('run');
    try {
      const job = await safeNavigationApi.startMonteCarloJob(config, monteCarloAlgorithms);
      if (id !== requestId.current) return;
      setBackendStatus('online');
      setLiveMonteCarlo(liveStateFromJob(job));
      setMessage('Monte Carlo rulează live');
      let streamClosed = false;
      const closeStream = safeNavigationApi.streamMonteCarloJob(
        job.id,
        (event) => {
          if (id !== requestId.current) return;
          setLiveMonteCarlo((current) => updateLiveState(current, event));
          if (event.type === 'job_finished' && event.result) {
            streamClosed = true;
            setMonteCarlo(event.result);
            setLatestMonteCarlo(event.result);
            setActiveStage('results');
            setBusy(false);
            setBusyAction(undefined);
            setMessage(`Au fost comparate ${event.result.summary.episode_count} episoade`);
            closeStream();
          } else if (event.type === 'job_failed') {
            streamClosed = true;
            const detail = event.message ?? event.error ?? 'Comparația Monte Carlo a eșuat.';
            setErrorMessage(detail);
            setMessage('Monte Carlo a eșuat');
            setBusy(false);
            setBusyAction(undefined);
            closeStream();
          }
        },
        () => {
          if (streamClosed || id !== requestId.current) return;
          setErrorMessage('Conexiunea live cu rularea Monte Carlo s-a întrerupt.');
          setMessage('Stream Monte Carlo întrerupt');
          setBusy(false);
          setBusyAction(undefined);
        },
      );
      monteCarloStreamCleanup.current = closeStream;
    } catch (error) {
      if (id !== requestId.current) return;
      const detail = error instanceof Error ? error.message : 'Eroare neașteptată la pornirea Monte Carlo';
      setBackendStatus('offline');
      setErrorMessage(detail);
      setMessage('Problemă de conectare la backend');
      setBusy(false);
      setBusyAction(undefined);
    }
  }, [config]);

  useEffect(() => () => {
    monteCarloStreamCleanup.current?.();
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      setBackendStatus('checking');
      try {
        const status = await safeNavigationApi.status();
        if (cancelled) return;
        setBackendStatus('online');
        setScenarioPresets(status.scenarios);
        setErrorMessage('');
        setExplanation(status.algorithms.find((item) => item.id === config.algorithm)?.explanation ?? '');
        await generateMap();
      } catch (error) {
        if (cancelled) return;
        setBackendStatus('offline');
        setMessage('Problemă de conectare la backend');
        setErrorMessage(error instanceof Error ? error.message : 'Backend-ul nu poate fi contactat');
      }
    }
    bootstrap();
    return () => {
      cancelled = true;
    };
    // Let React development StrictMode rerun this effect; the cleanup cancels stale responses.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Simulator de navigare sigură</p>
          <h1>Simularea și evaluarea agenților autonomi în medii necunoscute pe grilă</h1>
        </div>
        <div className={`run-status backend-${backendStatus}`}>
          {backendStatus === 'offline' ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
          <span>{busy ? 'Se lucrează' : message}</span>
        </div>
      </header>
      {errorMessage && (
        <section className="backend-alert">
          <Server size={17} />
          <div>
            <strong>Backend indisponibil sau eroare la răspuns.</strong>
            <span>{errorMessage}</span>
          </div>
          <button type="button" onClick={() => generateMap()} disabled={busy}>Reîncearcă</button>
        </section>
      )}

      <ControlPanel
        activeStage={activeStage}
        config={config}
        scenarioPresets={scenarioPresets}
        environment={environment}
        result={episodeResult}
        monteCarlo={monteCarlo}
        liveMonteCarlo={liveMonteCarlo}
        busy={busy}
        busyAction={busyAction}
        pendingMapConfig={pendingMapConfig}
        showPath={showPath}
        showRisk={showRisk}
        showCoordinates={showCoordinates}
        onStageChange={setActiveStage}
        onChange={updateConfig}
        onPreview={(nextConfig) => generateMap(nextConfig)}
        onMonteCarlo={runMonteCarlo}
        onTogglePath={() => setShowPath((value) => !value)}
        onToggleRisk={() => setShowRisk((value) => !value)}
        onToggleCoordinates={() => setShowCoordinates((value) => !value)}
      />
    </div>
  );
}

export default App;
