import { Link, useNavigate, useParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { ArrowLeft, Download, Target } from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { api } from '../lib/api';
import { artifactLabels, fmt, scenarioMeta, translateStatus } from '../lib/formatters';
import type { JobSnapshot } from '../lib/types';
import { EmptyState } from '../components/common/EmptyState';

export function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [run, setRun] = useState<JobSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!runId) return;
    api
      .getRun(runId)
      .then(setRun)
      .catch((e) => setError(e instanceof Error ? e.message : 'Eroare'));
  }, [runId]);

  if (error) {
    return <EmptyState title="Rulare indisponibilă" description={error} />;
  }
  if (!run) {
    return <p className="text-sm text-ink-muted">Se încarcă…</p>;
  }

  const meta = scenarioMeta[run.scenario];
  const artifacts = run.artifacts ?? {};
  const visualKeys = [
    'environment_map_png',
    'q_heatmap_png',
    'policy_png',
    'visits_png',
    'td_error_png',
    'greedy_path_png',
    'convergence_png',
    'epsilon_png',
    'success_png',
  ];
  const fileKeys = ['results_csv', 'qtable_path', 'manifest_json', 'greedy_trajectory_csv', 'greedy_trajectory_json'];

  return (
    <div className="space-y-6">
      <Button variant="ghost" size="sm" asChild>
        <Link to="/rulari">
          <ArrowLeft size={14} /> Înapoi la rulări
        </Link>
      </Button>

      <PageHeader
        eyebrow="Detalii rulare"
        title={run.id}
        description={run.message}
        actions={
          <>
            {artifacts.qtable_path ? (
              <Button onClick={() => navigate('/evaluare')}>
                <Target size={16} /> Folosește pentru evaluare
              </Button>
            ) : null}
          </>
        }
      />

      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="accent">{meta?.label ?? run.scenario}</Badge>
        <Badge
          variant={
            run.status === 'completed'
              ? 'success'
              : run.status === 'failed'
              ? 'danger'
              : 'default'
          }
        >
          {translateStatus(run.status)}
        </Badge>
        <span className="text-xs text-ink-subtle">
          Actualizat {fmt.date(run.updated_at ?? run.created_at)}
        </span>
      </div>

      <Tabs defaultValue="summary">
        <TabsList>
          <TabsTrigger value="summary">Sumar</TabsTrigger>
          <TabsTrigger value="visuals">Grafice</TabsTrigger>
          <TabsTrigger value="files">Fișiere</TabsTrigger>
          <TabsTrigger value="raw">Manifest</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="space-y-3 py-5">
              <p className="text-sm text-ink-muted">
                Această rulare conține un tabel Q rezultat din antrenarea pe scenariul{' '}
                <strong>{meta?.label ?? run.scenario}</strong>. Folosește pagina
                Evaluare pentru a-l testa pe medii noi.
              </p>
              <div className="flex flex-wrap gap-2">
                {Object.keys(artifacts).map((k) => (
                  <Badge key={k}>{artifactLabels[k] ?? k}</Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="visuals">
          <div className="grid gap-4 sm:grid-cols-2">
            {visualKeys
              .filter((k) => artifacts[k])
              .map((k) => (
                <Card key={k}>
                  <CardContent className="space-y-2 py-4">
                    <p className="text-xs uppercase tracking-wider text-ink-muted">
                      {artifactLabels[k] ?? k}
                    </p>
                    <a
                      href={api.artifactDownloadUrl(run.id, k)}
                      target="_blank"
                      rel="noreferrer"
                      className="block overflow-hidden rounded-lg border border-border/60 bg-elevated/40"
                    >
                      <img
                        src={api.artifactDownloadUrl(run.id, k)}
                        alt={artifactLabels[k] ?? k}
                        className="w-full h-auto"
                      />
                    </a>
                  </CardContent>
                </Card>
              ))}
            {visualKeys.every((k) => !artifacts[k]) ? (
              <EmptyState title="Niciun grafic disponibil" />
            ) : null}
          </div>
        </TabsContent>

        <TabsContent value="files">
          <Card>
            <CardContent className="divide-y divide-border/40">
              {fileKeys
                .filter((k) => artifacts[k])
                .map((k) => (
                  <div
                    key={k}
                    className="flex items-center justify-between gap-3 py-3 text-sm"
                  >
                    <div className="min-w-0">
                      <p className="text-ink">{artifactLabels[k] ?? k}</p>
                      <p className="font-mono text-xs text-ink-subtle truncate">
                        {artifacts[k]}
                      </p>
                    </div>
                    <Button asChild variant="ghost" size="sm">
                      <a href={api.artifactDownloadUrl(run.id, k)} download>
                        <Download size={14} /> Descarcă
                      </a>
                    </Button>
                  </div>
                ))}
              {fileKeys.every((k) => !artifacts[k]) ? (
                <EmptyState title="Niciun fișier de descărcat" className="border-0" />
              ) : null}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="raw">
          <Card>
            <CardContent>
              <pre className="overflow-auto rounded-lg bg-canvas/80 border border-border/60 p-4 text-xs text-ink-muted">
                {JSON.stringify(run, null, 2)}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
