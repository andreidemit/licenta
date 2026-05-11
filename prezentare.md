---
marp: true
theme: default
paginate: true
backgroundColor: #f8fafc
color: #111827
style: |
  section {
    font-family: 'Segoe UI', sans-serif;
    background: #f8fafc;
    color: #111827;
  }
  h1 { color: #075985; border-bottom: 2px solid #0ea5e9; }
  h2 { color: #075985; background: #e0f2fe; padding: 4px 10px; border-left: 6px solid #0ea5e9; }
  h3 { color: #0369a1; }
  code { background: #e2e8f0; color: #0f172a; }
  strong { color: #0f766e; }
  blockquote {
    color: #334155;
    border-left: 6px solid #14b8a6;
    background: #f0fdfa;
    padding: 8px 16px;
  }
  table { width: 100%; font-size: 24px; }
  th { background: #0369a1; color: white; }
  td { background: #ffffff; color: #111827; border-color: #cbd5e1; }
---

# Simulator Grid-Based pentru Evaluarea Strategiilor de Navigare Sigură

## Medii necunoscute generate procedural

---

**Autor:** Andrei Demit  
**Coordonator științific:** Lect. univ. dr. Florentina Suter  
**Universitatea:** Universitatea din București  
**Facultatea:** Facultatea de Matematică și Informatică  
**Sesiunea:** 2026

---

# Ideea centrală

Lucrarea nu răspunde doar la întrebarea:

> Agentul a ajuns sau nu la destinație?

Ci la întrebarea mai relevantă:

> **Care strategie este mai potrivită pentru navigare sigură în medii necunoscute?**

---

# Scopul lucrării

Construirea unui **simulator grid-based** pentru evaluarea strategiilor de navigare sigură în medii generate procedural.

Evaluarea urmărește:

- rata de succes;
- riscul acumulat;
- coliziunile;
- costul traseului;
- eficiența;
- generalizarea pe hărți noi.

---

# De ce nu este suficient succesul?

Două strategii pot ajunge la țintă, dar pot avea profiluri diferite:

| Strategie | Ajunge la țintă | Risc | Cost | Observație |
|---|---:|---:|---:|---|
| Drum scurt | Da | Mare | Mediu | eficient, dar periculos |
| Drum sigur | Da | Mic | Mic/mediu | mai potrivit operațional |

Concluzia: **navigarea sigură este o problemă multi-criterială**.

---

# Modelul de mediu

Mediul este un GridWorld generat procedural.

| Celulă | Rol |
|---|---|
| Empty | spațiu liber |
| Wall | obstacol, coliziune |
| Danger | zonă periculoasă |
| Start | poziția inițială |
| Goal | destinația |

Hărțile sunt validate prin BFS pentru a garanta existența unui drum posibil.

---

# Componenta de risc

Simulatorul nu marchează doar celulele periculoase.

El calculează o **hartă de risc** în jurul lor:

- risc maxim în celulele `DANGER`;
- risc ridicat în vecinătatea imediată;
- risc descrescător pe măsură ce distanța crește;
- penalizare configurabilă prin `risk_weight`.

---

# Strategii comparate

| Strategie | Tip | Idee principală |
|---|---|---|
| Random | baseline | alege aleator |
| Rule-Based | euristică | evită pericole imediate |
| A* | planificare | caută traseu scurt |
| Risk-Aware A* | planificare sigură | optimizează distanță + risc |
| Tabular Q-Learning | RL | învață pe coordonate absolute |
| Feature-Based Q-Learning | RL | învață pe features locale |

---

# Arhitectura simulatorului

```text
environment/
  GridWorld, MapGenerator, RiskModel

agents/
  Random, Rule-Based, A*, Risk-Aware A*, Q-Learning

simulation/
  Simulator, EpisodeResult, Metrics

experiments/
  Monte Carlo, comparație agenți

web/
  FastAPI backend + React frontend
```

---

# Fluxul unui episod

1. Se generează sau se încarcă o hartă.
2. Agentul primește observația curentă.
3. Agentul alege acțiunea.
4. Mediul aplică tranziția.
5. Se actualizează recompensa, riscul și metricile.
6. Episodul continuă până la goal, pericol sau timeout.

---

# Metrici urmărite

| Metrică | Ce măsoară |
|---|---|
| `success_rate` | procentul episoadelor reușite |
| `average_steps` | eficiența traseului |
| `average_collisions` | interacțiuni cu obstacole |
| `average_danger_entries` | intrări în zone periculoase |
| `average_risk_exposure` | risc acumulat |
| `average_total_cost` | cost global al traseului |
| `timeout_rate` | eșec prin depășirea pașilor |

---

# Experiment Monte Carlo

Configurație folosită pentru documentație:

```bash
PYTHONPATH=. .venv/bin/python -m experiments.run_experiment \
  --scenario medium \
  --maps 5 \
  --episodes-per-map 2 \
  --training-episodes 100 \
  --seed 42
```

Rezultat: **60 episoade** agregate.

---

# Rezultate: algoritmi de planificare

| Algoritm | Success | Pași | Risc | Cost |
|---|---:|---:|---:|---:|
| A* | 100% | 28.4 | 161.0 | 195.4 |
| Risk-Aware A* | 100% | 29.6 | 125.0 | 124.6 |

Interpretare:

**Risk-Aware A*** acceptă un traseu puțin mai lung, dar reduce riscul și costul total.

---

# Rezultate: baseline și RL

| Algoritm | Success | Coliziuni | Pericole | Timeout |
|---|---:|---:|---:|---:|
| Random | 0% | 40.7 | 1.0 | 0% |
| Rule-Based | 50% | 0.0 | 0.0 | 50% |
| Tabular Q | 0% | 23.8 | 1.0 | 0% |
| Feature-Based Q | 0% | 31.4 | 0.8 | 20% |

Interpretare: în evaluări scurte pe hărți noi, planificarea cu hartă completă este avantajată.

---

# Concluzia experimentală principală

Succesul singur ascunde diferențe importante.

În scenariul `medium`:

- A* și Risk-Aware A* au aceeași rată de succes;
- Risk-Aware A* are risc acumulat mai mic;
- Risk-Aware A* are cost total mai mic;
- deci strategia mai potrivită depinde de criteriile de siguranță, nu doar de destinație.

---

# Componenta Q-Learning energetică

Proiectul păstrează și o componentă RL interpretabilă:

- agent Q-Learning tabular;
- stare: `(rând, coloană, nivel_energie)`;
- energie discretizată în 4 buckets;
- scenarii A, B, C și WAREHOUSE;
- Q-table de `20 × 20 × 4 × 5 = 8.000` intrări.

Rol: studiu de caz pentru învățare prin consolidare și homeostazie energetică.

---

# Rezultate Q-Learning energetic

| Scenariu | Success last 100 | Greedy pași | Energie finală |
|---|---:|---:|---:|
| A | 100% | 34 | 88 |
| B | 96% | 38 | 84 |
| C | 100% | 12 | 88 |
| WAREHOUSE | 100% | 77 | 67 |

Q-Learning demonstrează comportament interpretabil, dar nu este singura strategie a sistemului.

---

# Interfața web

Aplicația web oferă:

- configurarea scenariului;
- alegerea algoritmului;
- generare de hărți;
- vizualizarea traseului;
- hartă de risc;
- metrici pe episod;
- comparație Monte Carlo;
- laborator separat pentru Q-Learning energetic.

---

# Deployment

Arhitectura cloud:

```text
Azure Static Web Apps
  React/Vite frontend

Azure Container Apps
  FastAPI backend + simulator Python

Azure Files
  rulări, artefacte, Q-table-uri

Application Insights
  loguri și observabilitate
```

---

# Legătura cu tehnici de simulare

Proiectul include:

- simulare bazată pe agenți;
- medii parametrizabile;
- hărți generate procedural;
- rulări repetate;
- seed-uri reproductibile;
- evaluare Monte Carlo;
- comparație statistică între strategii;
- analiză comportamentală prin metrici.

---

# Limitări

- GridWorld este o abstractizare discretă, nu robotică fizică reală.
- Agenții sunt single-agent.
- RL tabular generalizează limitat pe hărți noi.
- Experimentele Monte Carlo pot fi extinse cu mai multe hărți și episoade.
- Aplicația cloud este prototip demonstrativ, nu produs de producție.

---

# Direcții viitoare

- mai multe scenarii procedurale;
- antrenare mai lungă pentru agenții RL;
- variante DQN pentru grile mari;
- medii parțial observabile;
- agenți multipli;
- obstacole dinamice;
- analiză statistică mai amplă pe distribuții de hărți.

---

# Concluzie

Lucrarea construiește un simulator pentru evaluarea strategiilor de navigare sigură.

Valoarea proiectului este că transformă problema din:

> **a ajuns agentul la destinație?**

în:

> **care strategie navighează mai sigur, mai eficient și mai robust în medii necunoscute?**

---

# Mulțumesc!

**Teză de licență:** Simulator Grid-Based pentru Evaluarea Strategiilor de Navigare Sigură în Medii Generate Procedural
