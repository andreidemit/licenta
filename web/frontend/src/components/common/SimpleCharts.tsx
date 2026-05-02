import { useId } from 'react';

type RewardPoint = {
  step: number;
  reward: number;
};

type SeriesConfig = {
  key: string;
  label: string;
  color: string;
};

const fmtAxis = (value: number) =>
  Math.abs(value) >= 100 ? Math.round(value).toString() : value.toFixed(0);

function normalizeId(id: string) {
  return id.replace(/[^a-zA-Z0-9_-]/g, '');
}

function yScale(value: number, min: number, max: number, top: number, bottom: number) {
  const range = max - min || 1;
  return bottom - ((value - min) / range) * (bottom - top);
}

export function RewardAreaChart({
  data,
  width = 340,
  height = 140,
  stroke = 'hsl(217 91% 70%)',
  fill = 'hsl(217 91% 60%)',
  ariaLabel = 'Grafic cu evolutia recompensei',
}: {
  data: RewardPoint[];
  width?: number;
  height?: number;
  stroke?: string;
  fill?: string;
  ariaLabel?: string;
}) {
  const gradientId = normalizeId(useId());
  const padding = { top: 12, right: 12, bottom: 18, left: 12 };
  const top = padding.top;
  const bottom = height - padding.bottom;
  const left = padding.left;
  const right = width - padding.right;
  const safeData = data.length > 0 ? data : [{ step: 0, reward: 0 }];
  const rewards = safeData.map((p) => p.reward);
  const rawMin = Math.min(...rewards);
  const rawMax = Math.max(...rewards);
  const pad = Math.max(4, (rawMax - rawMin) * 0.12);
  const min = rawMin - pad;
  const max = rawMax + pad;

  const points = safeData.map((point, index) => {
    const x =
      safeData.length === 1
        ? (left + right) / 2
        : left + (index / (safeData.length - 1)) * (right - left);
    return { x, y: yScale(point.reward, min, max, top, bottom) };
  });

  const linePath = points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' ');
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${bottom} L ${points[0].x} ${bottom} Z`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label={ariaLabel}
      className="block"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={fill} stopOpacity={0.7} />
          <stop offset="100%" stopColor={fill} stopOpacity={0.02} />
        </linearGradient>
      </defs>
      <line x1={left} x2={right} y1={bottom} y2={bottom} stroke="hsl(222 24% 28%)" strokeDasharray="4 4" />
      <path d={areaPath} fill={`url(#${gradientId})`} />
      <path d={linePath} fill="none" stroke={stroke} strokeWidth={2.5} strokeLinecap="round" strokeLinejoin="round" />
      {points.length === 1 ? <circle cx={points[0].x} cy={points[0].y} r={3} fill={stroke} /> : null}
    </svg>
  );
}

export function MultiLineChart({
  data,
  series,
  xKey,
  width = 920,
  height = 320,
}: {
  data: Record<string, number>[];
  series: SeriesConfig[];
  xKey: string;
  width?: number;
  height?: number;
}) {
  const padding = { top: 20, right: 26, bottom: 64, left: 52 };
  const left = padding.left;
  const right = width - padding.right;
  const top = padding.top;
  const bottom = height - padding.bottom;
  const innerWidth = right - left;
  const innerHeight = bottom - top;
  const xValues = data.map((point) => Number(point[xKey])).filter(Number.isFinite);
  const yValues = data
    .flatMap((point) => series.map((item) => Number(point[item.key])))
    .filter(Number.isFinite);
  const minX = xValues.length ? Math.min(...xValues) : 0;
  const maxX = xValues.length ? Math.max(...xValues) : 1;
  const rawMinY = yValues.length ? Math.min(...yValues) : 0;
  const rawMaxY = yValues.length ? Math.max(...yValues) : 100;
  const padY = Math.max(5, (rawMaxY - rawMinY) * 0.12);
  const minY = rawMinY - padY;
  const maxY = rawMaxY + padY;
  const xRange = maxX - minX || 1;
  const gridLines = Array.from({ length: 5 }, (_, index) => {
    const ratio = index / 4;
    const y = top + ratio * innerHeight;
    const value = maxY - ratio * (maxY - minY);
    return { y, value };
  });

  const toX = (value: number) => left + ((value - minX) / xRange) * innerWidth;
  const toY = (value: number) => yScale(value, minY, maxY, top, bottom);

  if (series.length === 0) {
    return (
      <svg width={width} height={height} role="img" aria-label="Grafic gol" className="block">
        <text x={width / 2} y={height / 2} textAnchor="middle" fill="hsl(215 16% 65%)" fontSize={12}>
          Selecteaza cel putin o rulare.
        </text>
      </svg>
    );
  }

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Grafic comparativ pentru rularile selectate"
      className="block"
    >
      <rect x={0} y={0} width={width} height={height} rx={16} fill="transparent" />
      {gridLines.map((line) => (
        <g key={line.y}>
          <line x1={left} x2={right} y1={line.y} y2={line.y} stroke="hsl(222 24% 24%)" strokeDasharray="3 3" />
          <text x={left - 10} y={line.y + 4} textAnchor="end" fill="hsl(215 16% 55%)" fontSize={11}>
            {fmtAxis(line.value)}
          </text>
        </g>
      ))}
      <line x1={left} x2={right} y1={bottom} y2={bottom} stroke="hsl(222 24% 28%)" />
      <line x1={left} x2={left} y1={top} y2={bottom} stroke="hsl(222 24% 28%)" />
      <text x={left} y={bottom + 22} textAnchor="middle" fill="hsl(215 16% 55%)" fontSize={11}>
        {fmtAxis(minX)}
      </text>
      <text x={right} y={bottom + 22} textAnchor="middle" fill="hsl(215 16% 55%)" fontSize={11}>
        {fmtAxis(maxX)}
      </text>
      {series.map((item) => {
        const path = data
          .map((point, index) => {
            const x = toX(Number(point[xKey]));
            const y = toY(Number(point[item.key]));
            return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
          })
          .join(' ');
        return (
          <path
            key={item.key}
            d={path}
            fill="none"
            stroke={item.color}
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        );
      })}
      {series.map((item, index) => {
        const x = left + index * 205;
        const y = height - 28;
        return (
          <g key={item.key} transform={`translate(${x}, ${y})`}>
            <circle cx={0} cy={-4} r={4} fill={item.color} />
            <text x={12} y={0} fill="hsl(215 20% 78%)" fontSize={11}>
              {item.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}
