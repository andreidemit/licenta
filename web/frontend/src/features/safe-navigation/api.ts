import type {
  ExperimentProfileId,
  MonteCarloJobSnapshot,
  MonteCarloLiveEvent,
  MonteCarloResult,
  SafeEnvironment,
  SafeEpisodeResult,
  SafeNavigationConfig,
  SafeScenarioPreset,
} from './types';
import { getExperimentProfile } from './experimentProfiles';

const API = import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000';

function apiUrl(path: string) {
  return `${API}${path}`;
}

async function get<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(apiUrl(path));
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
    response = await fetch(apiUrl(path), {
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
        number_of_maps: config.number_of_maps,
        episodes_per_map: config.episodes_per_map,
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
  monteCarloRaw: (payload: MonteCarloRawRequest) =>
    post<MonteCarloResult>('/api/safe-navigation/monte-carlo', payload),
  startMonteCarloJob: (config: SafeNavigationConfig, algorithms: string[]) => {
    const profile = getExperimentProfile(config.experiment_profile);
    return post<MonteCarloJobSnapshot>('/api/safe-navigation/monte-carlo/jobs', {
      algorithms,
      experiment_profile: profile.id satisfies ExperimentProfileId,
      scenario: config.scenario,
      number_of_maps: config.number_of_maps,
      episodes_per_map: config.episodes_per_map,
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
  getMonteCarloJob: (jobId: string) =>
    get<MonteCarloJobSnapshot>(`/api/safe-navigation/monte-carlo/jobs/${jobId}`),
  streamMonteCarloJob: (
    jobId: string,
    onEvent: (event: MonteCarloLiveEvent) => void,
    onError: (error: Event) => void,
  ) => {
    const source = new EventSource(apiUrl(`/api/safe-navigation/monte-carlo/jobs/${jobId}/stream`));
    source.onmessage = (message) => {
      try {
        onEvent(JSON.parse(message.data) as MonteCarloLiveEvent);
      } catch (error) {
        onError(message);
      }
    };
    source.onerror = onError;
    return () => source.close();
  },
};

export type MonteCarloRawRequest = {
  algorithms: string[];
  experiment_profile: ExperimentProfileId;
  scenario: string;
  rows: number;
  cols: number;
  wall_probability: number;
  danger_probability: number;
  movement_noise: number;
  risk_weight: number;
  max_steps: number;
  training_episodes: number;
  number_of_maps: number;
  episodes_per_map: number;
  random_seed: number;
};
