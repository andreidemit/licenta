import { useEffect, useState } from 'react';
import { CheckCircle2, MousePointer2, Save, RefreshCw } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input, Label } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { GridCanvas } from '../features/grid/GridCanvas';
import { GridLegend } from '../features/grid/GridLegend';
import { useStoredEnvironments } from '../hooks/useRunsApi';
import { api } from '../lib/api';
import { cellColors, cellDescriptions, cellLabels, paintTools } from '../lib/formatters';
import type { EnvironmentPayload, GridPayload } from '../lib/types';
import { cn } from '../lib/cn';
import { Tooltip, TooltipContent, TooltipTrigger } from '../components/ui/tooltip';

function fromGrid(p: GridPayload, name = 'Mediu personalizat'): EnvironmentPayload {
  return {
    id: p.id ?? 'custom_preview',
    name: p.name ?? name,
    rows: p.rows,
    cols: p.cols,
    start: p.start,
    target: p.target,
    grid: p.grid,
  };
}

export function BuilderPage() {
  const [env, setEnv] = useState<EnvironmentPayload>();
  const [tool, setTool] = useState(1);
  const [seed, setSeed] = useState(42);
  const [scenario, setScenario] = useState('B');
  const [message, setMessage] = useState('Editează harta, apoi valideaz-o înainte de evaluare.');
  const [bfs, setBfs] = useState<number | null>(null);
  const { items: stored, reload } = useStoredEnvironments();

  useEffect(() => {
    api
      .previewEnvironment({ scenario, rows: 20, cols: 20, seed })
      .then((p) => {
        setEnv(fromGrid(p, 'Mediu de previzualizare'));
        setBfs(p.bfs_distance);
      })
      .catch(() => undefined);
  }, [scenario, seed]);

  const paint = (r: number, c: number) => {
    if (!env) return;
    const next = env.grid.map((row) => [...row]);
    if (tool === 6) {
      next[env.start[0]][env.start[1]] = 0;
      next[r][c] = 6;
      setEnv({ ...env, start: [r, c], grid: next });
      return;
    }
    if (tool === 5) {
      next[env.target[0]][env.target[1]] = 0;
      next[r][c] = 5;
      setEnv({ ...env, target: [r, c], grid: next });
      return;
    }
    const isStart = env.start[0] === r && env.start[1] === c;
    const isTarget = env.target[0] === r && env.target[1] === c;
    if (isStart || isTarget) {
      setMessage('Mută startul/ținta înainte de a revopsi acea celulă.');
      return;
    }
    next[r][c] = tool;
    setEnv({ ...env, grid: next });
  };

  const validate = async () => {
    if (!env) return;
    try {
      const res = await api.validateEnvironment(env);
      setBfs(res.environment.bfs_distance);
      setMessage(`Hartă validă. Drum BFS optim: ${res.environment.bfs_distance ?? 'indisponibil'} pași.`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Mediul nu este valid.');
    }
  };

  const save = async () => {
    if (!env) return;
    try {
      const res = await api.saveEnvironment(env);
      setMessage(`Salvat ca ${res.environment.id}.`);
      reload();
    } catch (e) {
      setMessage(e instanceof Error ? e.message : 'Salvare eșuată.');
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Construiește un mediu"
        title="Editor de hărți"
        description="Pornește de la o hartă procedurală, modifică celule cu unealta selectată, apoi validează drumul start→țintă cu BFS."
      />

      <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)_280px]">
        {/* Tools */}
        <div className="space-y-3">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Unelte de pictat</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-2">
              {paintTools.map((t) => (
                <Tooltip key={t} delayDuration={200}>
                  <TooltipTrigger asChild>
                    <button
                      type="button"
                      onClick={() => setTool(t)}
                      className={cn(
                        'flex items-center gap-2 rounded-lg border px-2.5 py-2 text-xs transition-all',
                        tool === t
                          ? 'border-accent bg-accent/10 text-ink shadow-glow'
                          : 'border-border/60 bg-elevated/60 text-ink-muted hover:text-ink',
                      )}
                    >
                      <span
                        className="h-3 w-3 rounded-sm"
                        style={{ backgroundColor: cellColors[t] }}
                      />
                      {cellLabels[t]}
                    </button>
                  </TooltipTrigger>
                  <TooltipContent>{cellDescriptions[t]}</TooltipContent>
                </Tooltip>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm">Generare hartă</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <Label>Scenariu sursă</Label>
                <select
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  className="input"
                >
                  <option value="A">A · Navigare</option>
                  <option value="B">B · Supraviețuire</option>
                  <option value="C">C · Hartă dinamică</option>
                </select>
              </div>
              <div>
                <Label>Sămânță</Label>
                <Input
                  type="number"
                  value={seed}
                  onChange={(e) => setSeed(Number(e.target.value))}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Canvas */}
        <div className="space-y-3">
          <GridCanvas
            grid={env}
            editable
            selectedTool={tool}
            onCellClick={paint}
            showCoords
          />
          <GridLegend />
          <Card>
            <CardContent className="flex flex-wrap items-center gap-3 py-3 text-sm">
              <Badge variant="info">{message}</Badge>
              {bfs != null ? <Badge variant="success">BFS {bfs}</Badge> : null}
              <div className="ml-auto flex items-center gap-2">
                <Button variant="secondary" size="sm" onClick={validate}>
                  <MousePointer2 size={14} /> Validează
                </Button>
                <Button onClick={save} size="sm">
                  <Save size={14} /> Salvează
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stored */}
        <div>
          <Card>
            <CardHeader className="pb-2 flex-row items-center justify-between">
              <CardTitle className="text-sm">Hărți salvate</CardTitle>
              <button onClick={reload} className="text-ink-muted hover:text-ink" aria-label="Reîncarcă">
                <RefreshCw size={14} />
              </button>
            </CardHeader>
            <CardContent className="space-y-2">
              {stored.length === 0 ? (
                <p className="text-xs text-ink-muted">Nicio hartă personalizată salvată încă.</p>
              ) : (
                stored.map((s) => (
                  <button
                    key={s.id}
                    onClick={async () => {
                      const p = await api.getEnvironment(s.id);
                      setEnv(fromGrid(p, p.name ?? s.name));
                      setBfs(p.bfs_distance);
                      setMessage(`Hartă ${s.name} încărcată.`);
                    }}
                    className="w-full rounded-lg border border-border/60 bg-elevated/40 p-2 text-left hover:border-accent/40 hover:bg-elevated/60 transition-all"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm text-ink truncate">{s.name}</span>
                      <Badge>
                        {s.rows}×{s.cols}
                      </Badge>
                    </div>
                    {s.bfs_distance != null ? (
                      <p className="mt-1 flex items-center gap-1 text-[10px] text-ink-subtle">
                        <CheckCircle2 size={10} /> BFS {s.bfs_distance}
                      </p>
                    ) : null}
                  </button>
                ))
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
