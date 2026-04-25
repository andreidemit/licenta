export const cellColors: Record<number, string> = {
  0: '#1e293b',
  1: '#52525b',
  2: '#a16207',
  3: '#10b981',
  4: '#e11d48',
  5: '#a78bfa',
  6: '#38bdf8',
};

export const cellLabels: Record<number, string> = {
  0: 'Liber',
  1: 'Obstacol',
  2: 'Noroi',
  3: 'Hrană',
  4: 'Pericol',
  5: 'Țintă',
  6: 'Pornire',
};

export const cellDescriptions: Record<number, string> = {
  0: 'Celulă traversabilă normală cu cost energetic standard.',
  1: 'Zid sau obstacol — agentul nu poate intra aici.',
  2: 'Teren dificil — consum dublu de energie.',
  3: 'Resursă de hrană — adaugă energie și recompensă.',
  4: 'Zonă periculoasă — sfârșește episodul cu eșec.',
  5: 'Obiectivul final — atingerea înseamnă succes.',
  6: 'Poziția de pornire a agentului.',
};

export const paintTools = [0, 1, 2, 3, 4, 6, 5];

export const actionNames = ['SUS', 'JOS', 'STÂNGA', 'DREAPTA', 'STAI'];

export const statusLabels: Record<string, string> = {
  queued: 'În așteptare',
  running: 'În rulare',
  completed: 'Finalizat',
  failed: 'Eșuat',
  cancelled: 'Anulat',
};

export const outcomeLabels: Record<string, string> = {
  target_reached: 'Țintă atinsă',
  energy_depleted: 'Energie epuizată',
  danger: 'Agent pierdut în pericol',
  timeout: 'Limită de pași',
};

export const backendCellLabels: Record<string, string> = {
  EMPTY: 'Liber',
  OBSTACLE: 'Obstacol',
  MUD: 'Noroi',
  FOOD: 'Hrană',
  DANGER: 'Pericol',
  TARGET: 'Țintă',
  START: 'Pornire',
};

export const artifactLabels: Record<string, string> = {
  results_csv: 'Rezultate CSV',
  convergence_png: 'Grafic convergență',
  epsilon_png: 'Grafic epsilon',
  success_png: 'Grafic succes',
  qtable_path: 'Tabel Q',
  greedy_trajectory_csv: 'Traseu lacom CSV',
  greedy_trajectory_json: 'Traseu lacom JSON',
  manifest_json: 'Manifest JSON',
  environment_map_png: 'Hartă mediu',
  q_heatmap_png: 'Hartă valori Q',
  policy_png: 'Politică învățată',
  visits_png: 'Vizite stări',
  td_error_png: 'Eroare TD',
  greedy_path_png: 'Traseu lacom',
};

export const scenarioMeta: Record<string, { label: string; description: string; accent: string }> = {
  A: {
    label: 'A · Navigare',
    description: 'Energie practic infinită — agentul învață doar topologia hărții.',
    accent: 'from-sky-500/20 to-sky-500/0',
  },
  B: {
    label: 'B · Supraviețuire',
    description: 'Energie limitată — agentul trebuie să echilibreze drumul cu hrana.',
    accent: 'from-emerald-500/20 to-emerald-500/0',
  },
  C: {
    label: 'C · Hartă dinamică',
    description: 'Obstacolele sunt relocate periodic, testând adaptabilitatea.',
    accent: 'from-amber-500/20 to-amber-500/0',
  },
  WAREHOUSE: {
    label: 'Depozit industrial',
    description: 'Hartă fixă 20×20 inspirată dintr-un depozit, mereu aceeași.',
    accent: 'from-violet-500/20 to-violet-500/0',
  },
};

export function translateStatus(status?: string): string {
  return status ? statusLabels[status] ?? status : '—';
}
export function translateOutcome(outcome?: string): string {
  return outcome ? outcomeLabels[outcome] ?? outcome : '—';
}
export function translateBackendCell(cell?: string): string {
  return cell ? backendCellLabels[cell] ?? cell : 'Nicio celulă';
}

const numberFormatter = new Intl.NumberFormat('ro-RO', { maximumFractionDigits: 1 });
const integerFormatter = new Intl.NumberFormat('ro-RO');
const percentFormatter = new Intl.NumberFormat('ro-RO', {
  style: 'percent',
  maximumFractionDigits: 1,
});
const dateFormatter = new Intl.DateTimeFormat('ro-RO', {
  dateStyle: 'medium',
  timeStyle: 'short',
});

export const fmt = {
  number: (value?: number | null, fallback = '—') =>
    value === undefined || value === null || Number.isNaN(value)
      ? fallback
      : numberFormatter.format(value),
  integer: (value?: number | null, fallback = '—') =>
    value === undefined || value === null || Number.isNaN(value)
      ? fallback
      : integerFormatter.format(value),
  percent: (value?: number | null, fallback = '—') =>
    value === undefined || value === null || Number.isNaN(value)
      ? fallback
      : percentFormatter.format(value),
  date: (value?: string | null, fallback = '—') => {
    if (!value) return fallback;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? fallback : dateFormatter.format(date);
  },
};
