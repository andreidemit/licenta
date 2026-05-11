import { useState } from 'react';
import { BookOpen, Brain, ChevronDown, ChevronUp, MapPinned, Route, ShieldAlert } from 'lucide-react';
import type { MonteCarloResult, SafeEnvironment, SafeEpisodeResult, SafeNavigationConfig } from './types';

const algorithmNotes: Record<string, string> = {
  random: 'Alege uniform dintre acțiuni. Este util ca baseline, deoarece orice strategie structurată ar trebui să îl depășească.',
  rule_based: 'Folosește reguli locale simple: evită pereții și pericolele imediate, apoi încearcă să se apropie de obiectiv.',
  astar: 'Planifică un drum scurt folosind distanța Manhattan. Este rapid pe hărți noi, dar nu optimizează explicit riscul.',
  risk_aware_astar: 'Planifică folosind atât distanța, cât și costul de risc. Poate alege un traseu mai lung dacă acesta evită zonele periculoase.',
  tabular_q: 'Învață valori Q legate de coordonate absolute. Poate performa bine pe harta de antrenare, dar transferul pe hărți noi este limitat.',
  feature_q: 'Învață din trăsături locale, precum pereți apropiați, pericole apropiate și direcția obiectivului, deci tiparele pot fi transferate mai bine.',
  sarsa: 'Algoritm on-policy: actualizează Q(s,a) cu acțiunea efectiv aleasă în starea următoare, nu cu maximul. Este mai conservator decât Q-Learning în zone cu risc.',
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
    sarsa: 'SARSA tabular',
    'SARSA tabular': 'SARSA tabular',
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
  if (config.algorithm === 'tabular_q' || config.algorithm === 'feature_q' || config.algorithm === 'sarsa') {
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

function detailedAlgorithmExplanation(config: SafeNavigationConfig) {
  const notes: Record<string, string> = {
    random: 'Agentul aleator nu planifică și nu învață. El alege o direcție la întâmplare, deci este folosit ca punct de plecare: dacă un algoritm serios nu îl depășește, atunci strategia respectivă nu aduce valoare în acel scenariu.',
    rule_based: 'Agentul bazat pe reguli folosește decizii simple: evită imediat pereții și pericolele, apoi încearcă să se apropie de obiectiv. Este ușor de explicat, dar poate eșua când are nevoie de ocoluri mai lungi.',
    astar: 'A* este un algoritm de planificare. El caută un drum scurt spre obiectiv folosind distanța Manhattan ca estimare. Este rapid pe hărți noi, dar varianta clasică nu tratează riscul ca obiectiv principal.',
    risk_aware_astar: 'A* conștient de risc extinde planificarea clasică: nu caută doar drumul scurt, ci adaugă penalizări pentru celulele periculoase și zonele apropiate de pericol. De aceea poate prefera un traseu mai lung, dar mai sigur.',
    tabular_q: `Q-Learning tabular învață valori pentru poziții exacte din hartă. În această configurație este antrenat ${config.training_episodes} episoade, apoi testat. Poate merge bine pe harta de antrenare, dar generalizează mai greu când harta se schimbă.`,
    feature_q: `Q-Learning pe trăsături nu memorează doar coordonate, ci folosește semnale locale: pereți apropiați, pericole apropiate și direcția obiectivului. După ${config.training_episodes} episoade de antrenare, poate transfera mai bine tipare de siguranță pe hărți noi.`,
    sarsa: `SARSA este un algoritm on-policy: actualizează Q(s,a) cu valoarea acțiunii efectiv alese în pasul următor, nu cu maximul posibil (ca Q-Learning). Aceasta îl face mai conservator — preferă trasee mai sigure — cu prețul unei convergențe ușor mai lente. Antrenament: ${config.training_episodes} episoade.`,
  };
  return notes[config.algorithm] || 'Algoritmul selectat este evaluat pe harta curentă folosind aceleași metrici ca restul strategiilor.';
}

function detailedEpisodeExplanation(result?: SafeEpisodeResult) {
  if (!result) {
    return 'După ce rulezi un episod, aici vei vedea cum se interpretează traseul: dacă agentul a ajuns la obiectiv, cât de lung a fost drumul și cât risc a acumulat.';
  }
  const status = result.success
    ? 'Agentul a ajuns la obiectiv, deci episodul este considerat reușit.'
    : result.timeout
      ? 'Agentul a atins limita de pași, deci nu a găsit o soluție suficient de rapidă.'
      : 'Agentul nu a finalizat cu succes, de obicei din cauza unei decizii nesigure sau a unui blocaj.';
  const safety = result.collisions === 0 && result.danger_entries === 0
    ? 'Din perspectiva siguranței, traseul este curat: nu există coliziuni și nici intrări în pericol.'
    : `Din perspectiva siguranței, traseul are ${result.collisions} coliziuni și ${result.danger_entries} intrări în pericol, deci trebuie analizate deciziile din acele zone.`;
  return `${status} A executat ${result.steps} pași, a obținut recompensa ${fmt(result.total_reward)} și a acumulat risc ${fmt(result.total_risk_exposure)}. ${safety}`;
}

function detailedMetricsExplanation() {
  return 'Pașii măsoară eficiența traseului. Recompensa este scorul global al episodului. Riscul măsoară expunerea la pericole. Coliziunile arată încercări de mișcare în pereți. Pericolul arată intrări în celule periculoase. Costul total combină efortul traseului cu penalizările, fiind util pentru comparații între agenți.';
}

function detailedComparisonExplanation(monteCarlo?: MonteCarloResult) {
  if (!monteCarlo?.summary.agents.length) {
    return 'Comparația Monte Carlo rulează mai mulți agenți pe mai multe hărți generate. Scopul este să nu judecăm un algoritm după un singur episod norocos sau ghinionist, ci după performanța medie.';
  }
  return `${monteCarloContext(monteCarlo)} Citește tabelul comparativ astfel: succesul arată robustețea, pașii arată eficiența, iar riscul arată cât de sigur este traseul. Un algoritm poate fi mai lent, dar mai potrivit pentru navigare sigură dacă reduce expunerea la pericol.`;
}

export function ExplanationPanel({
  config,
  environment,
  result,
  monteCarlo,
  text,
  compact = false,
}: {
  config: SafeNavigationConfig;
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
  text?: string;
  compact?: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const label = algorithmLabel(config.algorithm);
  const mapSummary = environment
    ? `Grilă ${environment.rows}x${environment.cols}, sămânță ${config.random_seed}, scenariu ${scenarioLabel(config.scenario)}.`
    : `Nu există încă o hartă generată.`;
  const episodeSummary = result
    ? `${label} ${result.success ? 'a ajuns la obiectiv' : result.timeout ? 'a depășit limita de pași' : 'a eșuat'} în ${result.steps} pași, recompensă ${fmt(result.total_reward)}, risc ${fmt(result.total_risk_exposure)}.`
    : 'Nu a fost rulat încă niciun episod pentru harta curentă.';
  const comparison = monteCarloContext(monteCarlo);

  if (compact) {
    const compactContext = config.algorithm === 'tabular_q' || config.algorithm === 'feature_q' || config.algorithm === 'sarsa'
      ? `A fost antrenat ${config.training_episodes} episoade, apoi evaluat pe traseul afișat.`
      : 'Este o strategie rulată direct, fără antrenare; traseul apare imediat după planificare.';
    return (
      <section className={expanded ? 'panel-card explanation-panel compact-explanation expanded' : 'panel-card explanation-panel compact-explanation'}>
        <h2><BookOpen size={18} /> Explicație educațională</h2>
        <div className="explanation-block">
          <strong><Brain size={15} /> {label}</strong>
          <p>{text || algorithmNotes[config.algorithm] || 'Strategia selectată este evaluată pe aceeași hartă și aceleași metrici.'}</p>
          <p>{comparison || compactContext}</p>
        </div>
        {expanded ? (
          <div className="expanded-explanation">
            <div>
              <strong>1. Ce face algoritmul?</strong>
              <p>{detailedAlgorithmExplanation(config)}</p>
            </div>
            <div>
              <strong>2. Cum citim traseul?</strong>
              <p>{detailedEpisodeExplanation(result)}</p>
            </div>
            <div>
              <strong>3. Ce înseamnă metricile?</strong>
              <p>{detailedMetricsExplanation()}</p>
            </div>
            <div>
              <strong>4. Cum citim comparația?</strong>
              <p>{detailedComparisonExplanation(monteCarlo)}</p>
            </div>
          </div>
        ) : null}
        <button
          type="button"
          className="education-toggle"
          onClick={() => setExpanded((value) => !value)}
          aria-expanded={expanded}
        >
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
          {expanded ? 'Ascunde explicația' : 'Vezi explicația completă'}
        </button>
      </section>
    );
  }

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
