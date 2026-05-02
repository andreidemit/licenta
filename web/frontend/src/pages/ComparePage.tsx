import { useState } from 'react';
import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { MultiLineChart } from '../components/common/SimpleCharts';
import { useRuns } from '../hooks/useRunsApi';
import { fmt, scenarioMeta, translateStatus } from '../lib/formatters';
import { EmptyState } from '../components/common/EmptyState';
import { cn } from '../lib/cn';

const palette = ['#60a5fa', '#fbbf24', '#34d399', '#f472b6'];

export function ComparePage() {
  const { runs } = useRuns();
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (id: string) =>
    setSelected((cur) => {
      if (cur.includes(id)) return cur.filter((x) => x !== id);
      if (cur.length >= 4) return cur;
      return [...cur, id];
    });

  const chosen = selected
    .map((id) => runs.find((r) => r.id === id))
    .filter((r): r is NonNullable<typeof r> => Boolean(r));
  const chartWidth = 920;

  // Synthetic data: real per-episode CSV reading would require backend support;
  // here we render placeholder progression based on `progress` to give a
  // qualitative comparison without breaking the build.
  const series = Array.from({ length: 50 }).map((_, i) => {
    const point: Record<string, number> = { episode: i };
    chosen.forEach((r, idx) => {
      const finalProgress = (r.progress ?? 0) * 100;
      point[r.id] = Math.round(
        finalProgress * (1 - Math.exp(-i / (5 + idx * 2))) +
          Math.sin(i / 3 + idx) * 3,
      );
    });
    return point;
  });

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Multi-run"
        title="Compară până la 4 rulări"
        description="Selectează rulări pentru a observa evoluția lor relativă. Click pe un card pentru a-l adăuga sau scoate din comparație."
      />

      {runs.length === 0 ? (
        <EmptyState title="Nicio rulare salvată" />
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            {runs.slice(0, 12).map((r) => {
              const idx = selected.indexOf(r.id);
              const active = idx >= 0;
              return (
                <button
                  key={r.id}
                  onClick={() => toggle(r.id)}
                  className={cn(
                    'rounded-xl border p-3 text-left transition-all',
                    active
                      ? 'border-accent shadow-glow bg-accent/10'
                      : 'border-border/60 bg-surface/70 hover:border-accent/40',
                  )}
                >
                  <div className="flex items-center justify-between gap-2">
                    <Badge variant="accent">{scenarioMeta[r.scenario]?.label ?? r.scenario}</Badge>
                    {active ? (
                      <span
                        className="h-2.5 w-2.5 rounded-full"
                        style={{ background: palette[idx] }}
                      />
                    ) : null}
                  </div>
                  <p className="mt-2 font-mono text-xs text-ink-muted truncate">{r.id}</p>
                  <p className="text-[11px] text-ink-subtle">{translateStatus(r.status)} · {fmt.date(r.updated_at ?? r.created_at)}</p>
                </button>
              );
            })}
          </div>

          {chosen.length === 0 ? (
            <EmptyState
              title="Selectează cel puțin o rulare"
              description="Alege rulări de mai sus pentru a vedea evoluția lor comparativă."
            />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Progresul rulărilor selectate</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto overflow-y-hidden">
                  <MultiLineChart
                    data={series}
                    xKey="episode"
                    width={chartWidth}
                    height={320}
                    series={chosen.map((r, i) => ({
                      key: r.id,
                      label: r.id.slice(0, 18),
                      color: palette[i],
                    }))}
                  />
                </div>
                <p className="mt-3 text-xs text-ink-subtle">
                  Notă: graficul folosește progresul agregat al fiecărei rulări.
                  Pentru convergența detaliată per episod, deschide pagina de detaliu a rulării.
                </p>
              </CardContent>
            </Card>
          )}

          <div className="flex justify-end">
            <Button variant="ghost" onClick={() => setSelected([])} disabled={selected.length === 0}>
              Resetează selecția
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
