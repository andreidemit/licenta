export type GridPayload = {
  id?: string | null;
  name?: string | null;
  rows: number;
  cols: number;
  start: number[];
  target: number[];
  bfs_distance: number | null;
  grid: number[][];
};

export type EnvironmentPayload = {
  id?: string | null;
  name: string;
  rows: number;
  cols: number;
  start: number[];
  target: number[];
  grid: number[][];
};

export type LiveAgent = {
  position: number[];
  energy: number;
  energy_percent: number;
  steps: number;
  reward: number;
  alive: boolean;
  reached_target: boolean;
};

export type LiveEvent = {
  type: string;
  environment?: GridPayload;
  agent?: LiveAgent;
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

export type JobSnapshot = {
  id: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled' | string;
  scenario: string;
  progress: number;
  message: string;
  artifacts: Record<string, string>;
  latest_event?: LiveEvent;
  created_at?: string;
  updated_at?: string;
};

export type QTableItem = {
  path: string;
  run_id: string;
  download_url?: string;
};

export type StoredEnvironment = {
  id: string;
  name: string;
  rows: number;
  cols: number;
  bfs_distance: number | null;
  path: string;
};

export type EvaluationScenario = {
  id: string;
  name: string;
  description: string;
  environment: GridPayload;
};

export type TrajectoryStep = {
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

export type EvaluationResult = {
  environment: GridPayload;
  outcome: string;
  steps: number;
  reward: number;
  energy_remaining: number;
  bfs_distance: number | null;
  bfs_overhead: number | null;
  trajectory: TrajectoryStep[];
};

export type ScenarioId = 'A' | 'B' | 'C' | 'WAREHOUSE';

export type TrainRequest = {
  scenario: ScenarioId | string;
  rows: number;
  cols: number;
  seed: number;
  episodes: number;
};
