import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/cn';

const badgeVariants = cva(
  'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium border',
  {
    variants: {
      variant: {
        default: 'bg-elevated/60 border-border/60 text-ink-muted',
        accent: 'bg-accent/15 border-accent/30 text-accent',
        success: 'bg-accent-success/15 border-accent-success/30 text-accent-success',
        warning: 'bg-accent-secondary/15 border-accent-secondary/30 text-accent-secondary',
        danger: 'bg-accent-danger/15 border-accent-danger/30 text-accent-danger',
        info: 'bg-accent-info/15 border-accent-info/30 text-accent-info',
        outline: 'bg-transparent border-border text-ink-muted',
      },
    },
    defaultVariants: { variant: 'default' },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)} {...props} />;
}
