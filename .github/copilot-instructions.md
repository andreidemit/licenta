# Copilot instructions

Sursă canonică pentru asistenții AI care lucrează în acest repository.
`AGENTS.md` și `CLAUDE.md` sunt aliasuri care fac trimitere aici.

## Privire de ansamblu

Repository-ul conține **două stive Python independente** care coexistă, plus
o aplicație web care le expune pe ambele:

| Stivă | Scop | Module cheie | Punct de intrare |
|-------|------|--------------|------------------|
| **Legacy Q-Learning** | Teză academică originală: tabular Q-Learning cu energie pe scenariile A/B/C/WAREHOUSE, GUI Pygame, exporturi CSV/PNG. | `src/` | `python -m src.main`, `python -m src.final_report` |
| **Safe Navigation + Monte Carlo** | Cadru generic pentru evaluarea comparativă a mai multor agenți (Random, RuleBased, A*, A* conștient de risc, Tabular Q, Feature-based Q) prin simulare Monte Carlo, cu metrici statistice extinse. | `environment/`, `agents/`, `simulation/`, `experiments/` | `python -m experiments.run_experiment`, FastAPI `web/backend/app.py` |
| **Aplicație web** | UI React + Vite peste FastAPI; expune ambele stive. | `web/backend/`, `web/frontend/` | `uvicorn web.backend.app:app`, `npm run dev` |

Cele două stive **nu** comunică între ele: legacy folosește `src/constants.py`
(reward, energie, scenarii); safe-navigation folosește `RewardConfig` din
`environment/grid_world.py`. Există două clase cu același nume `EpisodeResult`
(`src/trainer.py` și `simulation/episode_result.py`) — schemele sunt diferite
și **nu** sunt interschimbabile.

## Comenzi

Toate comenzile se rulează din rădăcina repo-ului, cu mediul virtual activ.

### Setup
```bash
python -m pip install -r requirements.txt
cd web/frontend && npm install   # doar pentru frontend
```

### Stiva legacy (`src/`)
```bash
# Mod manual (Pygame)
python -m src.main
python -m src.main --grid 10 --seed 100

# Antrenament
python -m src.main --train
python -m src.main --train --scenario A
python -m src.main --train --scenario C
python -m src.main --train --scenario WAREHOUSE
python -m src.main --alpha-sensitivity
python -m src.main --train --save-qtable data/qt.npy
python -m src.main --load-qtable data/qt.npy --visualize

# Pachetul standardizat pentru raport
python -m src.final_report --episodes 2000 --save-qtables
```

### Stiva safe-navigation (Monte Carlo)
```bash
# Comparare CLI a agenților pe profil prestabilit
python -m experiments.run_experiment

# Cu opțiuni: --profile, --scenario, --algorithms, --maps, --episodes-per-map
python -m experiments.run_experiment \
    --profile transfer_learning --scenario medium --maps 5 --episodes-per-map 3
```

Profile disponibile (`experiments/compare_agents.py::EXPERIMENT_PROFILES`):
`known_static`, `high_risk`, `stochastic_execution`, `same_map_learning`,
`transfer_learning`, `training_cost`. Fiecare declară `agent_lifecycle`:
- `per_map` — agentul este re-creat pentru fiecare hartă; pentru agenții
  Q, asta înseamnă că politica nu se transferă între hărți.
- `shared_across_maps` — agentul este antrenat o singură dată pe hărți
  dedicate, apoi evaluat pe alte hărți (doar `transfer_learning`).

### Aplicație web
```bash
# Backend FastAPI
uvicorn web.backend.app:app --reload --port 8000

# Frontend (alt terminal)
cd web/frontend && npm run dev   # http://localhost:5173

# Build de producție
cd web/frontend && npm run build
```

Rute principale:
- `/` și `/safe-navigation` — Wizard Safe Navigation (rulare hartă, episod, Monte Carlo).
- `/safe-navigation/monte-carlo` — Pagină dedicată de analiză statistică a ultimei rulări MC (boxplot-uri, intervale de încredere, scatter risc/recompensă, heatmap per hartă, heatmap de ocupare, export CSV/PNG).
- `/lab` — Laborator legacy Q-Learning (antrenare, rulări salvate, evaluare).

### Teste
Testele sunt module script-style sub `tests/`. Nu există configurare pytest.
```bash
python -m tests.test_quick
python -m tests.test_convergence
python -m tests.test_scenarios
python -m tests.test_warehouse
python -m tests.test_analytics
python -m tests.test_persistence
python -m tests.test_safe_navigation
python -m tests.test_metrics_extended
python -m tests.test_monte_carlo
python -m tests.test_web_api
python -m tests.test_transitions

# O funcție de test individuală
python -c "from tests.test_analytics import test_export_csv_creates_file; test_export_csv_creates_file()"
```

## Arhitectură detaliată

### Stiva legacy (`src/`)
- `src/main.py` — orchestrare CLI: mod manual, training, replay Q-table, sensibilitate alpha, scenariul fix `WAREHOUSE`.
- `src/environment.py` — generare procedurală de hartă (seed, BFS-validată) și `try_move()` care returnează tot payload-ul tranziției.
- `src/agent.py` — stare continuă a agentului și metrici per episod. `Agent.get_state()` proiectează în spațiul Q-Learning `(row, col, energy_bucket)`.
- `src/q_learning.py` — Q-table numpy `(rows, cols, 4, 5)`, ε-greedy, actualizări Bellman, persistență.
- `src/trainer.py` — singura buclă de antrenament; reset per episod, aplicare rezultat tranziție, actualizare Bellman, `EpisodeResult` legacy, switch-ul Scenario C.
- `src/renderer.py` — strat Pygame; overlay de heatmap Q-value și săgeți de politică.
- `src/analytics.py` — exporturi CSV + grafice Matplotlib în `data/`.
- `src/warehouse_scenario.py` — layout fix 20×20, păstrează același pipeline.
- `src/final_report.py` — pachetul reproductibil pentru lucrare (rulări standardizate, sumar CSV/JSON).

