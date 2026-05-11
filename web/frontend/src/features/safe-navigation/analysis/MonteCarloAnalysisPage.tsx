import { ArrowLeft, BarChart3, BookOpen } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import '../../../styles.css';
import * as Tabs from '@radix-ui/react-tabs';
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

function tabButtonStyle(active: boolean) {
  return {
    padding: '0.55rem 0.95rem',
    borderRadius: 999,
    fontSize: '0.85rem',
    fontWeight: 600,
    border: '1px solid',
    borderColor: active ? 'rgba(56,189,248,0.65)' : 'rgba(148,163,184,0.25)',
    background: active ? 'rgba(56,189,248,0.18)' : 'rgba(15,23,42,0.45)',
    color: active ? '#e0f2fe' : 'rgba(203,213,245,0.8)',
    cursor: 'pointer',
    transition: 'all 120ms ease',
  } as const;
}

export function MonteCarloAnalysisPage() {
  const result = useLatestMonteCarlo();
  const [tab, setTab] = useState(TABS[0].id);

  const headlineNumbers = useMemo(() => {
    if (!result) return null;
    const total = result.summary.episode_count;
    const agents = result.summary.agents.length;
    const profile = result.profile?.label ?? 'profil necunoscut';
    return { total, agents, profile };
  }, [result]);

  if (!result) {
    return (
      <div className="app-shell monte-carlo-analysis" style={{ padding: '2rem' }}>
        <header style={{ marginBottom: '1.5rem' }}>
          <p className="eyebrow">Analiză Monte Carlo</p>
          <h1>Niciun rezultat disponibil</h1>
          <p className="muted">
            Pornește o comparație Monte Carlo din pagina principală, apoi revino aici pentru analiza statistică detaliată.
          </p>
        </header>
        <Link to="/" className="primary-button">
          <ArrowLeft size={16} /> Înapoi la simulator
        </Link>
      </div>
    );
  }

  return (
    <div className="app-shell monte-carlo-analysis" style={{ padding: '1.75rem 2rem 4rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', alignItems: 'flex-end' }}>
        <div>
          <p className="eyebrow"><BarChart3 size={14} /> Analiză Monte Carlo</p>
          <h1 style={{ margin: '0.25rem 0 0.5rem' }}>Rezultate detaliate pe {headlineNumbers?.total} episoade</h1>
          <p className="muted" style={{ maxWidth: 720 }}>
            {headlineNumbers?.agents} agenți · profil <strong>{headlineNumbers?.profile}</strong>.
            Folosește tab-urile pentru distribuții, intervale de încredere și comportament per-hartă.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <Link to="/" className="secondary-button">
            <ArrowLeft size={16} /> Înapoi la simulator
          </Link>
        </div>
      </header>

      <section className="panel-card" style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', alignItems: 'center' }}>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', color: 'rgba(203,213,245,0.95)' }}>
          <BookOpen size={18} />
          <strong>Cum se citește această pagină</strong>
        </div>
        <p style={{ margin: 0, fontSize: '0.88rem', color: 'rgba(203,213,245,0.85)', maxWidth: 720 }}>
          Fiecare metrică este însoțită de variabilitatea ei. Dacă două bare au intervalele
          de încredere suprapuse, diferența între agenți nu este semnificativă statistic
          la nivelul 95% — concluzia trebuie nuanțată în consecință.
        </p>
      </section>

      <Tabs.Root value={tab} onValueChange={setTab}>
        <Tabs.List style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.25rem' }}>
          {TABS.map((entry) => (
            <Tabs.Trigger key={entry.id} value={entry.id} style={tabButtonStyle(tab === entry.id)}>
              {entry.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
        <Tabs.Content value="distributions">
          <RewardDistribution result={result} />
        </Tabs.Content>
        <Tabs.Content value="ci-bars">
          <MetricCIBars result={result} />
        </Tabs.Content>
        <Tabs.Content value="pareto">
          <RiskRewardScatter result={result} />
        </Tabs.Content>
        <Tabs.Content value="per-map">
          <PerMapHeatmap result={result} />
        </Tabs.Content>
        <Tabs.Content value="failures">
          <FailureBreakdown result={result} />
        </Tabs.Content>
        <Tabs.Content value="occupancy">
          <OccupancyHeatmap result={result} />
        </Tabs.Content>
        <Tabs.Content value="export">
          <ExportPanel result={result} />
        </Tabs.Content>
      </Tabs.Root>

      <footer className="muted" style={{ fontSize: '0.78rem', textAlign: 'center' }}>
        Agenți incluși: {result.summary.agents.map((row) => algorithmLabel(row.algorithm)).join(' · ')}
      </footer>
    </div>
  );
}

export default MonteCarloAnalysisPage;
