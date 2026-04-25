import { useCallback, useEffect, useRef, useState } from 'react';
import type { JobSnapshot, LiveEvent, TrainRequest } from '../lib/types';
import { api } from '../lib/api';

export type ChartPoint = { step: number; reward: number; energy: number };

export type TrainingState = {
  job?: JobSnapshot;
  live?: LiveEvent;
  chart: ChartPoint[];
  isStreaming: boolean;
  error?: string;
};

export function useTrainingStream() {
  const [state, setState] = useState<TrainingState>({ chart: [], isStreaming: false });
  const sourceRef = useRef<EventSource | null>(null);

  const stop = useCallback(() => {
    sourceRef.current?.close();
    sourceRef.current = null;
    setState((s) => ({ ...s, isStreaming: false }));
  }, []);

  const start = useCallback(async (payload: TrainRequest) => {
    stop();
    setState({ chart: [], isStreaming: true });
    try {
      const created = await api.startTraining(payload);
      setState((s) => ({ ...s, job: created }));
      const source = new EventSource(api.streamUrl(created.id));
      sourceRef.current = source;
      source.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'step') {
          setState((s) => ({
            ...s,
            live: msg as LiveEvent,
            chart: [
              ...s.chart.slice(-180),
              {
                step: msg.agent?.steps ?? 0,
                reward: msg.agent?.reward ?? 0,
                energy: msg.agent?.energy ?? 0,
              },
            ],
          }));
        }
        if (msg.type === 'job_status') {
          setState((s) => ({ ...s, job: msg as JobSnapshot }));
          if (['completed', 'failed', 'cancelled'].includes(msg.status)) {
            source.close();
            sourceRef.current = null;
            setState((s) => ({ ...s, isStreaming: false }));
          }
        }
      };
      source.onerror = () => {
        source.close();
        sourceRef.current = null;
        setState((s) => ({ ...s, isStreaming: false }));
      };
      return created;
    } catch (err) {
      setState({
        chart: [],
        isStreaming: false,
        error: err instanceof Error ? err.message : 'Eroare necunoscută',
      });
      throw err;
    }
  }, [stop]);

  useEffect(() => () => stop(), [stop]);

  return { ...state, start, stop };
}
