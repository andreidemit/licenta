import { BarChart3 } from 'lucide-react';
import type { MonteCarloResult, MonteCarloSummaryRow } from './types';
import { algorithmUseCases, getExperimentProfile } from './experimentProfiles';

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
}

function num(value: number) {
  return value.toFixed(1);
}

function algorithmLabel(value: string) {
  const labels: Record<string, string> = {
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
  };
  return labels[value] ?? value;
}

function algorithmKey(value: string) {
  const keys: Record<string, string> = {
    Random: 'random',
    'Rule-Based': 'rule_based',
    'Risk-Aware A*': 'risk_aware_astar',
    'Tabular Q-Learning': 'tabular_q',
    'Feature-Based Q-Learning': 'feature_q',
  };
  return keys[value] ?? value;
}

function useCaseFor(value: string) {
  return algorithmUseCases[algorithmKey(value)] ?? 'Folosit ca reper în comparația cu celelalte strategii.';
}

function profileTakeaway(profile: NonNullable<MonteCarloResult['profile']> | ReturnType<typeof getExperimentProfile>) {
  return 'expected_takeaway' in profile ? profile.expected_takeaway : profile.expectedTakeaway;
}

function buildOverallComment(rows: MonteCarloSummaryRow[]) {
  if (!rows.length) return 'Nu există încă suficiente rezultate pentru interpretare.';
  const bestBySuccess = rows[0];
  const safest = [...rows].sort((a, b) => a.average_risk_exposure - b.average_risk_exposure)[0];
  const fastest = [...rows].sort((a, b) => a.average_steps - b.average_steps)[0];
  const bestLabel = algorithmLabel(bestBySuccess.algorithm);
  const safestLabel = algorithmLabel(safest.algorithm);
  const fastestLabel = algorithmLabel(fastest.algorithm);

  if (bestBySuccess.algorithm === safest.algorithm) {
    return `${bestLabel} este cea mai echilibrată strategie în această rulare: are cea mai mare rată de succes și cea mai mică expunere la risc.`;
  }
  if (bestBySuccess.algorithm === fastest.algorithm) {
    return `${bestLabel} ajunge cel mai des la obiectiv și are traseele cele mai scurte, dar ${safestLabel} este mai prudent din perspectiva riscului.`;
  }
  return `${bestLabel} conduce la rata de succes, ${safestLabel} minimizează riscul, iar ${fastestLabel} produce cele mai scurte trasee.`;
}

function buildProfileConclusion(result: MonteCarloResult, rows: MonteCarloSummaryRow[]) {
  const profile = result.profile ?? getExperimentProfile(String(result.config.experiment_profile));
  const bestBySuccess = rows[0];
  const safest = [...rows].sort((a, b) => a.average_risk_exposure - b.average_risk_exposure)[0];
  const fastest = [...rows].sort((a, b) => a.average_steps - b.average_steps)[0];
  const robust = [...rows].sort((a, b) => {
    const unsafeA = a.collision_rate + a.danger_entry_rate + a.timeout_rate;
    const unsafeB = b.collision_rate + b.danger_entry_rate + b.timeout_rate;
    if (unsafeA !== unsafeB) return unsafeA - unsafeB;
    return b.success_rate - a.success_rate;
  })[0];
  return {
    profile,
    text: `${profileTakeaway(profile)} În această rulare: ${algorithmLabel(bestBySuccess.algorithm)} conduce la succes, ${algorithmLabel(safest.algorithm)} minimizează riscul, ${algorithmLabel(fastest.algorithm)} are cele mai scurte trasee, iar ${algorithmLabel(robust.algorithm)} are cel mai stabil profil operațional.`,
  };
}

function buildRowComment(row: MonteCarloSummaryRow, rows: MonteCarloSummaryRow[]) {
  const key = algorithmKey(row.algorithm);
  const bestSuccess = Math.max(...rows.map((item) => item.success_rate));
  const bestRisk = Math.min(...rows.map((item) => item.average_risk_exposure));
  const bestSteps = Math.min(...rows.map((item) => item.average_steps));
  const highRisk = row.average_risk_exposure > bestRisk * 1.35 && row.average_risk_exposure > 0;
  const slow = row.average_steps > bestSteps * 1.35;
  const unsafeEvents = row.average_collisions > 0.25 || row.average_danger_entries > 0.25;

  if (row.success_rate === bestSuccess && row.average_risk_exposure === bestRisk) {
    return 'Cea mai bună combinație între succes și siguranță.';
  }
  if (row.success_rate === bestSuccess) {
    return highRisk ? 'Foarte eficient, dar plătește prin expunere mai mare la risc.' : 'Rată de succes foarte bună pe hărțile generate.';
  }
  if (row.average_risk_exposure === bestRisk) {
    return slow ? 'Cel mai prudent, dar traseele sunt mai lungi.' : 'Cel mai sigur profil de risc în această comparație.';
  }
  if (row.timeout_rate > 0.25) {
    return 'Are dificultăți de finalizare; timeout-ul sugerează blocaje sau explorare slabă.';
  }
  if (unsafeEvents) {
    return 'Produce evenimente de siguranță; merită analizate coliziunile și intrările în pericol.';
  }
  if (key === 'tabular_q') {
    return 'Reflectă limitarea Q-Learning-ului tabular: coordonatele învățate transferă greu pe hărți noi.';
  }
  if (key === 'feature_q') {
    return 'Folosește tipare locale; rezultatul indică cât de bine se transferă aceste trăsături.';
  }
  if (key === 'astar' && highRisk) {
    return 'Planifică eficient, dar riscul nu este obiectivul principal al rutei.';
  }
  if (key === 'risk_aware_astar') {
    return 'Preferă trasee mai sigure, chiar dacă uneori acceptă pași suplimentari.';
  }
  if (row.success_rate < 0.35) {
    return 'Baseline slab pentru acest scenariu; mediul este dificil fără planificare robustă.';
  }
  return 'Performanță intermediară; util ca reper în comparația cu strategiile de top.';
}

