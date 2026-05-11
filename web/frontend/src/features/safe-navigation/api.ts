import type {
  ExperimentProfileId,
  MonteCarloResult,
  SafeEnvironment,
  SafeEpisodeResult,
  SafeNavigationConfig,
  SafeScenarioPreset,
} from './types';
import { getExperimentProfile } from './experimentProfiles';

const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

async function get<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API}${path}`);
  } catch (error) {
    throw new Error(`Backend-ul nu este disponibil la ${API}. Pornește serverul FastAPI și reîncearcă.`);
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = typeof data.detail === 'string' ? data.detail : `Cererea a eșuat: ${path}`;
    throw new Error(message);
  }
  return data as T;
}

async function post<T>(path: string, payload: unknown): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw new Error(`Backend-ul nu este disponibil la ${API}. Pornește serverul FastAPI și reîncearcă.`);
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = typeof data.detail === 'string' ? data.detail : `Cererea a eșuat: ${path}`;
    throw new Error(message);
  }
  return data as T;
}

export const safeNavigationApi = {
  status: () =>
    get<{
      status: string;
      algorithms: { id: string; name: string; explanation: string }[];
      scenarios: SafeScenarioPreset[];
      defaults: SafeNavigationConfig;
    }>('/api/safe-navigation/status'),
  preview: (config: SafeNavigationConfig) =>
    post<{ environment: SafeEnvironment; algorithm_explanation: string }>(
      '/api/safe-navigation/preview',
      config,
    ),
  runEpisode: (config: SafeNavigationConfig) =>
    post<{
      environment: SafeEnvironment;
      result: SafeEpisodeResult;
      training_history: SafeEpisodeResult[];
      algorithm_explanation: string;
    }>('/api/safe-navigation/episode', config),
  monteCarlo: (config: SafeNavigationConfig, algorithms: string[]) =>
    {
      const profile = getExperimentProfile(config.experiment_profile);
      return post<MonteCarloResult>('/api/safe-navigation/monte-carlo', {
        algorithms,
        experiment_profile: profile.id satisfies ExperimentProfileId,
        scenario: config.scenario,
        number_of_maps: profile.monteCarlo.number_of_maps,
        episodes_per_map: profile.monteCarlo.episodes_per_map,
        training_episodes: config.training_episodes,
        rows: config.rows,
        cols: config.cols,
        wall_probability: config.wall_probability,
        danger_probability: config.danger_probability,
        movement_noise: config.movement_noise,
        risk_weight: config.risk_weight,
        max_steps: config.max_steps,
        random_seed: config.random_seed,
      });
    },
};
