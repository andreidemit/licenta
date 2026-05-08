import { NavLink } from 'react-router-dom';
import {
  Home,
  Sparkles,
  Layers,
  Target,
  PencilRuler,
  GitCompareArrows,
} from 'lucide-react';
import { cn } from '../../lib/cn';

const navItems = [
  { to: '/lab', label: 'Legacy home', icon: Home, end: true },
  { to: '/lab/antrenare', label: 'Legacy training', icon: Sparkles },
  { to: '/lab/rulari', label: 'Legacy runs', icon: Layers },
  { to: '/lab/evaluare', label: 'Legacy evaluation', icon: Target },
  { to: '/lab/editor-mediu', label: 'Legacy map editor', icon: PencilRuler },
  { to: '/lab/comparatie', label: 'Legacy comparison', icon: GitCompareArrows },
];

export function Sidebar() {
  return (
    <aside className="hidden lg:flex w-60 shrink-0 flex-col border-r border-border/60 bg-surface/40 backdrop-blur px-3 py-5 gap-1">
      <div className="px-3 pb-4 mb-2 border-b border-border/40">
        <p className="font-serif text-lg font-semibold text-ink leading-tight">
          Legacy Q-Learning Lab
        </p>
        <p className="text-xs text-ink-subtle mt-0.5">
          Original tabular RL workflow
        </p>
      </div>
      <nav className="flex flex-col gap-0.5">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-all',
                'text-ink-muted hover:bg-elevated/60 hover:text-ink',
                isActive &&
                  'bg-accent/15 text-ink shadow-[inset_2px_0_0_0_hsl(var(--accent-primary))]',
              )
            }
          >
            <Icon size={16} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto px-3 pt-4 border-t border-border/40">
        <p className="text-[10px] uppercase tracking-wider text-ink-subtle">
          Versiune UI
        </p>
        <p className="text-xs text-ink-muted mt-0.5">v2 · 2025</p>
      </div>
    </aside>
  );
}
