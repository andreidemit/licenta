import * as React from 'react';
import { cn } from '../../lib/cn';

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        'w-full rounded-lg bg-elevated/60 border border-border/60 px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus:border-accent focus:ring-0 transition-colors',
        className,
      )}
      {...props}
    />
  ),
);
Input.displayName = 'Input';

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      'w-full rounded-lg bg-elevated/60 border border-border/60 px-3 py-2 text-xs font-mono text-ink placeholder:text-ink-subtle focus:border-accent focus:ring-0 transition-colors',
      className,
    )}
    {...props}
  />
));
Textarea.displayName = 'Textarea';

export const Select = React.forwardRef<HTMLSelectElement, React.SelectHTMLAttributes<HTMLSelectElement>>(
  ({ className, children, ...props }, ref) => (
    <select
      ref={ref}
      className={cn(
        'w-full rounded-lg bg-elevated/60 border border-border/60 px-3 py-2 text-sm text-ink focus:border-accent focus:ring-0 transition-colors',
        className,
      )}
      {...props}
    >
      {children}
    </select>
  ),
);
Select.displayName = 'Select';

export const Label = ({
  className,
  children,
  ...props
}: React.LabelHTMLAttributes<HTMLLabelElement>) => (
  <label
    className={cn('block text-xs font-medium uppercase tracking-wider text-ink-muted mb-1.5', className)}
    {...props}
  >
    {children}
  </label>
);
