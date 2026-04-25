import { cn } from '../../lib/cn';

export function PageHeader({
  title,
  eyebrow,
  description,
  actions,
  className,
}: {
  title: string;
  eyebrow?: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}) {
  return (
    <header className={cn('flex flex-wrap items-end justify-between gap-4 animate-slide-up', className)}>
      <div className="space-y-1.5 min-w-0">
        {eyebrow ? (
          <p className="text-xs uppercase tracking-[0.18em] text-accent-secondary font-medium">
            {eyebrow}
          </p>
        ) : null}
        <h1 className="font-serif text-3xl md:text-4xl font-semibold text-ink leading-tight">
          {title}
        </h1>
        {description ? (
          <p className="text-sm md:text-base text-ink-muted max-w-2xl">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex items-center gap-2">{actions}</div> : null}
    </header>
  );
}
