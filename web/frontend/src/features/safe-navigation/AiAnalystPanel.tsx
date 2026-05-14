import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { Bot, Loader2, MessageSquareText, Send } from 'lucide-react';
import { safeNavigationApi } from './api';
import type { LlmAnalysisResponse, LlmAnalysisStatus, MonteCarloResult } from './types';

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
    question: 'Propune următorul experiment util pentru validarea recomandării, fără să inventezi rezultate noi.',
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

export function AiAnalystPanel({ result }: { result?: MonteCarloResult }) {
  const [status, setStatus] = useState<LlmAnalysisStatus>(defaultStatus);
  const [busy, setBusy] = useState(false);
  const [question, setQuestion] = useState('');
  const [analysis, setAnalysis] = useState<LlmAnalysisResponse>();
  const [error, setError] = useState('');

  const customQuestion = question.trim();
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
    return () => {
      cancelled = true;
    };
  }, []);

  const helperText = useMemo(() => {
    if (!result?.recommendation) return 'Rulează Monte Carlo pentru a activa analistul AI.';
    if (!status.enabled) return 'LLM dezactivat: backendul va returna un fallback clar, fără apel către model.';
    if (!status.available) return status.message;
    return `Model: ${status.model} prin ${status.provider}.`;
  }, [result, status]);

  async function ask(nextQuestion: string) {
    const prompt = nextQuestion.trim();
    if (!result?.recommendation || !prompt || busy) return;
    setBusy(true);
    setError('');
    setAnalysis(undefined);
    try {
      const response = await safeNavigationApi.explainAnalysis({
        config: result.config,
        summary: result.summary,
        recommendation: result.recommendation,
        question: prompt,
        language: 'ro',
      });
      setAnalysis(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analistul AI nu a putut genera explicația.');
    } finally {
      setBusy(false);
    }
  }

  function submitCustomQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canAsk || !customQuestion) return;
    void ask(customQuestion);
  }

  return (
    <section className="ai-analyst-panel">
      <header>
        <div>
          <p className="eyebrow"><Bot size={14} /> Analist AI</p>
          <h3>Interpretare Gemma pentru rezultatele Monte Carlo</h3>
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

      {error ? <p className="ai-error">{error}</p> : null}

      {analysis ? (
        <div className="ai-answer">
          <p>{analysis.answer}</p>
          {analysis.key_points.length ? (
            <div>
              <strong>Puncte cheie</strong>
              <ul>{analysis.key_points.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          ) : null}
          {analysis.limitations.length ? (
            <div>
              <strong>Limitări</strong>
              <ul>{analysis.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
            </div>
          ) : null}
          {analysis.used_metrics.length ? (
            <small>Metrici folosite: {analysis.used_metrics.join(', ')}</small>
          ) : null}
          {analysis.fallback ? <small>Răspuns fallback, fără analiză completă de model.</small> : null}
        </div>
      ) : null}
    </section>
  );
}

export default AiAnalystPanel;
