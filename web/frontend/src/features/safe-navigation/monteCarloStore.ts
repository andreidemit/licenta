import { useEffect, useState } from 'react';
import type { MonteCarloResult } from './types';

const STORAGE_KEY = 'safeNavigation.lastMonteCarloResult';

let cached: MonteCarloResult | undefined;
const listeners = new Set<(value: MonteCarloResult | undefined) => void>();

function notify(value: MonteCarloResult | undefined) {
  for (const listener of listeners) listener(value);
}

function readFromStorage(): MonteCarloResult | undefined {
  if (typeof window === 'undefined') return undefined;
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return undefined;
    return JSON.parse(raw) as MonteCarloResult;
  } catch {
    return undefined;
  }
}

export function getLatestMonteCarlo(): MonteCarloResult | undefined {
  if (cached) return cached;
  cached = readFromStorage();
  return cached;
}

export function setLatestMonteCarlo(value: MonteCarloResult | undefined) {
  cached = value;
  if (typeof window !== 'undefined') {
    try {
      if (value) window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(value));
      else window.sessionStorage.removeItem(STORAGE_KEY);
    } catch {
      // sessionStorage might be unavailable; continue with in-memory cache
    }
  }
  notify(value);
}

export function useLatestMonteCarlo(): MonteCarloResult | undefined {
  const [value, setValue] = useState<MonteCarloResult | undefined>(() => getLatestMonteCarlo());
  useEffect(() => {
    const listener = (next: MonteCarloResult | undefined) => setValue(next);
    listeners.add(listener);
    setValue(getLatestMonteCarlo());
    return () => {
      listeners.delete(listener);
    };
  }, []);
  return value;
}
