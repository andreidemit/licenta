import type { LlmAnalysisResponse } from '../features/safe-navigation/types';

type Props = {
  title?: string;
  response: LlmAnalysisResponse | null;
  streaming?: boolean;
  streamingText?: string;
  loading?: boolean;
  error?: string | null;
  /** Dacă true, afișează key_points, limitations, used_metrics */
  expanded?: boolean;
  className?: string;
};

export function AiInsightCard({
  title = 'Analist AI',
  response,
  streaming = false,
  streamingText,
  loading = false,
  error,
  expanded = true,
  className = '',
}: Props) {
  const displayText = streaming ? streamingText ?? '' : (response?.answer ?? '');
  const showCursor = streaming && !error;
  const isFallback = response?.fallback ?? false;

  return (
    <div className={`ai-insight-card ${isFallback ? 'ai-insight-card--fallback' : ''} ${className}`}>
      <div className="ai-insight-card__header">
        <span className="ai-insight-card__icon">✦</span>
        <span className="ai-insight-card__title">{title}</span>
        {loading && !streaming && <span className="ai-status ai-status--loading">generează…</span>}
        {streaming && <span className="ai-status ai-status--streaming">transmite…</span>}
        {response?.model && !loading && !streaming && (
          <span className="ai-insight-card__model">{response.model}</span>
        )}
      </div>

      {error && (
        <p className="ai-error">{error}</p>
      )}

      {(loading && !streaming) && !error && (
        <div className="ai-skeleton">
          <div className="skeleton-line" style={{ width: '90%' }} />
          <div className="skeleton-line" style={{ width: '75%' }} />
          <div className="skeleton-line" style={{ width: '60%' }} />
        </div>
      )}

      {(displayText || showCursor) && !error && (
        <p className="ai-answer">
          {displayText}
          {showCursor && <span className="ai-cursor" />}
        </p>
      )}

      {expanded && response && !loading && !streaming && !error && (
        <>
          {response.key_points.length > 0 && (
            <ul className="ai-insight-card__points">
              {response.key_points.map((pt, i) => (
                <li key={i}>{pt}</li>
              ))}
            </ul>
          )}
          {response.limitations.length > 0 && (
            <details className="ai-insight-card__limitations">
              <summary>Limitări</summary>
              <ul>
                {response.limitations.map((lim, i) => (
                  <li key={i}>{lim}</li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
    </div>
  );
}
