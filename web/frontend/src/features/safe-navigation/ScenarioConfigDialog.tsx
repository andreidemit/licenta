import { useEffect, useState } from 'react';
import { Settings2, X } from 'lucide-react';
import type { SafeNavigationConfig, SafeScenarioPreset } from './types';
import { applyExperimentProfile, experimentProfiles, getExperimentProfile } from './experimentProfiles';

const scenarioLabels: Record<string, string> = {
  easy: 'Ușor',
  medium: 'Mediu',
  hard: 'Dificil',
  custom: 'Personalizat',
};

function fmtProbability(value: number) {
  return `${Math.round(value * 100)}%`;
}

function presetFor(config: SafeNavigationConfig, presets: SafeScenarioPreset[]) {
  return presets.find((preset) => preset.id === config.scenario);
}

type Props = {
  open: boolean;
  busy: boolean;
  config: SafeNavigationConfig;
  scenarioPresets: SafeScenarioPreset[];
  onClose: () => void;
  onApply: (config: SafeNavigationConfig) => void;
  onGenerate: (config: SafeNavigationConfig) => void;
};

export function ScenarioConfigDialog({
  open,
  busy,
  config,
  scenarioPresets,
  onClose,
  onApply,
  onGenerate,
}: Props) {
  const [draft, setDraft] = useState(config);
  const activePreset = presetFor(draft, scenarioPresets);
  const isCustom = draft.scenario === 'custom';
  const activeProfile = getExperimentProfile(draft.experiment_profile);

  useEffect(() => {
    if (open) setDraft(config);
  }, [config, open]);

  if (!open) return null;

  const patch = (next: Partial<SafeNavigationConfig>) => setDraft((current) => ({ ...current, ...next }));
  const changeProfile = (profileId: SafeNavigationConfig['experiment_profile']) => {
    setDraft((current) => applyExperimentProfile(current, profileId));
  };
  const apply = () => {
    onApply(draft);
    onClose();
  };
  const generate = () => {
    onGenerate(draft);
    onClose();
  };

  return (
    <div className="dialog-backdrop" role="presentation" onMouseDown={onClose}>
      <section
        className="scenario-dialog"
        role="dialog"
        aria-modal="true"
        aria-labelledby="scenario-dialog-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <header className="dialog-header">
          <div>
            <p className="eyebrow">Setări scenariu</p>
            <h2 id="scenario-dialog-title"><Settings2 size={18} /> Configurare scenariu</h2>
          </div>
          <button type="button" className="icon-button" aria-label="Închide dialogul" onClick={onClose}>
            <X size={18} />
          </button>
        </header>

        <div className="dialog-section">
          <h3>Scenariu activ</h3>
          <p>
            {scenarioLabels[draft.scenario] ?? draft.scenario}
            {activePreset && !isCustom
              ? `: ${activePreset.rows}x${activePreset.cols}, pereți ${fmtProbability(activePreset.wall_probability)}, pericole ${fmtProbability(activePreset.danger_probability)}.`
              : null}
          </p>
        </div>

        {isCustom ? (
          <div className="dialog-section">
            <h3>Parametrii hărții</h3>
            <div className="two-col">
              <label>Rânduri<input type="number" value={draft.rows} onChange={(event) => patch({ rows: Number(event.target.value) })} /></label>
              <label>Coloane<input type="number" value={draft.cols} onChange={(event) => patch({ cols: Number(event.target.value) })} /></label>
            </div>
            <div className="two-col">
              <label>Densitate pereți<input type="number" step="0.01" value={draft.wall_probability} onChange={(event) => patch({ wall_probability: Number(event.target.value) })} /></label>
              <label>Densitate pericole<input type="number" step="0.01" value={draft.danger_probability} onChange={(event) => patch({ danger_probability: Number(event.target.value) })} /></label>
            </div>
          </div>
        ) : (
          <div className="dialog-section preset-note">
            <h3>Parametrii hărții</h3>
            <p>Dimensiunea și densitățile sunt controlate de presetul selectat. Alege Personalizat pentru a modifica structura hărții.</p>
          </div>
        )}

        <div className="dialog-section">
          <h3>Ce vrem să demonstrăm?</h3>
          <label>
            Profil experimental
            <select value={draft.experiment_profile} onChange={(event) => changeProfile(event.target.value as SafeNavigationConfig['experiment_profile'])}>
              {experimentProfiles.map((profile) => (
                <option key={profile.id} value={profile.id}>{profile.label}</option>
              ))}
            </select>
          </label>
          <div className="profile-explanation-card">
            <strong>{activeProfile.shortLabel}</strong>
            <p>{activeProfile.description}</p>
            <small>{activeProfile.expectedTakeaway}</small>
          </div>
        </div>

        <div className="dialog-section">
          <h3>Setări experimentale</h3>
          <div className="two-col">
            <label>Zgomot mișcare<input type="number" step="0.05" value={draft.movement_noise} onChange={(event) => patch({ movement_noise: Number(event.target.value) })} /></label>
            <label>Pondere risc<input type="number" step="0.1" value={draft.risk_weight} onChange={(event) => patch({ risk_weight: Number(event.target.value) })} /></label>
          </div>
          <label>Seed aleator<input type="number" value={draft.random_seed} onChange={(event) => patch({ random_seed: Number(event.target.value) })} /></label>
        </div>

        <footer className="dialog-actions">
          <button type="button" className="ghost-button" onClick={onClose}>Anulează</button>
          <button type="button" className="secondary-button" onClick={apply}>Aplică</button>
          <button type="button" className="primary-button" disabled={busy} onClick={generate}>Aplică și generează hartă</button>
        </footer>
      </section>
    </div>
  );
}
