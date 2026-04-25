import { useEffect, useRef, useState } from 'react';

export function useReplayPlayer(maxStep: number, opts?: { speedMs?: number }) {
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speedMs, setSpeedMs] = useState(opts?.speedMs ?? 350);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    setStep(0);
    setPlaying(false);
  }, [maxStep]);

  useEffect(() => {
    if (!playing || maxStep <= 0) return;
    timerRef.current = window.setInterval(() => {
      setStep((s) => {
        if (s >= maxStep) {
          setPlaying(false);
          return s;
        }
        return s + 1;
      });
    }, speedMs);
    return () => {
      if (timerRef.current !== null) window.clearInterval(timerRef.current);
    };
  }, [playing, maxStep, speedMs]);

  return {
    step,
    setStep,
    playing,
    setPlaying,
    speedMs,
    setSpeedMs,
    reset: () => setStep(0),
    next: () => setStep((s) => Math.min(maxStep, s + 1)),
    prev: () => setStep((s) => Math.max(0, s - 1)),
    end: () => setStep(maxStep),
  };
}