### Stiva safe-navigation
- `environment/grid_world.py` — `GridWorld` cu `RewardConfig`, `RiskModel`, `movement_noise`. Returnează `(observation, reward, done, info)` din `step()`.
- `environment/map_generator.py` — generator BFS-validat, `SCENARIOS` prestabilite (`easy`, `medium`, `hard`, `custom`).
- `agents/base_agent.py` — interfață: `select_action`, `learn`, `reset`, `state_key`, `requires_training`, `name`, `explain()`.
- `simulation/simulator.py` — `Simulator(env, agent).run_episode(training=False)` — reset env + agent, până la `max_steps`, returnează `EpisodeResult` cu metrici riguros agregate.
- `simulation/metrics.py` — `aggregate_results(results)` returnează:
  - per agent: `success_rate`, intervale de încredere bootstrap 95%, distribuții (`mean/std/p05..p95/min/max`) pentru recompensă, pași, expunere la risc;
  - top-level `per_map[]`: defalcare agent × `map_seed`.
- `experiments/compare_agents.py` — `run_monte_carlo_experiment(...)` orchestrează toți agenții × toate hărțile pentru un profil dat. Pentru `transfer_learning` apelează `_run_transfer_experiment` care antrenează pe seed-uri dedicate (offset `+50_000`).

### Aplicație web
- `web/backend/app.py` — FastAPI: `/api/safe-navigation/{status,preview,episode,monte-carlo}`, `/api/training/...` (jobs cu `job_store.py`), `/api/evaluation-scenarios`, `/api/environments/preview`, `/api/scenarios`, `/api/runs/...`.
- `web/backend/models.py` — Pydantic. `MonteCarloRequest.algorithms` defaultuiește la cei 6 agenți expuși de UI.
- `web/frontend/src/App.tsx` — wizard-ul Safe Navigation (montat la `/` și `/safe-navigation`).
- `web/frontend/src/app/router.tsx` — toate rutele, inclusiv `/safe-navigation/monte-carlo`.
- `web/frontend/src/features/safe-navigation/` — wizard, panouri, dashboard comparativ.
- `web/frontend/src/features/safe-navigation/analysis/` — pagina dedicată de analiză MC + componente Recharts (`RewardDistribution`, `MetricCIBars`, `RiskRewardScatter`, `PerMapHeatmap`, `FailureBreakdown`, `OccupancyHeatmap`, `ExportPanel`).
- `web/frontend/src/features/safe-navigation/monteCarloStore.ts` — sessionStorage + hook care păstrează ultimul rezultat MC între rute, ca să nu fie nevoie de re-rulare.

## Convenții cheie

- **Contractul tranziției** se centrează pe `Environment.try_move()` (legacy) sau `GridWorld.step()` (safe-nav). Nu strecurați logică de reward în agent — modificați configurația sau modelul de risc.
- **Spațiul de stare RL** păstrează separarea continuu/discret: agentul are energie în `[0, ENERGY_MAX]`, dar Q-Learning indexează 4 buckets (`constants.ENERGY_THRESHOLDS`).
- **Wiring-ul scenariilor** este centralizat în `src/main.py` (legacy) sau `EXPERIMENT_PROFILES` (safe-nav). Adăugați configurări prin extinderea acelor structuri, nu prin if-uri răspândite.
- **`Environment.reset()` regenerează** din seed-ul stocat la fiecare episod. Subclasele trebuie să respecte același contract.
- **Antrenamentul legacy** prin `src.main.run_training()` exportă mereu `results_*`, `convergence_*`, `epsilon_*`, `success_*` în `data/`. Testele și artefactele istorice presupun acest naming.
- **`src.final_report`** este intrarea standardizată pentru pachetul reproductibil de teză.
- **Stilistic**: comentarii, docstring-uri și UI strings în română; identificatori în engleză.
- **Pentru smoke tests rapide**, `--episodes 50` rămâne defaultul potrivit (corespunde ferestrei rolling din `analytics`).

## Cum se citește analiza Monte Carlo în UI

Pagina `/safe-navigation/monte-carlo` conține tab-uri pentru:
- **Distribuții** — boxplot per agent (recompensă/pași/risc), comutator de metrică.
- **Intervale de încredere** — bare cu error bars CI 95% pentru success_rate, collision_rate, danger_entry_rate, timeout_rate, average_reward, average_steps, average_risk_exposure.
- **Risc / Recompensă** — scatter Pareto (un punct = un episod, mărime = pași, color = agent).
- **Per-hartă** — heatmap agent × `map_seed` colorat după success_rate.
- **Eșecuri** — stacked bar succes / pericol / coliziune / timeout.
- **Ocupare grilă** — heatmap SVG agregat din path-uri pe agentul selectat.
- **Export** — CSV (rezumat agregat + episoade brute), JSON, PNG per chart.

CI-urile sunt bootstrap 1000 resamples cu seed determinist (1234) — reproducibile, dar nu independente între agenți.

## Lucruri de evitat

- Nu importați din `src/` în stiva safe-navigation și invers; păstrați izolarea.
- Nu confundați cele două `EpisodeResult` (vezi docstring-urile pentru distincție).
- Nu adăugați comenzi noi de lint/build/test fără un motiv concret legat de task.
- Nu scrieți teste sub `pytest` fără configurare; respectați stilul script-style din `tests/`.
