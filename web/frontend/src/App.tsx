import { useCallback, useEffect, useRef, useState } from 'react';
import { Server, ShieldAlert, ShieldCheck } from 'lucide-react';
import './styles.css';
import { safeNavigationApi } from './features/safe-navigation/api';
import { ControlPanel } from './features/safe-navigation/ControlPanel';
import { ExperimentDashboard } from './features/safe-navigation/ExperimentDashboard';
import { ExplanationPanel } from './features/safe-navigation/ExplanationPanel';
import { GridWorldView } from './features/safe-navigation/GridWorldView';
import { MetricsPanel } from './features/safe-navigation/MetricsPanel';
import type {
  MonteCarloResult,
  SafeEnvironment,
  SafeEpisodeResult,
  SafeNavigationConfig,
} from './features/safe-navigation/types';

const initialConfig: SafeNavigationConfig = {
  algorithm: 'risk_aware_astar',
  scenario: 'medium',
  rows: 15,
  cols: 15,
  wall_probability: 0.2,
  danger_probability: 0.1,
  movement_noise: 0,
  risk_weight: 1,
  max_steps: 300,
  training_episodes: 150,
  random_seed: 42,
};

type BusyAction = 'map' | 'episode' | 'monte-carlo';

export function App() {
  const [config, setConfig] = useState(initialConfig);
  const [environment, setEnvironment] = useState<SafeEnvironment>();
  const [episodeResult, setEpisodeResult] = useState<SafeEpisodeResult>();
  const [monteCarlo, setMonteCarlo] = useState<MonteCarloResult>();
  const [explanation, setExplanation] = useState('');
  const [busy, setBusy] = useState(false);
  const [busyAction, setBusyAction] = useState<BusyAction>();
  const [message, setMessage] = useState('Ready');
  const [errorMessage, setErrorMessage] = useState('');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [showPath, setShowPath] = useState(true);
  const [showRisk, setShowRisk] = useState(true);
  const [showCoordinates, setShowCoordinates] = useState(false);
  const requestId = useRef(0);

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
      const detail = error instanceof Error ? error.message : 'Unexpected request failure';
      setBackendStatus('offline');
      setErrorMessage(detail);
      setMessage('Backend connection problem');
    } finally {
      if (id === requestId.current) {
        setBusy(false);
        setBusyAction(undefined);
      }
    }
  }, []);

  const generateMap = useCallback(async () => {
    await runRequest(
      'map',
      'Generating solvable map...',
      () => safeNavigationApi.preview(config),
      (response) => {
        setEnvironment(response.environment);
        setEpisodeResult(undefined);
        setExplanation(response.algorithm_explanation);
        setMessage('Map generated');
      },
    );
  }, [config, runRequest]);

  const runEpisode = useCallback(async () => {
    await runRequest(
      'episode',
      'Running episode...',
      () => safeNavigationApi.runEpisode(config),
      (response) => {
        setEnvironment(response.environment);
        setEpisodeResult(response.result);
        setExplanation(response.algorithm_explanation);
        setMessage(response.result.success ? 'Episode succeeded' : 'Episode finished without success');
      },
    );
  }, [config, runRequest]);

  const runMonteCarlo = useCallback(async () => {
    await runRequest(
      'monte-carlo',
      'Running Monte Carlo comparison...',
      () => safeNavigationApi.monteCarlo(config, [
        'random',
        'rule_based',
        'astar',
        'risk_aware_astar',
        'tabular_q',
        'feature_q',
      ]),
      (response) => {
        setMonteCarlo(response);
        setMessage(`Compared ${response.summary.episode_count} episodes`);
      },
    );
  }, [config, runRequest]);

  useEffect(() => {
    let cancelled = false;
    async function bootstrap() {
      setBackendStatus('checking');
      try {
        const status = await safeNavigationApi.status();
        if (cancelled) return;
        setBackendStatus('online');
        setErrorMessage('');
        setExplanation(status.algorithms.find((item) => item.id === config.algorithm)?.explanation ?? '');
        await generateMap();
      } catch (error) {
        if (cancelled) return;
        setBackendStatus('offline');
        setMessage('Backend connection problem');
        setErrorMessage(error instanceof Error ? error.message : 'Could not reach the backend');
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
          <p className="eyebrow">Safe Navigation Simulator</p>
          <h1>Simulation and evaluation of autonomous agents in unknown grid-based environments</h1>
        </div>
        <div className={`run-status backend-${backendStatus}`}>
          {backendStatus === 'offline' ? <ShieldAlert size={18} /> : <ShieldCheck size={18} />}
          <span>{busy ? 'Working' : message}</span>
        </div>
      </header>
      {errorMessage && (
        <section className="backend-alert">
          <Server size={17} />
          <div>
            <strong>Backend unavailable or returned an error.</strong>
            <span>{errorMessage}</span>
          </div>
          <button type="button" onClick={generateMap} disabled={busy}>Retry</button>
        </section>
      )}

      <div className="workspace">
        <ControlPanel
          config={config}
          busy={busy}
          onChange={setConfig}
          onPreview={generateMap}
          onEpisode={runEpisode}
          onMonteCarlo={runMonteCarlo}
        />
        <div className="center-stack">
          <GridWorldView
            environment={environment}
            result={episodeResult}
            showPath={showPath}
            showRisk={showRisk}
            showCoordinates={showCoordinates}
            onTogglePath={() => setShowPath((value) => !value)}
            onToggleRisk={() => setShowRisk((value) => !value)}
            onToggleCoordinates={() => setShowCoordinates((value) => !value)}
          />
          <ExperimentDashboard result={monteCarlo} busy={busyAction === 'monte-carlo'} />
        </div>
        <div className="right-stack">
          <MetricsPanel config={config} result={episodeResult} />
          <ExplanationPanel text={explanation} />
        </div>
      </div>
    </div>
  );
}

export default App;
