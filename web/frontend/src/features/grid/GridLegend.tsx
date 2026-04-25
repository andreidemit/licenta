import { paintTools, cellColors, cellLabels, cellDescriptions } from '../../lib/formatters';
import { Tooltip, TooltipContent, TooltipTrigger } from '../../components/ui/tooltip';

export function GridLegend() {
  return (
    <div className="flex flex-wrap gap-2">
      {paintTools.map((cell) => (
        <Tooltip key={cell} delayDuration={150}>
          <TooltipTrigger asChild>
            <span className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-elevated/60 px-2.5 py-1 text-xs text-ink-muted">
              <span
                className="h-3 w-3 rounded-sm"
                style={{ backgroundColor: cellColors[cell] }}
              />
              {cellLabels[cell]}
            </span>
          </TooltipTrigger>
          <TooltipContent>{cellDescriptions[cell]}</TooltipContent>
        </Tooltip>
      ))}
    </div>
  );
}
