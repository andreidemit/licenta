import { Link } from 'react-router-dom';
import { useState } from 'react';
import { LayoutGrid, List, Search } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { useRuns } from '../hooks/useRunsApi';
import { fmt, scenarioMeta, translateStatus } from '../lib/formatters';
import { EmptyState } from '../components/common/EmptyState';
import { cn } from '../lib/cn';

export function RunsPage() {
  const { runs, loading, reload } = useRuns();
  const [view, setView] = useState<'cards' | 'table'>('cards');
  const [filter, setFilter] = useState('');
  const [scenarioFilter, setScenarioFilter] = useState<string>('all');

  const filtered = runs.filter((r) => {
    if (scenarioFilter !== 'all' && r.scenario !== scenarioFilter) return false;
    if (filter && !r.id.toLowerCase().includes(filter.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Istoric"
        title="Rulări de antrenare"
        description="Explorează experimentele anterioare. Click pe o rulare pentru detalii, grafice și artefacte."
        actions={
          <>
            <Button
              variant={view === 'cards' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setView('cards')}
              aria-label="Vizualizare carduri"
            >
              <LayoutGrid size={16} />
            </Button>
            <Button
              variant={view === 'table' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setView('table')}
              aria-label="Vizualizare tabel"
            >
              <List size={16} />
            </Button>
            <Button variant="secondary" size="sm" onClick={reload} disabled={loading}>
              {loading ? 'Reîncarc…' : 'Reîncarcă'}
            </Button>
          </>
        }
      />

      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[220px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-subtle" size={14} />
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Caută după ID rulare…"
            className="pl-9"
          />
        </div>
        <select
          value={scenarioFilter}
          onChange={(e) => setScenarioFilter(e.target.value)}
          className="input max-w-[220px]"
        >
          <option value="all">Toate scenariile</option>
          <option value="A">A · Navigare</option>
          <option value="B">B · Supraviețuire</option>
          <option value="C">C · Hartă dinamică</option>
          <option value="WAREHOUSE">Depozit</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          title="Nicio rulare găsită"
          description='Pornește o antrenare din pagina „Antrenare” pentru a vedea rezultatele aici.'
        />
      ) : view === 'cards' ? (
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {filtered.map((r) => {
            const meta = scenarioMeta[r.scenario];
            return (
              <Link key={r.id} to={`/rulari/${r.id}`}>
                <Card className="h-full hover:-translate-y-0.5 hover:shadow-glow transition-all">
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between gap-2">
                      <Badge variant="accent">{meta?.label ?? r.scenario}</Badge>
                      <Badge
                        variant={
                          r.status === 'completed'
                            ? 'success'
                            : r.status === 'failed'
                            ? 'danger'
                            : r.status === 'running'
                            ? 'info'
                            : 'default'
                        }
                      >
                        {translateStatus(r.status)}
                      </Badge>
                    </div>
                    <p className="font-mono text-xs text-ink-muted truncate">{r.id}</p>
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs text-ink-muted">
                        <span>Progres</span>
                        <span className="font-mono">{Math.round((r.progress ?? 0) * 100)}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-elevated overflow-hidden">
                        <div
                          className={cn(
                            'h-full',
                            r.status === 'completed' ? 'bg-accent-success' : 'bg-accent',
                          )}
                          style={{ width: `${Math.round((r.progress ?? 0) * 100)}%` }}
                        />
                      </div>
                    </div>
                    <p className="text-[11px] text-ink-subtle">
                      {fmt.date(r.updated_at ?? r.created_at)}
                    </p>
                  </CardContent>
                </Card>
              </Link>
            );
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0 overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="text-left text-xs uppercase tracking-wider text-ink-muted">
                <tr className="border-b border-border/60">
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Scenariu</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Progres</th>
                  <th className="px-4 py-3">Actualizat</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-border/30 hover:bg-elevated/40 transition-colors"
                  >
                    <td className="px-4 py-3">
                      <Link to={`/rulari/${r.id}`} className="font-mono text-xs hover:text-accent">
                        {r.id}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant="accent">{scenarioMeta[r.scenario]?.label ?? r.scenario}</Badge>
                    </td>
                    <td className="px-4 py-3">
                      <Badge
                        variant={
                          r.status === 'completed'
                            ? 'success'
                            : r.status === 'failed'
                            ? 'danger'
                            : 'default'
                        }
                      >
                        {translateStatus(r.status)}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">
                      {Math.round((r.progress ?? 0) * 100)}%
                    </td>
                    <td className="px-4 py-3 text-xs text-ink-muted">
                      {fmt.date(r.updated_at ?? r.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
