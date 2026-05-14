import type {
  EpisodeExplainRequest,
  ExperimentProfileId,
  LlmAnalysisRequest,
  LlmAnalysisResponse,
  LlmAnalysisStatus,
  LlmConfigRequest,
  LlmConfigResponse,
  MapExplainRequest,
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
        optimization_objective: config.optimization_objective,
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
      optimization_objective: config.optimization_objective,
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
  analysisStatus: () =>
    get<LlmAnalysisStatus>('/api/safe-navigation/analysis/status'),
  explainAnalysis: (payload: LlmAnalysisRequest) =>
    post<LlmAnalysisResponse>('/api/safe-navigation/analysis/explain', payload),
  explainEpisode: (payload: EpisodeExplainRequest) =>
    post<LlmAnalysisResponse>('/api/safe-navigation/episode/explain', payload),
  explainMap: (payload: MapExplainRequest) =>
    post<LlmAnalysisResponse>('/api/safe-navigation/map/explain', payload),
  streamExplainAnalysis: (
    payload: LlmAnalysisRequest,
    onToken: (token: string) => void,
    onDone: () => void,
    onError: (err: Error) => void,
    signal?: AbortSignal,
  ) => {
    fetch(apiUrl('/api/safe-navigation/analysis/explain/stream'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      signal,
    })
      .then(async (response) => {
        if (!response.ok || !response.body) {
          const data = await response.json().catch(() => ({}));
          throw new Error(
            typeof data.detail === 'string' ? data.detail : 'Streaming eșuat',
          );
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() ?? '';
          for (const line of lines) {
            if (!line.startsWith('data:')) continue;
            try {
              const parsed = JSON.parse(line.slice(5).trim());
              if (parsed.error) { onError(new Error(String(parsed.error))); return; }
              if (parsed.done) { onDone(); return; }
              if (typeof parsed.token === 'string') onToken(parsed.token);
            } catch {
              // ignora linii malformate
            }
          }
        }
        onDone();
      })
      .catch((err: unknown) => {
        if (err instanceof Error && err.name === 'AbortError') return;
        onError(err instanceof Error ? err : new Error(String(err)));
      });
  },
  configureAnalysis: (payload: LlmConfigRequest) =>
    post<LlmConfigResponse>('/api/safe-navigation/analysis/configure', payload),
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
  optimization_objective: SafeNavigationConfig['optimization_objective'];
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
