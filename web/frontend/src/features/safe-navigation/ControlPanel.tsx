import { BarChart3, Bot, Dice5, GraduationCap, Map, Play, RefreshCw, SlidersHorizontal } from 'lucide-react';
import type { SafeNavigationConfig } from './types';

const algorithms = [
  ['random', 'Aleator'],
  ['rule_based', 'Bazat pe reguli'],
  ['astar', 'A*'],
  ['risk_aware_astar', 'A* conștient de risc'],
  ['tabular_q', 'Q-Learning tabular'],
  ['feature_q', 'Q-Learning pe trăsături'],
];

const scenarios = [
  ['easy', 'Ușor'],
  ['medium', 'Mediu'],
  ['hard', 'Dificil'],
  ['custom', 'Personalizat'],
];

type Props = {
  config: SafeNavigationConfig;
  busy: boolean;
  onChange: (config: SafeNavigationConfig) => void;
  onPreview: () => void;
  onEpisode: () => void;
  onMonteCarlo: () => void;
};

export function ControlPanel({ config, busy, onChange, onPreview, onEpisode, onMonteCarlo }: Props) {
  const patch = (next: Partial<SafeNavigationConfig>) => onChange({ ...config, ...next });

  return (
    <aside className="control-panel">
      <section className="panel-card setup-card">
        <h2><Bot size={18} /> Configurare experiment</h2>
        <div className="form-section">
          <label>
            Alege algoritmul
            <select value={config.algorithm} onChange={(event) => patch({ algorithm: event.target.value })}>
              {algorithms.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
            </select>
          </label>
          <label>
            Scenariu
            <select value={config.scenario} onChange={(event) => patch({ scenario: event.target.value })}>
              {scenarios.map(([id, label]) => <option key={id} value={id}>{label}</option>)}
            </select>
          </label>
        </div>

        <div className="form-section">
          <h3><Map size={15} /> Parametrii mediului</h3>
          <div className="two-col">
            <label>Rânduri<input type="number" value={config.rows} onChange={(event) => patch({ rows: Number(event.target.value) })} /></label>
            <label>Coloane<input type="number" value={config.cols} onChange={(event) => patch({ cols: Number(event.target.value) })} /></label>
          </div>
          <div className="two-col">
            <label>Densitate pereți<input type="number" step="0.01" value={config.wall_probability} onChange={(event) => patch({ wall_probability: Number(event.target.value) })} /></label>
            <label>Densitate pericole<input type="number" step="0.01" value={config.danger_probability} onChange={(event) => patch({ danger_probability: Number(event.target.value) })} /></label>
          </div>
          <div className="two-col">
            <label>Zgomot mișcare<input type="number" step="0.05" value={config.movement_noise} onChange={(event) => patch({ movement_noise: Number(event.target.value) })} /></label>
            <label>Pondere risc<input type="number" step="0.1" value={config.risk_weight} onChange={(event) => patch({ risk_weight: Number(event.target.value) })} /></label>
          </div>
        </div>

        <div className="form-section">
          <h3><GraduationCap size={15} /> Învățare / evaluare</h3>
          <div className="two-col">
            <label>Episoade antrenare<input type="number" value={config.training_episodes} onChange={(event) => patch({ training_episodes: Number(event.target.value) })} /></label>
            <label>Seed aleator<input type="number" value={config.random_seed} onChange={(event) => patch({ random_seed: Number(event.target.value) })} /></label>
          </div>
        </div>
      </section>

      <section className="panel-card control-actions sticky-actions">
        <h2><Dice5 size={18} /> Controale simulare <SlidersHorizontal size={15} /></h2>
        <button className="secondary-button" disabled={busy} onClick={onPreview}><RefreshCw size={16} /> Generează hartă</button>
        <button className="primary-button" disabled={busy} onClick={onEpisode}><Play size={16} /> Rulează episod</button>
        <button className="secondary-button" disabled={busy} onClick={onMonteCarlo}><BarChart3 size={16} /> Compară Monte Carlo</button>
      </section>
    </aside>
  );
}
