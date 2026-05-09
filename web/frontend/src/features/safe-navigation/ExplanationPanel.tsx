import { BookOpen, Brain, MapPinned, Route, ShieldAlert } from 'lucide-react';
import type { MonteCarloResult, SafeEnvironment, SafeEpisodeResult, SafeNavigationConfig } from './types';

const algorithmNotes: Record<string, string> = {
  random: 'Alege uniform dintre acțiuni. Este util ca baseline, deoarece orice strategie structurată ar trebui să îl depășească.',
  rule_based: 'Folosește reguli locale simple: evită pereții și pericolele imediate, apoi încearcă să se apropie de obiectiv.',
  astar: 'Planifică un drum scurt folosind distanța Manhattan. Este rapid pe hărți noi, dar nu optimizează explicit riscul.',
  risk_aware_astar: 'Planifică folosind atât distanța, cât și costul de risc. Poate alege un traseu mai lung dacă acesta evită zonele periculoase.',
  tabular_q: 'Învață valori Q legate de coordonate absolute. Poate performa bine pe harta de antrenare, dar transferul pe hărți noi este limitat.',
  feature_q: 'Învață din trăsături locale, precum pereți apropiați, pericole apropiate și direcția obiectivului, deci tiparele pot fi transferate mai bine.',
};

function fmt(value?: number, digits = 1) {
  return value === undefined || Number.isNaN(value) ? '-' : value.toFixed(digits);
}

function algorithmLabel(value: string) {
  const labels: Record<string, string> = {
    random: 'Aleator',
    'Random': 'Aleator',
    rule_based: 'Bazat pe reguli',
    'Rule-Based': 'Bazat pe reguli',
    astar: 'A*',
    risk_aware_astar: 'A* conștient de risc',
    'Risk-Aware A*': 'A* conștient de risc',
    tabular_q: 'Q-Learning tabular',
    'Tabular Q-Learning': 'Q-Learning tabular',
    feature_q: 'Q-Learning pe trăsături',
    'Feature-Based Q-Learning': 'Q-Learning pe trăsături',
  };
  return labels[value] ?? value;
}

function scenarioLabel(value: string) {
  const labels: Record<string, string> = {
    easy: 'ușor',
    medium: 'mediu',
    hard: 'dificil',
    custom: 'personalizat',
  };
  return labels[value] ?? value;
}

function selectedAlgorithmContext(config: SafeNavigationConfig) {
  if (config.algorithm === 'tabular_q' || config.algorithm === 'feature_q') {
    return `Înainte de evaluare, backend-ul antrenează agentul timp de ${config.training_episodes} episoade pe harta generată, apoi rulează un episod greedy de test.`;
  }
  if (config.algorithm === 'astar' || config.algorithm === 'risk_aware_astar') {
    return 'Aceasta este o strategie de planificare: calculează ruta direct, fără fază de învățare. De aceea un episod se poate termina foarte rapid.';
  }
  return 'Acest agent nu învață în timpul episodului; este evaluat direct ca strategie de referință.';
}

function monteCarloContext(result?: MonteCarloResult) {
  if (!result?.summary.agents.length) return '';
  const sorted = [...result.summary.agents].sort((a, b) => {
    if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
    return a.average_risk_exposure - b.average_risk_exposure;
  });
  const best = sorted[0];
  return `Ultima rulare Monte Carlo a comparat ${result.summary.episode_count} episoade. Cel mai bun rând este ${algorithmLabel(best.algorithm)}, cu ${Math.round(best.success_rate * 100)}% succes și expunere medie la risc ${fmt(best.average_risk_exposure)}.`;
}

export function ExplanationPanel({
  config,
  environment,
  result,
  monteCarlo,
  text,
}: {
  config: SafeNavigationConfig;
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
  text?: string;
}) {
  const label = algorithmLabel(config.algorithm);
  const mapSummary = environment
    ? `Grilă ${environment.rows}x${environment.cols}, sămânță ${config.random_seed}, scenariu ${scenarioLabel(config.scenario)}.`
    : `Nu există încă o hartă generată.`;
  const episodeSummary = result
    ? `${label} ${result.success ? 'a ajuns la obiectiv' : result.timeout ? 'a depășit limita de pași' : 'a eșuat'} în ${result.steps} pași, recompensă ${fmt(result.total_reward)}, risc ${fmt(result.total_risk_exposure)}.`
    : 'Nu a fost rulat încă niciun episod pentru harta curentă.';
  const comparison = monteCarloContext(monteCarlo);

  return (
    <section className="panel-card explanation-panel">
      <h2><BookOpen size={18} /> Explicație educațională</h2>
      <div className="explanation-block">
        <strong><Brain size={15} /> {label}</strong>
        <p>{text || algorithmNotes[config.algorithm] || 'Alege un algoritm pentru a vedea cum se comportă strategia în simulator.'}</p>
        <p>{selectedAlgorithmContext(config)}</p>
      </div>
      <div className="explanation-block">
        <strong><MapPinned size={15} /> Harta curentă</strong>
        <p>{mapSummary}</p>
        <p>Densitate pereți {config.wall_probability}, densitate pericole {config.danger_probability}, zgomot mișcare {config.movement_noise}, pondere risc {config.risk_weight}.</p>
      </div>
      <div className="explanation-block">
        <strong><Route size={15} /> Episodul curent</strong>
        <p>{episodeSummary}</p>
        {result && (
          <p>{result.collisions === 0 && result.danger_entries === 0
            ? 'Ruta a evitat atât pereții, cât și celulele periculoase.'
            : `Ruta a produs ${result.collisions} coliziuni și ${result.danger_entries} intrări în pericol.`}</p>
        )}
      </div>
      {comparison && (
        <div className="explanation-block">
          <strong><ShieldAlert size={15} /> Insight comparativ</strong>
          <p>{comparison}</p>
        </div>
      )}
    </section>
  );
}
