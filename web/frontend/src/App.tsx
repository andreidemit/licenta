import { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
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

export function App() {
  const [config, setConfig] = useState(initialConfig);
  const [environment, setEnvironment] = useState<SafeEnvironment>();
  const [episodeResult, setEpisodeResult] = useState<SafeEpisodeResult>();
  const [monteCarlo, setMonteCarlo] = useState<MonteCarloResult>();
  const [explanation, setExplanation] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('Ready');
  const [showPath, setShowPath] = useState(true);
  const [showRisk, setShowRisk] = useState(true);
  const [showCoordinates, setShowCoordinates] = useState(false);

  async function generateMap() {
    setBusy(true);
    setMessage('Generating solvable map...');
    try {
      const response = await safeNavigationApi.preview(config);
      setEnvironment(response.environment);
      setEpisodeResult(undefined);
      setExplanation(response.algorithm_explanation);
      setMessage('Map generated');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Map generation failed');
    } finally {
      setBusy(false);
    }
  }

  async function runEpisode() {
    setBusy(true);
    setMessage('Running episode...');
    try {
      const response = await safeNavigationApi.runEpisode(config);
      setEnvironment(response.environment);
      setEpisodeResult(response.result);
      setExplanation(response.algorithm_explanation);
      setMessage(response.result.success ? 'Episode succeeded' : 'Episode finished without success');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Episode failed');
    } finally {
      setBusy(false);
    }
  }

  async function runMonteCarlo() {
    setBusy(true);
    setMessage('Running Monte Carlo comparison...');
    try {
      const response = await safeNavigationApi.monteCarlo(config, [
        'random',
        'rule_based',
        'astar',
        'risk_aware_astar',
        'tabular_q',
        'feature_q',
      ]);
      setMonteCarlo(response);
      setMessage(`Compared ${response.summary.episode_count} episodes`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Monte Carlo failed');
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    generateMap();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Safe Navigation Simulator</p>
          <h1>Simulation and evaluation of autonomous agents in unknown grid-based environments</h1>
        </div>
        <div className="run-status">
          <ShieldCheck size={18} />
          <span>{busy ? 'Working' : message}</span>
        </div>
      </header>

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
          <ExperimentDashboard result={monteCarlo} />
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
