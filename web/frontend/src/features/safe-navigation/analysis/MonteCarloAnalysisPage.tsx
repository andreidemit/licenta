import { ArrowLeft, BarChart3, BookOpen } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import * as Tabs from '@radix-ui/react-tabs';
import '../../../styles.css';
import { safeNavigationApi, type MonteCarloRawRequest } from '../api';
import { AiAnalystPanel } from '../AiAnalystPanel';
import { setLatestMonteCarlo, useLatestMonteCarlo } from '../monteCarloStore';
import { RecommendationPanel } from '../RecommendationPanel';
import { algorithmLabel } from './analysisHelpers';
import { ExportPanel } from './ExportPanel';
import { FailureBreakdown } from './FailureBreakdown';
import { MetricCIBars } from './MetricCIBars';
import { MonteCarloConfigurator, DEFAULT_MC_PAYLOAD } from './MonteCarloConfigurator';
import { OccupancyHeatmap } from './OccupancyHeatmap';
import { PerMapHeatmap } from './PerMapHeatmap';
import { RewardDistribution } from './RewardDistribution';
import { RiskRewardScatter } from './RiskRewardScatter';

const TABS = [
  { id: 'distributions', label: 'Distribuții' },
  { id: 'ci-bars', label: 'Intervale de încredere' },
  { id: 'pareto', label: 'Risc / Recompensă' },
  { id: 'per-map', label: 'Per-hartă' },
  { id: 'failures', label: 'Eșecuri' },
  { id: 'occupancy', label: 'Ocupare grilă' },
  { id: 'export', label: 'Export' },
];

export function MonteCarloAnalysisPage() {
  const result = useLatestMonteCarlo();
  const [tab, setTab] = useState<string>(TABS[0].id);
  const [payload, setPayload] = useState<MonteCarloRawRequest>(() => ({ ...DEFAULT_MC_PAYLOAD }));
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | undefined>();
  const [error, setError] = useState<string | undefined>();

  const headline = useMemo(() => {
    if (!result) return null;
    return {
      total: result.summary.episode_count,
      agents: result.summary.agents.length,
      profile: result.profile?.label ?? 'profil necunoscut',
    };
  }, [result]);

  const runExperiment = useCallback(async () => {
    setBusy(true);
    setError(undefined);
    setMessage(undefined);
    try {
      const response = await safeNavigationApi.monteCarloRaw(payload);
      setLatestMonteCarlo(response);
      setMessage(`Au fost agregate ${response.summary.episode_count} episoade pe ${response.summary.agents.length} agenți.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Comparația Monte Carlo a eșuat.');
    } finally {
      setBusy(false);
    }
  }, [payload]);

  return (
    <div className="mc-page">
      <header className="mc-page__topbar">
        <div>
          <p className="eyebrow"><BarChart3 size={14} /> Experiment Monte Carlo</p>
          <h1 className="mc-page__title">
            {headline
              ? `Rezultate detaliate pe ${headline.total} episoade`
              : 'Configurează experimentul și rulează Monte Carlo'}
          </h1>
          {headline && (
            <p className="mc-page__subtitle">
              {headline.agents} agenți · profil <strong>{headline.profile}</strong>. Folosește tab-urile
              pentru distribuții, intervale de încredere și comportament per-hartă.
            </p>
          )}
        </div>
        <Link to="/lab" className="secondary-button" style={{ width: 'auto' }}>
          <ArrowLeft size={16} /> Laborator Q-Learning
        </Link>
      </header>

      <MonteCarloConfigurator
        payload={payload}
        onChange={setPayload}
        onRun={runExperiment}
        busy={busy}
        error={error}
        message={message}
      />

      {result ? (
        <>
          <section className="mc-page__legend">
            <BookOpen size={18} />
            <div>
              <strong>Cum se citește această pagină</strong>
              <div>
                Fiecare metrică este însoțită de variabilitatea ei. Dacă două bare au intervalele
                de încredere suprapuse, diferența între agenți nu este semnificativă statistic la 95%
                și concluzia trebuie nuanțată în consecință.
              </div>
            </div>
          </section>

          <RecommendationPanel
            result={result}
            selectedObjective={payload.optimization_objective}
            onObjectiveChange={(objective) => setPayload((current) => ({ ...current, optimization_objective: objective }))}
          />

          <AiAnalystPanel result={result} autoTrigger />

          <Tabs.Root value={tab} onValueChange={setTab}>
            <Tabs.List className="mc-page__tabs">
              {TABS.map((entry) => (
                <Tabs.Trigger key={entry.id} value={entry.id} className="mc-tab">
                  {entry.label}
                </Tabs.Trigger>
              ))}
            </Tabs.List>
            <div style={{ marginTop: 12 }}>
              <Tabs.Content value="distributions"><RewardDistribution result={result} /></Tabs.Content>
              <Tabs.Content value="ci-bars"><MetricCIBars result={result} /></Tabs.Content>
              <Tabs.Content value="pareto"><RiskRewardScatter result={result} /></Tabs.Content>
              <Tabs.Content value="per-map"><PerMapHeatmap result={result} /></Tabs.Content>
              <Tabs.Content value="failures"><FailureBreakdown result={result} /></Tabs.Content>
              <Tabs.Content value="occupancy"><OccupancyHeatmap result={result} /></Tabs.Content>
              <Tabs.Content value="export"><ExportPanel result={result} /></Tabs.Content>
            </div>
          </Tabs.Root>

          <footer className="mc-page__footer">
            Agenți incluși: {result.summary.agents.map((row) => algorithmLabel(row.algorithm)).join(' · ')}
          </footer>
        </>
      ) : (
        <section className="mc-page__empty">
          <strong>Niciun rezultat încă.</strong>
          <p>
            Configurează parametrii de mai sus și apasă <em>„Rulează Monte Carlo"</em>. Acesta este
            fluxul principal de experimentare: compară strategiile pe mai multe hărți și episoade,
            apoi afișează analiza statistică dedesubt.
          </p>
        </section>
      )}
    </div>
  );
}

export default MonteCarloAnalysisPage;
