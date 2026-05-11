import type { ReactNode } from 'react';
import { HelpCircle } from 'lucide-react';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../components/ui/tooltip';

export function TooltipLabel({
  children,
  text,
}: {
  children: ReactNode;
  text: string;
}) {
  return (
    <Tooltip delayDuration={120}>
      <TooltipTrigger asChild>
        <span className="safe-tooltip-label">
          {children}
          <HelpCircle size={13} aria-hidden="true" />
        </span>
      </TooltipTrigger>
      <TooltipContent side="top" align="center" className="safe-metric-tooltip">
        {text}
      </TooltipContent>
    </Tooltip>
  );
}
