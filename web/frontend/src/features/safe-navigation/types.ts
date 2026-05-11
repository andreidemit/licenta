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
  map_seed?: number | null;
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

export type MonteCarloDistribution = {
  mean: number;
  std: number;
  p05: number;
  p25: number;
  p50: number;
  p75: number;
  p95: number;
  ci95_low: number;
  ci95_high: number;
  min: number;
  max: number;
};

export type MonteCarloSummaryRow = {
  algorithm: string;
  episodes: number;
  success_rate: number;
  success_rate_ci95_low?: number;
  success_rate_ci95_high?: number;
  average_reward: number;
  average_steps: number;
  average_collisions: number;
  collision_rate: number;
  collision_rate_ci95_low?: number;
  collision_rate_ci95_high?: number;
  average_danger_entries: number;
  danger_entry_rate: number;
  danger_entry_rate_ci95_low?: number;
  danger_entry_rate_ci95_high?: number;
  average_risk_exposure: number;
  average_total_cost: number;
  timeout_rate: number;
  timeout_rate_ci95_low?: number;
  timeout_rate_ci95_high?: number;
  average_computation_time_ms: number;
  reward_distribution?: MonteCarloDistribution;
  steps_distribution?: MonteCarloDistribution;
  risk_distribution?: MonteCarloDistribution;
};

export type MonteCarloPerMapRow = {
  map_seed: number;
  algorithm: string;
  episodes: number;
  success_rate: number;
  average_reward: number;
  average_steps: number;
  average_risk_exposure: number;
  collision_rate: number;
  danger_entry_rate: number;
  timeout_rate: number;
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
    per_map?: MonteCarloPerMapRow[];
  };
  episodes: SafeEpisodeResult[];
};
