import type { MonteCarloResult, SafeEpisodeResult } from '../types';

const AGENT_COLORS: Record<string, string> = {
  random: '#f59e0b',
  Random: '#f59e0b',
  rule_based: '#ca8a04',
  'Rule-Based': '#ca8a04',
  astar: '#0ea5e9',
  'A*': '#0ea5e9',
  risk_aware_astar: '#7c3aed',
  'Risk-Aware A*': '#7c3aed',
  tabular_q: '#dc2626',
  'Tabular Q-Learning': '#dc2626',
  feature_q: '#0f766e',
  'Feature-Based Q-Learning': '#0f766e',
  feature_risk_astar: '#2563eb',
  'Feature-Risk A*': '#2563eb',
};

export const CHART_THEME = {
  grid: '#e2e8f0',
  axis: '#475569',
  axisLabel: '#1f2937',
  tooltipBg: '#ffffff',
  tooltipBorder: '#d5deea',
  tooltipText: '#142033',
  median: '#0f766e',
  mean: '#dc2626',
  errorBar: '#0f172a',
} as const;

export function colorFor(algorithm: string): string {
  if (AGENT_COLORS[algorithm]) return AGENT_COLORS[algorithm];
  let hash = 0;
  for (let i = 0; i < algorithm.length; i += 1) {
    hash = (hash * 31 + algorithm.charCodeAt(i)) >>> 0;
  }
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 60%)`;
}

const ALGORITHM_LABELS: Record<string, string> = {
  random: 'Aleator',
  Random: 'Aleator',
  rule_based: 'Bazat pe reguli',
  'Rule-Based': 'Bazat pe reguli',
  astar: 'A*',
  risk_aware_astar: 'A* conștient de risc',
  'Risk-Aware A*': 'A* conștient de risc',
  tabular_q: 'Q-Learning tabular',
  'Tabular Q-Learning': 'Q-Learning tabular',
  feature_q: 'Q-Learning pe trăsături',
  'Feature-Based Q-Learning': 'Q-Learning pe trăsături',
  feature_risk_astar: 'Feature-Risk A* experimental',
  'Feature-Risk A*': 'Feature-Risk A* experimental',
};

export function algorithmLabel(value: string): string {
  return ALGORITHM_LABELS[value] ?? value;
}

export function formatNumber(value: number, digits = 2): string {
  if (!Number.isFinite(value)) return '-';
  if (Math.abs(value) >= 100) return value.toFixed(0);
  return value.toFixed(digits);
}

export function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function groupEpisodesByAlgorithm(
  result: MonteCarloResult,
): Record<string, SafeEpisodeResult[]> {
  const grouped: Record<string, SafeEpisodeResult[]> = {};
  for (const episode of result.episodes) {
    if (!grouped[episode.algorithm]) grouped[episode.algorithm] = [];
    grouped[episode.algorithm].push(episode);
  }
  return grouped;
}

export function quantile(sorted: number[], q: number): number {
  if (!sorted.length) return 0;
  if (sorted.length === 1) return sorted[0];
  const rank = q * (sorted.length - 1);
  const lower = Math.floor(rank);
  const upper = Math.ceil(rank);
  if (lower === upper) return sorted[lower];
  const weight = rank - lower;
  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

export function computeBoxStats(values: number[]) {
  const sorted = [...values].sort((a, b) => a - b);
  return {
    min: sorted[0] ?? 0,
    p05: quantile(sorted, 0.05),
    p25: quantile(sorted, 0.25),
    p50: quantile(sorted, 0.5),
    p75: quantile(sorted, 0.75),
    p95: quantile(sorted, 0.95),
    max: sorted[sorted.length - 1] ?? 0,
    mean: sorted.length ? sorted.reduce((a, b) => a + b, 0) / sorted.length : 0,
    count: sorted.length,
  };
}

export function buildOccupancyHeatmap(
  episodes: SafeEpisodeResult[],
  rows: number,
  cols: number,
): { matrix: number[][]; max: number } {
  const matrix: number[][] = Array.from({ length: rows }, () => Array.from({ length: cols }, () => 0));
  for (const episode of episodes) {
    for (const position of episode.path ?? []) {
      const row = position[0];
      const col = position[1];
      if (row >= 0 && row < rows && col >= 0 && col < cols) {
        matrix[row][col] += 1;
      }
    }
  }
  let max = 0;
  for (const row of matrix) {
    for (const value of row) {
      if (value > max) max = value;
    }
  }
  return { matrix, max };
}

export function downloadFile(filename: string, content: string, mime = 'text/csv') {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

export function summaryToCsv(result: MonteCarloResult): string {
  const headers = [
    'algorithm',
    'episodes',
    'success_rate',
    'success_rate_ci95_low',
    'success_rate_ci95_high',
    'average_reward',
    'reward_std',
    'reward_p25',
    'reward_p50',
    'reward_p75',
    'average_steps',
    'steps_std',
    'average_risk_exposure',
    'risk_std',
    'collision_rate',
    'danger_entry_rate',
    'timeout_rate',
    'average_computation_time_ms',
  ];
  const rows = result.summary.agents.map((row) => [
    row.algorithm,
    row.episodes,
    row.success_rate,
    row.success_rate_ci95_low ?? '',
    row.success_rate_ci95_high ?? '',
    row.average_reward,
    row.reward_distribution?.std ?? '',
    row.reward_distribution?.p25 ?? '',
    row.reward_distribution?.p50 ?? '',
    row.reward_distribution?.p75 ?? '',
    row.average_steps,
    row.steps_distribution?.std ?? '',
    row.average_risk_exposure,
    row.risk_distribution?.std ?? '',
    row.collision_rate,
    row.danger_entry_rate,
    row.timeout_rate,
    row.average_computation_time_ms,
  ]);
  return [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
}

export function episodesToCsv(result: MonteCarloResult): string {
  const headers = [
    'algorithm',
    'map_seed',
    'success',
    'total_reward',
    'steps',
    'total_risk_exposure',
    'collisions',
    'danger_entries',
    'timeout',
    'computation_time_ms',
  ];
  const rows = result.episodes.map((episode) => [
    episode.algorithm,
    episode.map_seed ?? '',
    episode.success ? 1 : 0,
    episode.total_reward,
    episode.steps,
    episode.total_risk_exposure,
    episode.collisions,
    episode.danger_entries,
    episode.timeout ? 1 : 0,
    episode.computation_time_ms,
  ]);
  return [headers.join(','), ...rows.map((row) => row.join(','))].join('\n');
}

export function svgToPng(svg: SVGSVGElement, scale = 2): Promise<string> {
  const xml = new XMLSerializer().serializeToString(svg);
  const svg64 = `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(xml)))}`;
  const bbox = svg.getBoundingClientRect();
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = Math.max(1, Math.floor(bbox.width * scale));
      canvas.height = Math.max(1, Math.floor(bbox.height * scale));
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        reject(new Error('Canvas indisponibil'));
        return;
      }
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      resolve(canvas.toDataURL('image/png'));
    };
    image.onerror = () => reject(new Error('Nu am putut converti SVG-ul'));
    image.src = svg64;
  });
}
