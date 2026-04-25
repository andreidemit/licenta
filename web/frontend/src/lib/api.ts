import type {
  EnvironmentPayload,
  EvaluationResult,
  EvaluationScenario,
  GridPayload,
  JobSnapshot,
  QTableItem,
  StoredEnvironment,
  TrainRequest,
} from './types';

export const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://127.0.0.1:8000';

export function absoluteUrl(path?: string | null): string {
  if (!path) return '#';
  return path.startsWith('http') ? path : `${API_BASE}${path}`;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message =
      (data && typeof data === 'object' && 'detail' in data && (data as { detail?: string }).detail) ||
      `Eroare ${response.status} la ${path}`;
    throw new Error(message);
  }
  return data as T;
}

export const api = {
  health: () => request<{ status: string }>(`/api/health`),
  scenarios: () => request<{ scenarios: { id: string; label: string }[] }>(`/api/scenarios`),
  previewEnvironment: (params: { scenario: string; rows: number; cols: number; seed: number }) =>
    request<GridPayload>(
      `/api/environments/preview?scenario=${params.scenario}&rows=${params.rows}&cols=${params.cols}&seed=${params.seed}`,
    ),
  validateEnvironment: (env: EnvironmentPayload) =>
    request<{ environment: GridPayload }>(`/api/environments/validate`, {
      method: 'POST',
      body: JSON.stringify(env),
    }),
  saveEnvironment: (env: EnvironmentPayload) =>
    request<{ environment: StoredEnvironment }>(`/api/environments`, {
      method: 'POST',
      body: JSON.stringify(env),
    }),
  listEnvironments: () =>
    request<{ environments: StoredEnvironment[] }>(`/api/environments`),
  getEnvironment: (id: string) => request<GridPayload>(`/api/environments/${id}`),
  startTraining: (payload: TrainRequest) =>
    request<JobSnapshot>(`/api/train`, { method: 'POST', body: JSON.stringify(payload) }),
  listRuns: () => request<{ runs: JobSnapshot[] }>(`/api/runs`),
  getRun: (id: string) => request<JobSnapshot>(`/api/runs/${id}`),
  listQTables: () => request<{ qtables: QTableItem[] }>(`/api/qtables`),
  evaluate: (payload: {
    qtable_path: string;
    environments: EnvironmentPayload[];
    energy: number;
  }) =>
    request<{ results: EvaluationResult[] }>(`/api/evaluate`, {
      method: 'POST',
      body: JSON.stringify(payload),
    }),
  evaluationScenarios: () =>
    request<{ scenarios: EvaluationScenario[] }>(`/api/evaluation-scenarios`),
  artifactDownloadUrl: (runId: string, key: string) =>
    absoluteUrl(`/api/runs/${runId}/artifacts/${key}/download`),
  streamUrl: (jobId: string) => `${API_BASE}/api/stream/${jobId}`,
};
