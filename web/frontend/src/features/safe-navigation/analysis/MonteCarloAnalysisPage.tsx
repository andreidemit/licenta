import { ArrowLeft, BarChart3, BookOpen } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import * as Tabs from '@radix-ui/react-tabs';
import '../../../styles.css';
import { useLatestMonteCarlo } from '../monteCarloStore';
import { algorithmLabel } from './analysisHelpers';
import { ExportPanel } from './ExportPanel';
import { FailureBreakdown } from './FailureBreakdown';
import { MetricCIBars } from './MetricCIBars';
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

  const headline = useMemo(() => {
    if (!result) return null;
    return {
      total: result.summary.episode_count,
      agents: result.summary.agents.length,
      profile: result.profile?.label ?? 'profil necunoscut',
    };
  }, [result]);

  if (!result) {
    return (
      <div className="mc-page">
        <header className="mc-page__topbar">
          <div>
            <p className="eyebrow"><BarChart3 size={14} /> Analiză Monte Carlo</p>
            <h1 className="mc-page__title">Niciun rezultat disponibil</h1>
          </div>
          <Link to="/" className="secondary-button" style={{ width: 'auto' }}>
            <ArrowLeft size={16} /> Înapoi la simulator
          </Link>
        </header>
        <section className="mc-page__empty">
          <p>
            Pornește o comparație Monte Carlo din pagina principală a simulatorului. După ce rulezi
            butonul <em>„Compară Monte Carlo"</em>, revino aici pentru analiza statistică detaliată.
          </p>
          <Link to="/" className="primary-button" style={{ width: 'auto' }}>
            <ArrowLeft size={16} /> Mergi la simulator
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="mc-page">
      <header className="mc-page__topbar">
        <div>
          <p className="eyebrow"><BarChart3 size={14} /> Analiză Monte Carlo</p>
          <h1 className="mc-page__title">Rezultate detaliate pe {headline?.total} episoade</h1>
          <p className="mc-page__subtitle">
            {headline?.agents} agenți · profil <strong>{headline?.profile}</strong>. Folosește tab-urile
            pentru distribuții, intervale de încredere și comportament per-hartă.
          </p>
        </div>
        <Link to="/" className="secondary-button" style={{ width: 'auto' }}>
          <ArrowLeft size={16} /> Înapoi la simulator
        </Link>
      </header>

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
    </div>
  );
}

export default MonteCarloAnalysisPage;
