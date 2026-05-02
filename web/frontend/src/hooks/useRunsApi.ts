import { useCallback, useEffect, useState } from 'react';
import { api } from '../lib/api';
import type {
  EvaluationScenario,
  JobSnapshot,
  QTableItem,
  StoredEnvironment,
} from '../lib/types';

export function useRuns() {
  const [runs, setRuns] = useState<JobSnapshot[]>([]);
  const [loading, setLoading] = useState(false);
  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const payload = await api.listRuns();
      setRuns(payload.runs ?? []);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void reload();
  }, [reload]);
  return { runs, loading, reload };
}

export function useQTables() {
  const [items, setItems] = useState<QTableItem[]>([]);
  const reload = useCallback(async () => {
    const payload = await api.listQTables();
    setItems(payload.qtables ?? []);
  }, []);
  useEffect(() => {
    void reload();
  }, [reload]);
  return { items, reload };
}

export function useStoredEnvironments() {
  const [items, setItems] = useState<StoredEnvironment[]>([]);
  const reload = useCallback(async () => {
    const payload = await api.listEnvironments();
    setItems(payload.environments ?? []);
  }, []);
  useEffect(() => {
    void reload();
  }, [reload]);
  return { items, reload };
}

export function useEvaluationScenarios() {
  const [items, setItems] = useState<EvaluationScenario[]>([]);
  useEffect(() => {
    let cancelled = false;
    void api.evaluationScenarios().then((payload) => {
      if (!cancelled) setItems(payload.scenarios ?? []);
    });
    return () => {
      cancelled = true;
    };
  }, []);
  return items;
}
