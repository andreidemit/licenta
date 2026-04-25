import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, ChevronRight } from 'lucide-react';
import { api } from '../../lib/api';
import { cn } from '../../lib/cn';

const routeLabels: Record<string, string> = {
  '': 'Acasă',
  antrenare: 'Antrenare',
  rulari: 'Rulări',
  evaluare: 'Evaluare',
  'editor-mediu': 'Editor mediu',
  comparatie: 'Comparație',
};

export function Topbar() {
  const location = useLocation();
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;
    const check = () => {
      api
        .health()
        .then(() => !cancelled && setBackendOk(true))
        .catch(() => !cancelled && setBackendOk(false));
    };
    check();
    const id = window.setInterval(check, 15000);
    return () => {
      cancelled = true;
      window.clearInterval(id);
    };
  }, []);

  const segments = location.pathname.split('/').filter(Boolean);
  const crumbs = [{ label: 'Acasă', to: '/' }];
  let acc = '';
  for (const seg of segments) {
    acc += `/${seg}`;
    crumbs.push({ label: routeLabels[seg] ?? seg, to: acc });
  }

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between gap-4 border-b border-border/60 bg-canvas/80 backdrop-blur px-6 py-3">
      <nav aria-label="breadcrumb" className="flex items-center gap-1.5 text-sm text-ink-muted min-w-0">
        {crumbs.map((c, i) => (
          <span key={c.to} className="flex items-center gap-1.5 min-w-0">
            {i > 0 ? <ChevronRight size={14} className="text-ink-subtle shrink-0" /> : null}
            {i === crumbs.length - 1 ? (
              <span className="text-ink truncate">{c.label}</span>
            ) : (
              <Link to={c.to} className="hover:text-ink transition-colors truncate">
                {c.label}
              </Link>
            )}
          </span>
        ))}
      </nav>

      <div className="flex items-center gap-3">
        <div
          className={cn(
            'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs',
            backendOk === null && 'border-border/60 bg-elevated/40 text-ink-muted',
            backendOk === true &&
              'border-accent-success/30 bg-accent-success/10 text-accent-success',
            backendOk === false && 'border-accent-danger/30 bg-accent-danger/10 text-accent-danger',
          )}
        >
          <Activity size={12} />
          <span>
            {backendOk === null ? 'Verific backend…' : backendOk ? 'Backend conectat' : 'Backend offline'}
          </span>
        </div>
      </div>
    </header>
  );
}
