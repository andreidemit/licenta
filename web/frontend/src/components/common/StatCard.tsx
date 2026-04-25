import { motion } from 'framer-motion';
import { InfoTip } from './InfoTip';
import { cn } from '../../lib/cn';

export function StatCard({
  label,
  value,
  hint,
  icon,
  accent = 'default',
  className,
}: {
  label: string;
  value: string | number;
  hint?: string;
  icon?: React.ReactNode;
  accent?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  className?: string;
}) {
  const ring: Record<string, string> = {
    default: 'from-accent/10 to-transparent',
    success: 'from-accent-success/15 to-transparent',
    warning: 'from-accent-secondary/15 to-transparent',
    danger: 'from-accent-danger/15 to-transparent',
    info: 'from-accent-info/15 to-transparent',
  };
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: 'easeOut' }}
      className={cn(
        'relative overflow-hidden rounded-xl border border-border/60 bg-surface/80 backdrop-blur p-4',
        'shadow-soft',
        className,
      )}
    >
      <div
        aria-hidden
        className={cn(
          'absolute inset-x-0 top-0 h-px bg-gradient-to-r opacity-80',
          ring[accent],
        )}
      />
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-1.5 text-xs uppercase tracking-wider text-ink-muted">
          {icon ? <span className="text-ink-subtle">{icon}</span> : null}
          <span>{label}</span>
          {hint ? <InfoTip text={hint} /> : null}
        </div>
      </div>
      <div className="mt-2 font-mono text-2xl font-medium text-ink">{value}</div>
    </motion.div>
  );
}
