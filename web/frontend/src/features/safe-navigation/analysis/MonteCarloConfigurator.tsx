import { useState } from 'react';
import { Loader2, Play, RotateCcw, Settings2, Sparkles } from 'lucide-react';
import type { MonteCarloRawRequest } from '../api';
import { experimentProfiles, getExperimentProfile } from '../experimentProfiles';
import { TooltipLabel } from '../TooltipLabel';
import type { ExperimentProfileId } from '../types';
import { algorithmLabel } from './analysisHelpers';

const ALL_ALGORITHMS: { id: string; description: string }[] = [
  { id: 'random', description: 'Baseline minim, alege uniform.' },
  { id: 'rule_based', description: 'Reguli locale: evită pereții și pericolele.' },
  { id: 'astar', description: 'Planificare clasică pe distanță Manhattan.' },
  { id: 'risk_aware_astar', description: 'A* cu penalizare explicită de risc.' },
  { id: 'tabular_q', description: 'Q-Learning pe coordonate absolute (necesită antrenare).' },
  { id: 'feature_q', description: 'Q-Learning pe trăsături locale (necesită antrenare).' },
];

const SCENARIOS: { id: string; label: string }[] = [
  { id: 'easy', label: 'Ușor' },
  { id: 'medium', label: 'Mediu' },
  { id: 'hard', label: 'Dificil' },
  { id: 'custom', label: 'Personalizat' },
];

export const DEFAULT_MC_PAYLOAD: MonteCarloRawRequest = {
  algorithms: ALL_ALGORITHMS.map((a) => a.id),
  experiment_profile: 'known_static',
  scenario: 'medium',
  rows: 15,
  cols: 15,
  wall_probability: 0.2,
  danger_probability: 0.1,
  movement_noise: 0,
  risk_weight: 1,
  max_steps: 300,
  training_episodes: 150,
  number_of_maps: 6,
  episodes_per_map: 2,
  random_seed: 42,
};

type Props = {
  payload: MonteCarloRawRequest;
  onChange: (payload: MonteCarloRawRequest) => void;
  onRun: () => void;
  busy: boolean;
  error?: string;
  message?: string;
};

function NumberField({
  label,
  value,
  min,
  max,
  step,
  onChange,
  hint,
  tooltip,
}: {
  label: string;
  value: number;
  min?: number;
  max?: number;
  step?: number;
  onChange: (next: number) => void;
  hint?: string;
  tooltip?: string;
}) {
  return (
    <label className="mc-config__field">
      <span>{tooltip ? <TooltipLabel text={tooltip}>{label}</TooltipLabel> : label}</span>
      <input
        type="number"
        value={Number.isFinite(value) ? value : 0}
        min={min}
        max={max}
        step={step ?? 1}
        onChange={(event) => {
          const parsed = Number(event.target.value);
          onChange(Number.isFinite(parsed) ? parsed : 0);
        }}
      />
      {hint && <small>{hint}</small>}
    </label>
  );
}

