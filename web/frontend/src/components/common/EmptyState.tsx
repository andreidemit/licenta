import { cn } from '../../lib/cn';

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
}: {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center text-center gap-3 py-10 px-6',
        'rounded-xl border border-dashed border-border/60 bg-surface/40',
        className,
      )}
    >
      {icon ? <div className="text-ink-subtle">{icon}</div> : null}
      <h3 className="font-serif text-lg text-ink">{title}</h3>
      {description ? (
        <p className="text-sm text-ink-muted max-w-md">{description}</p>
      ) : null}
      {action ? <div className="mt-1">{action}</div> : null}
    </div>
  );
}
