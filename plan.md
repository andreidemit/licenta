# Plan — Safe Navigation Simulator + LLM Explanation Layer

> Plan curent al lucrării de licență. Pentru planul Q-Learning energetic original (acum studiu de caz în `src/`), vezi [`docs/legacy_qlearning_plan.md`](docs/legacy_qlearning_plan.md).

## TL;DR

Aplicație web (FastAPI + React) care evaluează **Monte Carlo** mai mulți agenți de navigare pe hărți generate procedural, agregă metrici statistice (intervale de încredere bootstrap, distribuții, breakdown per hartă) și expune un **strat de explicații AI** peste rezultatele simulării. Recomandarea de algoritm rămâne deterministă; LLM-ul interpretează compromisurile, propune configurații și răspunde la întrebări — fără să modifice ranking-ul.

**Stivă tehnologică:** Python 3.11+ (FastAPI, NumPy), React 19 + Vite + TypeScript (Recharts pentru vizualizări statistice, Radix UI pentru tab-uri/tooltip), Tailwind CSS, Ollama (default `gemma4:26b`) sau provider OpenAI-compatibil.

## Componente principale

### 1. Mediu de simulare (`environment/`)
- `GridWorld` cu `RewardConfig` și `RiskModel`; suport pentru zgomot de tranziție.
- Generator BFS-validat (`MapGenerator`); preset-uri `easy`, `medium`, `hard`, `custom`.

### 2. Agenți (`agents/`)
Random, Rule-Based, A*, Risk-Aware A*, Tabular Q-Learning, Feature-Based Q-Learning, Feature-Risk-Aware A* (hibrid experimental). Fiecare implementează `BaseAgent.explain()`.

### 3. Simulator + metrici (`simulation/`, `experiments/`)
- `Simulator` rulează episoade cu logging riguros al traiectoriei și expunerii la risc.
- `aggregate_results` produce: success rate, collision rate, danger entry rate, timeout rate, reward / steps / risk distributions (`mean/std/p05..p95/min/max`), CI bootstrap 95% (1000 resamples, seed determinist).
- `run_monte_carlo_experiment` orchestrează agenți × hărți × episoade; profile `known_static`, `high_risk`, `stochastic_execution`, `same_map_learning`, `transfer_learning`, `training_cost`.

### 4. Studiu de caz Q-Learning energetic (`src/`)
Cod legacy păstrat pentru raportul reproductibil: `python -m src.final_report`. Nu mai este expus prin web.

### 5. Backend FastAPI (`web/backend/`)
Endpoints:
- `/api/health`, `/api/safe-navigation/{status,preview,episode,monte-carlo}`
- `/api/safe-navigation/monte-carlo/jobs[/...]` (cu SSE pentru live updates)
- `/api/safe-navigation/{analysis,episode,map,analysis/configure}/explain` (+ stream)

LLM client cu fallback între `/v1/chat/completions` și `/api/chat` (Ollama nativ).

### 6. Frontend React (`web/frontend/`)
- `/` (canonic) — wizard Safe Navigation: configurare → preview hartă → episod → Monte Carlo → rezultate.
- `/safe-navigation/monte-carlo` — pagină dedicată de analiză statistică (boxplot-uri, intervale de încredere, scatter risc/recompensă, heatmap per hartă, ocupare grilă, export CSV/PNG).
- `AiAnalystPanel` — un singur componenta unificată care auto-declanșează interpretarea recomandării și acceptă întrebări rapide / libere.

## Status implementare

- ✅ Mediu, agenți, simulator, agregare metrici, recomandare deterministă.
- ✅ FastAPI + React UI, vizualizări statistice avansate, export.
- ✅ Strat LLM (status, explicații pe rezultat / episod / hartă, configurator AI), streaming SSE, fallback transparent când LLM e dezactivat / indisponibil.
- ✅ Studiu de caz reproductibil în `src/` (raport `python -m src.final_report`).
- ✅ Cleanup obsolete: paginile lab Q-Learning, endpoint-urile legate de training/runs/environments, comentariul live AI și componentele UI nefolosite au fost eliminate.

## Comenzi rapide

```bash
# Backend
uvicorn web.backend.app:app --reload --port 8000

# Frontend
cd web/frontend && npm install && npm run dev   # http://localhost:5173

# Comparație Monte Carlo CLI
python -m experiments.run_experiment --profile known_static --maps 5 --episodes-per-map 3

# Studiu de caz Q-Learning
python -m src.final_report --episodes 2000 --save-qtables

# Smoke tests
python -m tests.test_safe_navigation
python -m tests.test_monte_carlo
python -m tests.test_web_api
```

## Documentație canonică

- [`.github/copilot-instructions.md`](.github/copilot-instructions.md) — instrucțiuni pentru asistenții AI (arhitectură, comenzi, capcane).
- [`readme.md`](readme.md), [`licenta.md`](licenta.md), [`prezentare.md`](prezentare.md) — descriere lucrare, capitole teză, slide-uri.
- [`docs/legacy_qlearning_plan.md`](docs/legacy_qlearning_plan.md) — planul detaliat original (Q-Learning energetic), păstrat ca referință istorică.
