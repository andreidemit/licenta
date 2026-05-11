import { Activity, AlertTriangle, CheckCircle2, Gauge, Route } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../components/ui/tooltip';
import type { MonteCarloResult, SafeEnvironment, SafeEpisodeResult, SafeNavigationConfig } from './types';

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

function pct(value: number) {
  return `${Math.round(value * 100)}%`;
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

const metricTooltips = {
  steps: 'Câte acțiuni a executat agentul până la finalul episodului. Un număr mai mic înseamnă de obicei un traseu mai eficient.',
  reward: 'Scorul primit din funcția de recompensă. Obiectivul crește scorul, iar pașii, riscul, coliziunile și eșecurile îl scad.',
  risk: 'Suma expunerii la risc acumulată pe traseu. Crește când agentul intră în pericol sau se apropie de zone periculoase.',
  collisions: 'De câte ori agentul a încercat să intre într-un perete sau obstacol. Coliziunile indică decizii nesigure sau explorare slabă.',
  danger: 'De câte ori agentul a intrat într-o celulă periculoasă. Pentru navigare sigură, valoarea ideală este 0.',
  cost: 'Costul total agregat al traseului. Ajută la compararea eficienței cu siguranța: un cost mai mic este mai bun.',
};

function MetricTile({
  label,
  value,
  tooltip,
}: {
  label: string;
  value: string | number;
  tooltip: string;
}) {
  return (
    <Tooltip delayDuration={120}>
      <TooltipTrigger asChild>
        <div className="metric-tooltip-trigger" tabIndex={0} aria-label={`${label}: ${tooltip}`}>
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      </TooltipTrigger>
      <TooltipContent side="top" align="center" className="safe-metric-tooltip">
        {tooltip}
      </TooltipContent>
    </Tooltip>
  );
}

function buildStory({
  config,
  environment,
  result,
  monteCarlo,
}: {
  config: SafeNavigationConfig;
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
}) {
  const story = [];
  const label = algorithmLabel(config.algorithm);
  if (!result) {
    story.push({
      icon: Gauge,
      text: `${label} este selectat. Generează o hartă sau rulează un episod pentru a observa comportamentul strategiei.`,
    });
    story.push({
      icon: AlertTriangle,
      text: `Mediul folosește scenariul ${scenarioLabel(config.scenario)}, zgomot de mișcare ${config.movement_noise} și pondere de risc ${config.risk_weight}.`,
    });
  } else {
    const status = result.success ? 'a ajuns la obiectiv' : result.timeout ? 'a depășit limita de pași' : 's-a oprit fără succes';
    story.push({
      icon: result.success ? CheckCircle2 : AlertTriangle,
      text: `${label} ${status} după ${result.steps} pași, cu recompensă ${fmt(result.total_reward)} și expunere la risc ${fmt(result.total_risk_exposure)}.`,
    });
    if (environment) {
      const [sr, sc] = environment.start;
      const [gr, gc] = environment.goal;
      const manhattan = Math.abs(sr - gr) + Math.abs(sc - gc);
      story.push({
        icon: Route,
        text: `Distanța Manhattan directă este ${manhattan}; lungimea traseului este ${result.path_length}, iar diferența indică ocoliri cauzate de obstacole sau risc.`,
      });
    }
    if (result.collisions || result.danger_entries) {
      story.push({
        icon: AlertTriangle,
        text: `Evenimente de siguranță: ${result.collisions} coliziuni și ${result.danger_entries} intrări în pericol.`,
      });
    } else {
      story.push({
        icon: CheckCircle2,
        text: 'Episodul nu a avut coliziuni și nici intrări în celule periculoase.',
      });
    }
  }

  if (monteCarlo?.summary.agents.length) {
    const bestSuccess = [...monteCarlo.summary.agents].sort((a, b) => b.success_rate - a.success_rate)[0];
    const lowestRisk = [...monteCarlo.summary.agents].sort((a, b) => a.average_risk_exposure - b.average_risk_exposure)[0];
    story.push({
      icon: Activity,
      text: `Monte Carlo a comparat ${monteCarlo.summary.episode_count} episoade: cea mai bună rată de succes este ${algorithmLabel(bestSuccess.algorithm)}, cu ${pct(bestSuccess.success_rate)}.`,
    });
    story.push({
      icon: Gauge,
      text: `Cea mai mică expunere medie la risc este ${algorithmLabel(lowestRisk.algorithm)}, cu ${fmt(lowestRisk.average_risk_exposure)}.`,
    });
  }

  return story.slice(0, 4);
}

export function MetricsPanel({
  config,
  environment,
  result,
  monteCarlo,
  compact = false,
  showStory = true,
}: {
  config: SafeNavigationConfig;
  environment?: SafeEnvironment;
  result?: SafeEpisodeResult;
  monteCarlo?: MonteCarloResult;
  compact?: boolean;
  showStory?: boolean;
}) {
  const statusKey = result ? (result.success ? 'success' : result.timeout ? 'timeout' : 'failed') : 'ready';
  const statusLabel = result ? (result.success ? 'Succes' : result.timeout ? 'Timeout' : 'Eșec') : 'Gata';
  const story = buildStory({ config, environment, result, monteCarlo });
  return (
    <aside className={compact ? 'metrics-panel compact-metrics' : 'metrics-panel'}>
      <section className="panel-card run-summary-card">
        <div>
          <small>Algoritm curent</small>
          <strong>{algorithmLabel(config.algorithm)}</strong>
        </div>
        <b className={`badge ${statusKey}`}>{statusLabel}</b>
        <dl>
          {compact ? (
            <>
              <MetricTile label="Pași" value={result?.steps ?? '-'} tooltip={metricTooltips.steps} />
              <MetricTile label="Recompensă" value={fmt(result?.total_reward)} tooltip={metricTooltips.reward} />
              <MetricTile label="Risc" value={fmt(result?.total_risk_exposure)} tooltip={metricTooltips.risk} />
            </>
          ) : (
            <>
              <div><dt>Pași</dt><dd>{result?.steps ?? '-'}</dd></div>
              <div><dt>Recompensă</dt><dd>{fmt(result?.total_reward)}</dd></div>
              <div><dt>Risc</dt><dd>{fmt(result?.total_risk_exposure)}</dd></div>
            </>
          )}
          {compact ? (
            <>
              <MetricTile label="Coliziuni" value={result?.collisions ?? '-'} tooltip={metricTooltips.collisions} />
              <MetricTile label="Pericol" value={result?.danger_entries ?? '-'} tooltip={metricTooltips.danger} />
              <MetricTile label="Cost" value={fmt(result?.total_cost)} tooltip={metricTooltips.cost} />
            </>
          ) : null}
        </dl>
      </section>

      {showStory ? (
        <section className="panel-card story-card">
          <h2><Route size={18} /> Poveste experimentală</h2>
          {story.map(({ icon: Icon, text }) => (
            <p key={text}><Icon size={15} /> {text}</p>
          ))}
        </section>
      ) : null}

      {!compact ? (
        <section className="panel-card live-metrics-card">
          <h2><Activity size={18} /> Metrici live</h2>
          <div className="status-row">
            <span>{algorithmLabel(config.algorithm)}</span>
            <b className={`badge ${statusKey}`}>{statusLabel}</b>
          </div>
          <div className="metric-grid">
            <div><small>Pași</small><strong>{result?.steps ?? '-'}</strong></div>
            <div><small>Recompensă totală</small><strong>{fmt(result?.total_reward)}</strong></div>
            <div><small>Cost total</small><strong>{fmt(result?.total_cost)}</strong></div>
            <div><small>Expunere la risc</small><strong>{fmt(result?.total_risk_exposure)}</strong></div>
            <div><small>Coliziuni</small><strong>{result?.collisions ?? '-'}</strong></div>
            <div><small>Intrări în pericol</small><strong>{result?.danger_entries ?? '-'}</strong></div>
            <div><small>Lungime traseu</small><strong>{result?.path_length ?? '-'}</strong></div>
            <div><small>Timp rulare</small><strong>{fmt(result?.computation_time_ms, 2)} ms</strong></div>
          </div>
        </section>
      ) : null}
    </aside>
  );
}
