import { useCallback, useRef, useState } from 'react';

export type StreamingState = {
  text: string;
  streaming: boolean;
  done: boolean;
  error: string | null;
};

export type StreamingControls = {
  start: (fetcher: (onToken: (t: string) => void, onDone: () => void, onError: (e: Error) => void, signal: AbortSignal) => void) => void;
  abort: () => void;
  reset: () => void;
};

/**
 * Hook care consumă un stream de tokeni SSE și expune textul acumulat.
 * Utilizare:
 *   const [state, controls] = useStreamingText();
 *   controls.start((onToken, onDone, onError, signal) => {
 *     safeNavigationApi.streamExplainAnalysis(payload, onToken, onDone, onError, signal);
 *   });
 */
export function useStreamingText(): [StreamingState, StreamingControls] {
  const [state, setState] = useState<StreamingState>({
    text: '',
    streaming: false,
    done: false,
    error: null,
  });

  const abortRef = useRef<AbortController | null>(null);

  const start = useCallback(
    (
      fetcher: (
        onToken: (t: string) => void,
        onDone: () => void,
        onError: (e: Error) => void,
        signal: AbortSignal,
      ) => void,
    ) => {
      if (abortRef.current) abortRef.current.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      setState({ text: '', streaming: true, done: false, error: null });

      fetcher(
        (token) => {
          setState((prev) => ({ ...prev, text: prev.text + token }));
        },
        () => {
          setState((prev) => ({ ...prev, streaming: false, done: true }));
        },
        (err) => {
          setState((prev) => ({
            ...prev,
            streaming: false,
            done: true,
            error: err.message,
          }));
        },
        controller.signal,
      );
    },
    [],
  );

  const abort = useCallback(() => {
    abortRef.current?.abort();
    setState((prev) => ({ ...prev, streaming: false }));
  }, []);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState({ text: '', streaming: false, done: false, error: null });
  }, []);

  return [state, { start, abort, reset }];
}
