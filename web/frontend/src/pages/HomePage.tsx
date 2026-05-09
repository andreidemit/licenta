import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Sparkles,
  Target,
  PencilRuler,
  Layers,
  GitCompareArrows,
  Brain,
} from 'lucide-react';
import { PageHeader } from '../components/common/PageHeader';
import { Card, CardContent } from '../components/ui/card';
import { useRuns } from '../hooks/useRunsApi';
import { Badge } from '../components/ui/badge';
import { fmt, scenarioMeta, translateStatus } from '../lib/formatters';

const shortcuts = [
  {
    to: '/lab/antrenare',
    icon: Sparkles,
    title: 'Antrenează agentul',
    description:
      'Configurează scenariul, ajustează hiperparametrii și pornește un job de antrenare cu progres live.',
    accent: 'from-sky-400/20',
  },
  {
    to: '/lab/evaluare',
    icon: Target,
    title: 'Pune agentul la probă',
    description:
      'Alege un tabel Q antrenat și un scenariu de test, apoi privește agentul cum se descurcă pe noul mediu.',
    accent: 'from-emerald-400/20',
  },
  {
    to: '/lab/editor-mediu',
    icon: PencilRuler,
    title: 'Construiește un mediu',
    description:
      'Pictează propria hartă cu obstacole, hrană și pericole. Validează drumul cu BFS înainte de testare.',
    accent: 'from-amber-400/20',
  },
  {
    to: '/lab/rulari',
    icon: Layers,
    title: 'Explorează rulările',
    description:
      'Răsfoiește experimentele anterioare, vezi grafice de convergență și descarcă artefactele.',
    accent: 'from-violet-400/20',
  },
  {
    to: '/lab/comparatie',
    icon: GitCompareArrows,
    title: 'Compară experimente',
    description:
      'Suprapune până la 4 rulări și observă diferențele de performanță și convergență.',
    accent: 'from-rose-400/20',
  },
];

export function HomePage() {
  const { runs } = useRuns();
  const lastRun = runs[0];
  return (
    <div className="space-y-10">
      <PageHeader
        eyebrow="Laborator academic"
        title="Laborator Q-Learning"
        description="Un studiu interactiv asupra învățării prin recompensă: configurează experimente, observă agentul în timp real și testează politici învățate pe medii noi."
      />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {shortcuts.map((s, i) => {
          const Icon = s.icon;
          return (
            <motion.div
              key={s.to}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * i, duration: 0.3, ease: 'easeOut' }}
            >
              <Link to={s.to} className="group block h-full">
                <Card className="relative h-full overflow-hidden transition-all hover:-translate-y-0.5 hover:shadow-glow">
                  <div
                    aria-hidden
                    className={`absolute inset-0 bg-gradient-to-br ${s.accent} to-transparent opacity-50 group-hover:opacity-80 transition-opacity`}
                  />
                  <CardContent className="relative space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="inline-flex h-10 w-10 items-center justify-center rounded-lg bg-elevated/60 border border-border/60 text-accent">
                        <Icon size={20} />
                      </div>
                      <ArrowRight
                        size={18}
                        className="text-ink-subtle group-hover:text-accent group-hover:translate-x-1 transition-all"
                      />
                    </div>
                    <h3 className="font-serif text-lg text-ink">{s.title}</h3>
                    <p className="text-sm text-ink-muted leading-relaxed">{s.description}</p>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          );
        })}
      </section>

      {lastRun ? (
        <section className="space-y-3">
          <h2 className="font-serif text-xl text-ink flex items-center gap-2">
            <Brain size={18} className="text-accent" /> Ultima rulare
          </h2>
          <Link to={`/lab/rulari/${lastRun.id}`}>
            <Card className="hover:-translate-y-0.5 transition-transform">
              <CardContent className="flex flex-wrap items-center gap-4 justify-between">
                <div className="space-y-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="accent">
                      {scenarioMeta[lastRun.scenario]?.label ?? lastRun.scenario}
                    </Badge>
                    <Badge>{translateStatus(lastRun.status)}</Badge>
                    <span className="text-xs text-ink-subtle">
                      {fmt.date(lastRun.updated_at ?? lastRun.created_at)}
                    </span>
                  </div>
                  <p className="text-sm text-ink-muted truncate">{lastRun.id}</p>
                </div>
                <div className="flex items-center gap-2 text-accent">
                  <span className="text-sm">Vezi detalii</span>
                  <ArrowRight size={16} />
                </div>
              </CardContent>
            </Card>
          </Link>
        </section>
      ) : null}
    </div>
  );
}