export function ExperimentDashboard({ result, busy = false }: { result?: MonteCarloResult; busy?: boolean }) {
  if (busy) {
    return (
      <section className="panel-card comparison-dashboard dashboard-loading">
        <h2><BarChart3 size={18} /> Dashboard comparativ</h2>
        <p className="dashboard-caption">
          Monte Carlo rulează pe hărți generate. Poate dura câteva secunde când sunt incluși agenți care învață.
        </p>
        <div className="loading-row"><i /> Se compară agenții...</div>
      </section>
    );
  }

  if (!result) {
    return (
      <section className="panel-card comparison-dashboard">
        <h2><BarChart3 size={18} /> Dashboard comparativ</h2>
        <p className="muted">Rulează comparația Monte Carlo pentru a vedea metrici statistice pe hărți generate.</p>
      </section>
    );
  }

  const sortedRows = [...result.summary.agents].sort((a, b) => {
    if (b.success_rate !== a.success_rate) return b.success_rate - a.success_rate;
    return a.average_risk_exposure - b.average_risk_exposure;
  });
  const overallComment = buildOverallComment(sortedRows);
  const profileConclusion = buildProfileConclusion(result, sortedRows);
  const maxRisk = Math.max(1, ...sortedRows.map((row) => row.average_risk_exposure));
  const bestSuccess = Math.max(...sortedRows.map((row) => row.success_rate));
  const bestRisk = Math.min(...sortedRows.map((row) => row.average_risk_exposure));
  const bestSteps = Math.min(...sortedRows.map((row) => row.average_steps));
  return (
    <section className="panel-card comparison-dashboard">
      <h2><BarChart3 size={18} /> Dashboard comparativ</h2>
      <p className="dashboard-caption">
        Monte Carlo compară fiecare agent pe hărți generate și rezumă succesul, eficiența traseului și expunerea la risc.
      </p>
      <div className="comparison-insight">
        <strong>Concluzie experimentală: {profileConclusion.profile.label}</strong>
        <span>{profileConclusion.text}</span>
      </div>
      <div className="comparison-insight secondary-insight">
        <strong>Comentariu numeric</strong>
        <span>{overallComment}</span>
      </div>
      <div className="comparison-table">
        <div className="table-head">
          <span>Algoritm</span><span>Succes</span><span>Pași</span><span>Risc</span><span>Recompensă</span>
        </div>
        {sortedRows.map((row) => (
          <div className="table-row" key={row.algorithm}>
            <div className="algorithm-cell">
              <strong>{algorithmLabel(row.algorithm)}</strong>
              <small>{buildRowComment(row, sortedRows)}</small>
              <em>{useCaseFor(row.algorithm)}</em>
            </div>
            <span className={row.success_rate === bestSuccess ? 'winner-cell' : ''}>{pct(row.success_rate)}</span>
            <span className={row.average_steps === bestSteps ? 'winner-cell' : ''}>{num(row.average_steps)}</span>
            <span className={row.average_risk_exposure === bestRisk ? 'winner-cell' : ''}>{num(row.average_risk_exposure)}</span>
            <span>{num(row.average_reward)}</span>
          </div>
        ))}
      </div>
      <div className="bar-list">
        {sortedRows.map((row) => (
          <div key={row.algorithm}>
            <label><span>{algorithmLabel(row.algorithm)} - succes</span><b>{pct(row.success_rate)}</b></label>
            <div className="bar"><i style={{ width: `${row.success_rate * 100}%` }} /></div>
          </div>
        ))}
        {sortedRows.map((row) => (
          <div key={`${row.algorithm}-risk`}>
            <label><span>{algorithmLabel(row.algorithm)} - expunere la risc</span><b>{num(row.average_risk_exposure)}</b></label>
            <div className="bar risk"><i style={{ width: `${(row.average_risk_exposure / maxRisk) * 100}%` }} /></div>
          </div>
        ))}
      </div>
    </section>
  );
}