export function MonteCarloConfigurator({ payload, onChange, onRun, busy, error, message }: Props) {
  const [profileApplied, setProfileApplied] = useState<ExperimentProfileId | undefined>(payload.experiment_profile);

  const totalEpisodes = payload.algorithms.length * payload.number_of_maps * payload.episodes_per_map;
  const heavyTraining = payload.algorithms.some((id) => id === 'tabular_q' || id === 'feature_q');
  const expectedTraining = heavyTraining
    ? payload.algorithms.filter((id) => id === 'tabular_q' || id === 'feature_q').length *
      payload.number_of_maps *
      payload.training_episodes
    : 0;

  function patch(partial: Partial<MonteCarloRawRequest>) {
    onChange({ ...payload, ...partial });
  }

  function toggleAlgorithm(id: string) {
    const next = payload.algorithms.includes(id)
      ? payload.algorithms.filter((value) => value !== id)
      : [...payload.algorithms, id];
    patch({ algorithms: next });
  }

  function applyProfile(id: ExperimentProfileId) {
    const profile = getExperimentProfile(id);
    patch({
      experiment_profile: id,
      scenario: profile.recommended.scenario ?? payload.scenario,
      movement_noise: profile.recommended.movement_noise ?? payload.movement_noise,
      risk_weight: profile.recommended.risk_weight ?? payload.risk_weight,
      training_episodes: profile.recommended.training_episodes ?? payload.training_episodes,
      max_steps: profile.recommended.max_steps ?? payload.max_steps,
      danger_probability: profile.recommended.danger_probability ?? payload.danger_probability,
      number_of_maps: profile.monteCarlo.number_of_maps,
      episodes_per_map: profile.monteCarlo.episodes_per_map,
    });
    setProfileApplied(id);
  }

  function resetDefaults() {
    onChange({ ...DEFAULT_MC_PAYLOAD });
    setProfileApplied(DEFAULT_MC_PAYLOAD.experiment_profile);
  }

  const noAlgorithms = payload.algorithms.length === 0;

  return (
    <section className="panel-card mc-config">
      <header className="mc-config__header">
        <div>
          <h2><Settings2 size={18} /> Configurare experiment</h2>
          <p className="mc-config__subtitle">
            Fluxul principal rulează exclusiv comparația Monte Carlo. Configurezi aici ipoteza,
            algoritmii și bugetul statistic; profilurile completează doar valorile recomandate,
            iar fiecare câmp rămâne editabil manual.
          </p>
        </div>
        <button type="button" className="secondary-button" onClick={resetDefaults} disabled={busy}>
          <RotateCcw size={14} /> Resetează la valori implicite
        </button>
      </header>

      <div className="mc-config__profile">
        <label htmlFor="mc-profile">
          <TooltipLabel text="Profilul setează o ipoteză experimentală și valori recomandate, dar nu blochează editarea manuală.">
            Profil experiment
          </TooltipLabel>
        </label>
        <select
          id="mc-profile"
          className="mc-select"
          value={payload.experiment_profile}
          onChange={(event) => patch({ experiment_profile: event.target.value as ExperimentProfileId })}
          disabled={busy}
        >
          {experimentProfiles.map((profile) => (
            <option key={profile.id} value={profile.id}>{profile.label}</option>
          ))}
        </select>
        <button
          type="button"
          className="secondary-button mc-config__apply"
          onClick={() => applyProfile(payload.experiment_profile)}
          disabled={busy}
        >
          <Sparkles size={14} /> Aplică valorile recomandate
        </button>
        {profileApplied === payload.experiment_profile && (
          <p className="mc-config__profile-hint">
            {getExperimentProfile(payload.experiment_profile).description}
          </p>
        )}
      </div>

      <fieldset className="mc-config__fieldset">
        <legend>Algoritmi comparați</legend>
        <div className="mc-checkbox-grid">
          {ALL_ALGORITHMS.map((algo) => {
            const checked = payload.algorithms.includes(algo.id);
            return (
              <label key={algo.id} className={`mc-checkbox${checked ? ' mc-checkbox--checked' : ''}`}>
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() => toggleAlgorithm(algo.id)}
                  disabled={busy}
                />
                <span>
                  <strong>{algorithmLabel(algo.id)}</strong>
                  <small>{algo.description}</small>
                </span>
              </label>
            );
          })}
        </div>
        {noAlgorithms && (
          <p className="mc-config__warning">Selectează cel puțin un algoritm pentru a putea rula.</p>
        )}
      </fieldset>

      <fieldset className="mc-config__fieldset">
        <legend>Mediu și hartă</legend>
        <div className="mc-config__grid">
          <label className="mc-config__field">
            <span>
              <TooltipLabel text="Preset pentru dimensiunea și dificultatea mediului; custom permite control complet.">
                Scenariu
              </TooltipLabel>
            </span>
            <select
              className="mc-select"
              value={payload.scenario}
              onChange={(event) => patch({ scenario: event.target.value })}
              disabled={busy}
            >
              {SCENARIOS.map((scenario) => (
                <option key={scenario.id} value={scenario.id}>{scenario.label}</option>
              ))}
            </select>
            <small>Doar „personalizat" folosește integral parametrii de mai jos.</small>
          </label>
          <NumberField label="Rânduri (rows)" tooltip="rows = numărul de rânduri ale grilei." value={payload.rows} min={5} max={50}
            onChange={(value) => patch({ rows: value })} />
          <NumberField label="Coloane (cols)" tooltip="cols = numărul de coloane ale grilei." value={payload.cols} min={5} max={50}
            onChange={(value) => patch({ cols: value })} />
          <NumberField label="Densitate pereți" tooltip="Probabilitatea ca o celulă liberă să devină perete/obstacol." value={payload.wall_probability} min={0} max={0.6} step={0.01}
            onChange={(value) => patch({ wall_probability: value })} />
          <NumberField label="Densitate pericole" tooltip="Probabilitatea ca o celulă liberă să devină zonă periculoasă." value={payload.danger_probability} min={0} max={0.4} step={0.01}
            onChange={(value) => patch({ danger_probability: value })} />
          <NumberField label="Zgomot mișcare" tooltip="Probabilitatea ca acțiunea executată să difere de acțiunea cerută de agent." value={payload.movement_noise} min={0} max={1} step={0.05}
            onChange={(value) => patch({ movement_noise: value })}
            hint="0 = determinist, 1 = aleator pur." />
        </div>
      </fieldset>

      <fieldset className="mc-config__fieldset">
        <legend>Recompensă și agenți</legend>
        <div className="mc-config__grid">
          <NumberField label="Pondere risc" tooltip="Cât de mult contează riscul în costul/recompensa episodului." value={payload.risk_weight} min={0} max={10} step={0.1}
            onChange={(value) => patch({ risk_weight: value })}
            hint="Multiplicator al penalizării de risc în recompensă." />
          <NumberField label="Pași maximi / episod" tooltip="Limita după care episodul se termină cu timeout." value={payload.max_steps} min={1} max={5000}
            onChange={(value) => patch({ max_steps: value })} />
          <NumberField label="Episoade de antrenare" tooltip="Numărul de episoade de training pentru agenții Q înainte de evaluare." value={payload.training_episodes} min={0} max={10000}
            onChange={(value) => patch({ training_episodes: value })}
            hint="Folosit doar de Q-Learning tabular și feature." />
        </div>
      </fieldset>

      <fieldset className="mc-config__fieldset">
        <legend>Buget Monte Carlo</legend>
        <div className="mc-config__grid">
          <NumberField label="Număr de hărți" tooltip="Câte hărți generate procedural intră în experiment." value={payload.number_of_maps} min={1} max={100}
            onChange={(value) => patch({ number_of_maps: value })} />
          <NumberField label="Episoade per hartă" tooltip="De câte ori este evaluat fiecare agent pe aceeași hartă." value={payload.episodes_per_map} min={1} max={100}
            onChange={(value) => patch({ episodes_per_map: value })} />
          <NumberField label="Sămânță aleatoare" tooltip="Seed reproductibil pentru generarea hărților și rulărilor." value={payload.random_seed} min={0}
            onChange={(value) => patch({ random_seed: value })}
            hint="Aceeași sămânță reproduce exact aceleași hărți și episoade." />
        </div>
        <p className="mc-config__estimate">
          <strong>Total episoade evaluate:</strong> {totalEpisodes} (
          {payload.algorithms.length} algoritmi × {payload.number_of_maps} hărți × {payload.episodes_per_map} episoade).
          {expectedTraining > 0 && (
            <>
              {' '}<strong>Episoade de antrenare totale:</strong> {expectedTraining}.
            </>
          )}
        </p>
      </fieldset>

      <div className="mc-config__actions">
        <button
          type="button"
          className="primary-button"
          onClick={onRun}
          disabled={busy || noAlgorithms}
        >
          {busy ? <Loader2 size={16} className="mc-spin" /> : <Play size={16} />}
          {busy ? 'Se rulează Monte Carlo...' : 'Rulează Monte Carlo'}
        </button>
        {message && !error && <span className="mc-config__message">{message}</span>}
        {error && <span className="mc-config__error">{error}</span>}
      </div>
    </section>
  );
}

export default MonteCarloConfigurator;
