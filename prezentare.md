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
  table { width: 100%; font-size: 23px; }
  th { background: #0369a1; color: white; }
  td { background: #ffffff; color: #111827; border-color: #cbd5e1; }
---

# Cum alegi strategia de navigare potrivită într-un mediu necunoscut?

## Simulator interactiv pentru evaluare și recomandare în navigare sigură

**Autor:** Andrei Demit  
**Coordonator științific:** Lect. univ. dr. Florentina Suter  
**Universitatea din București, FMI — 2026**

---

# Context și idee centrală

Sistemele autonome nu sunt evaluate doar după faptul că ajung la destinație, ci și după modul în care ajung acolo.

În logistică, medicină sau aplicații autonome contează:

- riscul acumulat pe traseu;
- coliziunile și intrările în zone periculoase;
- costul traseului și timpul de decizie;
- robustețea pe hărți necunoscute.

> **Întrebarea lucrării:** pentru un anumit tip de mediu și un anumit criteriu de siguranță, care strategie este cea mai potrivită?

---

# Scopul lucrării

Lucrarea construiește un **simulator grid-based utilizabil în timp real** pentru evaluarea strategiilor de navigare sigură.

Simulatorul permite:

1. generarea de hărți cu obstacole, zone periculoase și incertitudine;
2. rularea mai multor strategii în aceleași condiții;
3. evaluarea prin succes, risc, coliziuni, cost și timeout;
4. recomandarea strategiei potrivite pentru criteriile selectate;
5. reproducerea experimentelor prin seed-uri și Monte Carlo;
6. explicarea rezultatelor printr-un analist AI opțional, fără a schimba scorurile;
7. accesarea sistemului prin UI web, API și deployment cloud.

---

# Dimensiunea experimentală

Accentul nu cade pe implementarea izolată a unui algoritm, ci pe metodologia de evaluare.

| Dimensiune | Variantă simplă | În această lucrare |
|---|---|---|
| Mediu | hartă fixă | hărți generate procedural |
| Algoritmi | un singur agent | 6 strategii + hibrid experimental |
| Evaluare | succes / eșec | risc, cost, coliziuni, timeout |
| Reproducere | rulare manuală | seed-uri, Monte Carlo, export |
| Utilizare | script local | produs web interactiv + API + Azure |
| Decizie | interpretare manuală | recomandare pe baza metricilor + explicație AI opțională |

---

# Modelul de mediu

Mediul este un **GridWorld generat procedural**, validat prin BFS.

| Celulă | Rol | Analog real |
|---|---|---|
| Empty | spațiu liber | coridor, alee |
| Wall | obstacol | perete, raft, mașinărie |
| Danger | zonă periculoasă | zonă interzisă, persoane, risc operațional |
| Start | poziție inițială | punct de plecare |
| Goal | destinație | zonă de livrare / stație |

Parametrul `movement_noise` modelează incertitudinea execuției.

---

# Risc și recompense

Recompensele și riscul modelează trade-off-ul dintre rapiditate și siguranță.

| Element | Semnificație |
|---|---|
| `goal = +100` | misiunea este finalizată |
| `danger = -100` | incident critic |
| `wall = -10` | coliziune |
| `step = -1` | cost de timp / energie |
| `risk_weight` | penalizare proporțională cu apropierea de pericol |

Riscul nu apare doar în celula periculoasă: celulele apropiate de `DANGER` primesc cost suplimentar.

---

# Strategii comparate

| Algoritm | Rol | Când este potrivit |
|---|---|---|
| Random | baseline statistic | verifică dificultatea mediului |
| Rule-Based | baseline euristic | soluție simplă, explicabilă |
| A* | planificare globală | hartă cunoscută, drum scurt |
| Risk-Aware A* | planificare sigură | zone periculoase, persoane, cost mare al incidentelor |
| Tabular Q-Learning | RL pe coordonate | același mediu repetat |
| Feature-Based Q-Learning | RL pe features locale | medii variate, transfer de tipare |
| Feature-Risk A* | hibrid experimental | costuri locale învățate + planificare sigură |

Strategiile pot fi analizate individual sau ca parte a unui flux hibrid: învățarea ajustează costurile locale, iar planificarea caută ruta pe harta actualizată.

---

# Rolul algoritmilor

| Algoritm | Idee principală | Limitare |
|---|---|---|
| Random | alege aleator | nu folosește informații despre mediu |
| Rule-Based | evită riscul local și merge spre goal | se poate bloca fără planificare globală |
| A* | caută cel mai scurt drum | nu optimizează explicit riscul |
| Risk-Aware A* | include costul de risc în planificare | depinde de hartă și modelul de risc |
| Tabular Q | învață valori Q pe poziții absolute | generalizează slab pe hărți noi |
| Feature-Based Q | învață din pereți, pericole și direcția goal-ului | poate confunda contexte locale similare |

În produsul final, acești algoritmi nu sunt doar demonstrați separat, ci evaluați pentru a susține o alegere: rapiditate, siguranță, robustețe sau echilibru între criterii.

---

# Arhitectura simulatorului

```text
environment/
  GridWorld, MapGenerator, RiskModel, RewardConfig

agents/
  Random, Rule-Based, A*, Risk-Aware A*,
  Tabular Q-Learning, Feature-Based Q-Learning,
  Feature-Risk A* experimental

simulation/
  Simulator, EpisodeResult, Metrics

experiments/
  profiluri Monte Carlo, comparație agenți,
  ranking pe metrici, explicație, strategie recomandată

web/backend/llm_*.py
  Analist AI Gemma/Ollama pentru interpretarea rezultatelor,
  fără recalcularea recomandării

web/
  FastAPI backend + React frontend
```

---

# Metodologie experimentală

Experimentul Monte Carlo rulează agenții pe mai multe hărți generate procedural.

```bash
PYTHONPATH=. .venv/bin/python -m experiments.run_experiment \
  --scenario medium \
  --maps 5 \
  --episodes-per-map 2 \
  --training-episodes 100 \
  --seed 42 \
  --profile known_static
```

Rezultat: **60 episoade** agregate.

Metrici: succes, reward, pași, coliziuni, intrări în pericol, risc acumulat, cost total, timeout.

---

# Rezultate: A* vs Risk-Aware A*

În profilul `known_static`, ambele strategii ajung la țintă, dar cu profil diferit de risc și cost.

| Algoritm | Success | Pași | Risc acumulat | Cost total |
|---|---:|---:|---:|---:|
| A* | 100% | 28.4 | 161.0 | 195.4 |
| Risk-Aware A* | 100% | 29.6 | 125.0 | 124.6 |

Risk-Aware A* alege un traseu cu 4% mai lung, dar obține:

- risc cu **22%** mai mic;
- cost total cu **36%** mai mic.

---

# Rezultate: baseline și RL

| Algoritm | Success | Coliziuni | Pericole | Timeout |
|---|---:|---:|---:|---:|
| Random | 0% | 40.7 | 1.0 | 0% |
| Rule-Based | 50% | 0.0 | 0.0 | 50% |
| Tabular Q | 0% | 23.8 | 1.0 | 0% |
| Feature-Based Q | 0% | 31.4 | 0.8 | 20% |

Interpretare:

- Rule-Based evită coliziunile, dar se blochează des.
- Agenții RL sunt dezavantajați de training scurt și hărți noi.
- Tabular Q devine relevant în profilul `same_map_learning`.

---

# Componenta Q-Learning energetică

Pe lângă simulatorul safe-navigation, proiectul include un studiu de caz RL interpretabil:

- stare: `(rând, coloană, nivel_energie)`;
- energie discretizată în 4 buckets;
- Q-table de `20 × 20 × 4 × 5 = 8.000` intrări;
- scenarii A, B, C și WAREHOUSE.

| Scenariu | Success last 100 | Greedy pași | Observație |
|---|---:|---:|---|
| A | 100% | 34 | convergență de bază |
| B | 96% | 38 | constrângere energetică |
| C | 100% | 12 | mediu modificat |
| WAREHOUSE | 100% | 77 | hartă fixă industrială |

---

# Interfață web și deployment

Aplicația web transformă simulatorul într-un instrument utilizabil:

- configurare vizuală a scenariului și algoritmilor;
- vizualizare hartă + heatmap de risc;
- rulare Monte Carlo și analiză metrici;
- recomandare de strategie în funcție de obiectiv;
- panou Analist AI pentru explicarea recomandării și a compromisurilor;
- export CSV/PNG/JSON;
- laborator separat pentru Q-Learning energetic.

Deployment:

```text
Azure Static Web Apps  -> React/Vite frontend
Azure Container Apps   -> FastAPI backend + simulator Python
Azure Container Apps   -> Ollama/Gemma intern, opțional, pe profil GPU
Azure Files            -> rulări, artefacte, Q-table-uri
```

---

# Concluzie

Lucrarea propune un **simulator operațional** pentru evaluarea și alegerea strategiilor de navigare sigură.

Rezultatele arată că aceeași rată de succes poate ascunde diferențe importante de risc și cost.

În funcție de context:

- A* este potrivit pentru hartă cunoscută și traseu scurt;
- Risk-Aware A* este potrivit când siguranța contează mai mult;
- Tabular Q-Learning este potrivit pentru medii repetate;
- Feature-Based Q-Learning urmărește transferul pe hărți variate;
- Feature-Risk A* este o extensie experimentală pentru conectarea învățării locale cu planificarea;
- Rule-Based rămâne un reper simplu și explicabil.

Astfel, aplicația nu răspunde doar dacă un agent ajunge la țintă, ci ce strategie merită folosită pentru situația configurată.
