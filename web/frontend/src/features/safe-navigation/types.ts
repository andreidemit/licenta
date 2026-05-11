export type SafeEnvironment = {
  rows: number;
  cols: number;
  start: number[];
  goal: number[];
  grid: number[][];
  risk_map?: number[][];
};

export type SafeEpisodeResult = {
  algorithm: string;
  success: boolean;
  total_reward: number;
  steps: number;
  collisions: number;
  danger_entries: number;
  total_risk_exposure: number;
  path: number[][];
  path_length: number;
  reached_goal: boolean;
  timeout: boolean;
  events: {
    step: number;
    event_type: string;
    position: number[];
    reward: number;
    risk_cost: number;
    action: number;
    requested_action: number;
    distance_to_goal: number;
  }[];
  computation_time_ms: number;
  total_cost: number;
};

export type SafeNavigationConfig = {
  algorithm: string;
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
  random_seed: number;
};

export type ExperimentProfileId =
  | 'known_static'
  | 'high_risk'
  | 'stochastic_execution'
  | 'same_map_learning'
  | 'transfer_learning'
  | 'training_cost';

export type SafeScenarioPreset = {
  id: string;
  rows: number;
  cols: number;
  wall_probability: number;
  danger_probability: number;
};

export type MonteCarloSummaryRow = {
  algorithm: string;
  episodes: number;
  success_rate: number;
  average_reward: number;
  average_steps: number;
  average_collisions: number;
  collision_rate: number;
  average_danger_entries: number;
  danger_entry_rate: number;
  average_risk_exposure: number;
  average_total_cost: number;
  timeout_rate: number;
  average_computation_time_ms: number;
};

export type MonteCarloResult = {
  config: Record<string, unknown>;
  profile?: {
    id: ExperimentProfileId;
    label: string;
    description: string;
    assumption: string;
    expected_takeaway: string;
    favored_algorithms: string[];
    protocol: string;
  };
  summary: {
    episode_count: number;
    agents: MonteCarloSummaryRow[];
  };
  episodes: SafeEpisodeResult[];
};
