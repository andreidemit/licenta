import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { Bot, Loader2, MessageSquareText, Send } from 'lucide-react';
import { AiInsightCard } from '../../components/AiInsightCard';
import { useStreamingText } from '../../hooks/useStreamingText';
import { safeNavigationApi } from './api';
import type { LlmAnalysisStatus, MonteCarloResult } from './types';

const QUICK_QUESTIONS = [
  {
    label: 'Explică recomandarea',
    question: 'Explică recomandarea, ranking-ul și principalele compromisuri pentru această rulare Monte Carlo.',
  },
  {
    label: 'De ce nu a câștigat alt algoritm?',
    question: 'Explică de ce algoritmii care nu sunt recomandați au pierdut, folosind doar metricile din rezultat.',
  },
  {
    label: 'Ce experiment urmează?',
    question: 'Propune următorul experiment util pentru validarea recomandării, fără să inventezi rezultate noi sau să schimbi ranking-ul.',
  },
];

function defaultStatus(): LlmAnalysisStatus {
  return {
    enabled: false,
    available: false,
    provider: 'ollama',
    model: 'gemma4:26b',
    message: 'Se verifică disponibilitatea analistului AI...',
  };
}

export function AiAnalystPanel({ result, autoTrigger = false }: { result?: MonteCarloResult; autoTrigger?: boolean }) {
  const [status, setStatus] = useState<LlmAnalysisStatus>(defaultStatus);
  const [question, setQuestion] = useState('');
  const [streamState, streamControls] = useStreamingText();

  const customQuestion = question.trim();
  const busy = streamState.streaming;
  const canAsk = !!result?.recommendation && !busy && (status.available || !status.enabled);
  const statusClass = status.available ? 'available' : status.enabled ? 'unavailable' : 'disabled';
  const statusLabel = status.available ? 'disponibil' : status.enabled ? 'indisponibil' : 'dezactivat';

  useEffect(() => {
    let cancelled = false;
    async function loadStatus() {
      try {
        const response = await safeNavigationApi.analysisStatus();
        if (!cancelled) setStatus(response);
      } catch (err) {
        if (!cancelled) {
          setStatus({
            ...defaultStatus(),
            enabled: true,
            available: false,
            message: err instanceof Error ? err.message : 'Nu se poate verifica analistul AI.',
          });
        }
      }
    }
    loadStatus();
    return () => { cancelled = true; };
  }, []);

  // Auto-trigger la prima întrebare rapidă când LLM devine disponibil
  useEffect(() => {
    if (!autoTrigger || !result?.recommendation || !status.available) return;
    ask(QUICK_QUESTIONS[0].question);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoTrigger, status.available, result?.recommendation]);

  const helperText = useMemo(() => {
    if (!result?.recommendation) return 'Rulează Monte Carlo pentru a activa analistul AI.';
    if (!status.enabled) return 'LLM dezactivat: backendul va returna un fallback clar, fără apel către model.';
    if (!status.available) return status.message;
    return `Model: ${status.model} prin ${status.provider}. Explică rezultatele; nu modifică recomandarea deterministă.`;
  }, [result, status]);

  function ask(nextQuestion: string) {
    const prompt = nextQuestion.trim();
    if (!result?.recommendation || !prompt || busy) return;
    streamControls.reset();
    streamControls.start((onToken, onDone, onError, signal) => {
      safeNavigationApi.streamExplainAnalysis(
        {
          config: result.config,
          summary: result.summary,
          recommendation: result.recommendation!,
          question: prompt,
          language: 'ro',
        },
        onToken, onDone, onError, signal,
      );
    });
  }

  function submitCustomQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canAsk || !customQuestion) return;
    ask(customQuestion);
  }

  return (
    <section className="ai-analyst-panel">
      <header>
        <div>
          <p className="eyebrow"><Bot size={14} /> Analist AI</p>
          <h3>Asistent de interpretare pentru rezultatele Monte Carlo</h3>
        </div>
        <span className={`ai-status ${statusClass}`}>{statusLabel}</span>
      </header>

      <p className="ai-helper">{helperText}</p>

      <div className="ai-quick-actions">
        {QUICK_QUESTIONS.map((item) => (
          <button
            type="button"
            key={item.label}
            disabled={!canAsk}
            onClick={() => ask(item.question)}
          >
            <MessageSquareText size={14} /> {item.label}
          </button>
        ))}
      </div>

      <form className="ai-question-row" onSubmit={submitCustomQuestion}>
        <input
          type="text"
          value={question}
          placeholder="Întrebare liberă despre rezultat..."
          disabled={!result?.recommendation || busy}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit" disabled={!canAsk || !customQuestion}>
          {busy ? <Loader2 size={15} className="mc-spin" /> : <Send size={15} />} Trimite
        </button>
      </form>

      {(streamState.text || streamState.streaming || streamState.error || streamState.done) && (
        <AiInsightCard
          title="Răspuns Analist AI"
          response={null}
          streaming={streamState.streaming}
          streamingText={streamState.text}
          loading={streamState.streaming && !streamState.text}
          error={streamState.error}
          expanded={false}
        />
      )}
    </section>
  );
}

export default AiAnalystPanel;
