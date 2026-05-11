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

# Cum alegi strategia de navigare potrivită pentru un robot autonom?

## Simulator pentru evaluarea comparativă a strategiilor de navigare sigură

---

**Autor:** Andrei Demit  
**Coordonator științific:** Lect. univ. dr. Florentina Suter  
**Universitatea:** Universitatea din București  
**Facultatea:** Facultatea de Matematică și Informatică  
**Sesiunea:** 2026

---

# De ce contează navigarea sigură?

Sistemele autonome operează astăzi în medii unde un traseu greșit are consecințe reale:

- 🏭 **roboți de depozit** (Amazon, DHL) — coliziunile opresc linii întregi de producție;
- 🚁 **drone de livrare** — zonele interzise înseamnă accidente sau pierderea echipamentului;
- 🏥 **roboți medicali** — un obstacol nedetectat poate pune pacienți în pericol;
- 🚗 **vehicule autonome** — traseul scurt nu este întotdeauna cel mai sigur.

> **Întrebarea relevantă nu este „agentul a ajuns?", ci „cum a ajuns?"**

---

# Ideea centrală

GPS-ul clasic îți dă **drumul cel mai scurt**. Dar în logistică, medicină sau apărare, contează și:

- câte zone periculoase a traversat traseul?
- câte coliziuni s-au produs?
- care este costul operațional total?

Lucrarea construiește un **cadru de evaluare comparativă** care răspunde la:

> **Care strategie navighează mai sigur, mai eficient și mai robust în medii necunoscute?**

---

# Scopul lucrării

Un **simulator** care permite:

1. generarea de medii realiste cu obstacole, zone periculoase și incertitudine;
2. rularea și compararea mai multor strategii de navigare în aceleași condiții;
3. măsurarea nu doar a succesului, ci a **profilului complet de risc și cost**;
4. reproducerea experimentelor și exportul rezultatelor pentru analiză.

---

# De ce nu este suficient succesul?

Două strategii pot ajunge la destinație, dar cu profiluri de risc complet diferite:

| Strategie | Ajunge la țintă | Risc acumulat | Cost | Adecvat pentru |
|---|---:|---:|---:|---|
| Drum scurt (A*) | Da | Mare | Mediu | livrare rapidă, mediu controlat |
| Drum sigur (Risk-Aware A*) | Da | Mic | Mic | operațiuni critice, medii cu persoane |

**Concluzie:** alegerea strategiei corecte depinde de contextul operațional, nu doar de destinație.

Un depozit automatizat și un robot medical au același tip de problemă, dar criterii de siguranță diferite.

---

# Modelul de mediu

Mediul este un **GridWorld generat procedural** — o abstractizare a planurilor de etaj, depozite sau hărți de navigare.

| Celulă | Rol | Analog real |
|---|---|---|
| Empty | spațiu liber | coridor, alee |
| Wall | obstacol, coliziune | perete, raft, mașinărie |
| Danger | zonă periculoasă, terminală | zonă cu persoane, suprafață periculoasă |
| Start | poziția inițială | punct de plecare robot |
| Goal | destinația | zona de livrare, stație de andocare |

Hărțile sunt validate prin BFS — garantând că există întotdeauna un drum posibil.

Parametrul `movement_noise` simulează incertitudinea din execuție (roți patinate, drift de senzor).

---

# Structura recompenselor

Recompensele reflectă trade-off-urile din lumea reală: **rapiditate vs. siguranță**.

| Eveniment | Valoare | Justificare operațională |
|---|---:|---|
| goal | +100 | misiunea a fost îndeplinită |
| danger (terminal) | −100 | incident critic, cost maxim |
| wall (coliziune) | −10 | avarie echipament |
| pas normal | −1 | cost energetic / timp |
| mai aproape de goal | +2 | progres spre destinație |
| mai departe de goal | −2 | detour ineficient |

Recompensele de formare (`closer`/`farther`) accelerează învățarea fără a schimba politica optimă.

---

# Componenta de risc

Simulatorul nu marchează doar celulele periculoase — calculează o **zonă de influență** a riscului:

| Distanță Manhattan față de DANGER | Cost de risc |
|---:|---:|
| 0 (celulă DANGER) | 100.0 |
| 1 | 10.0 |
| 2 | 5.0 |
| 3 | 2.0 |

Aceasta modelează realitatea: **apropierea de o zonă periculoasă are cost chiar fără intrare directă** (zona de siguranță din jurul echipamentelor industriale, distanța față de persoane).

`RiskAwareAStarAgent` include acest cost în planificare. Riscul acumulat este urmărit independent de recompensă.

---

# Strategii comparate

Fiecare strategie modelează o paradigmă diferită de luare a deciziei:

| Strategie | Paradigmă | Când este potrivită |
|---|---|---|
| Random | baseline | referință statistică |
| Rule-Based | euristică locală | resurse limitate, reacție rapidă |
| A* | planificare globală | hartă complet cunoscut, viteză prioritară |
| Risk-Aware A* | planificare sigură | operațiuni critice, prezența persoanelor |
| Tabular Q-Learning | RL pe coordonate | mediu fix, repetitiv (ex. acelaşi depozit) |
| Feature-Based Q-Learning | RL transferabil | medii variate, generalizare necesară |

---

# Profiluri experimentale — scenarii de deployment

Fiecare profil reproduce un context operațional real:

| Profil | Context real | Strategie avantajată |
|---|---|---|
| `known_static` | depozit cu plan fix, harta cunoscută | A*, Risk-Aware A* |
| `high_risk` | teren cu zone interzise, siguranță prioritară | Risk-Aware A* |
| `stochastic_execution` | roboți cu imprecizie mecanică, drift | robustețe > precizie |
| `same_map_learning` | robot care operează repetat în același spațiu | Tabular Q-Learning |
| `transfer_learning` | flotă de roboți pe locații diferite | Feature-Based Q-Learning |
| `training_cost` | cost de antrenare vs. decizie rapidă | A* fără training vs. RL cu training |

> **Nu există o strategie universal optimă** — contextul operațional determină alegerea.

---

# Arhitectura simulatorului

```text
environment/
  GridWorld, MapGenerator, RiskModel, RewardConfig
  scenarii: easy (10×10), medium (15×15), hard (20×20)

agents/
  Random, Rule-Based, A*, Risk-Aware A*,
  Tabular Q-Learning, Feature-Based Q-Learning

simulation/
  Simulator, EpisodeResult, Metrics
  (metrici cu CI95% bootstrap, percentile, per-map)

experiments/
  6 profiluri Monte Carlo, comparație agenți

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

Metricile reflectă **standardele de evaluare din siguranța sistemelor autonome**:

| Metrică | Ce măsoară | Relevanță operațională |
|---|---|---|
| `success_rate` | episoade reușite | KPI principal de misiune |
| `average_steps` | lungimea traseului | eficiența energetică / timp |
| `average_collisions` | impacturi cu obstacole | avarii de echipament |
| `average_danger_entries` | intrări în zone periculoase | incidente de siguranță |
| `average_risk_exposure` | risc acumulat pe traseu | cost de siguranță total |
| `average_total_cost` | `−reward + risk` | cost operațional compozit |
| `timeout_rate` | misiuni neterminate | disponibilitate sistem |
| `average_computation_time_ms` | timp de decizie | fezabilitate real-time |

Toate metricile includ CI95% bootstrap și defalcare per hartă.

---

# Experiment Monte Carlo

Configurație folosită pentru documentație:

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

Profilul `known_static` evaluează toți agenții cu hartă complet cunoscută, condiții deterministe.

---

# Rezultate: algoritmi de planificare

Aceeași rată de succes, profil de risc diferit — **tocmai de aceea succesul singur nu ajunge**:

| Algoritm | Success | Pași | Risc acumulat | Cost total |
|---|---:|---:|---:|---:|
| A* | 100% | 28.4 | 161.0 | 195.4 |
| Risk-Aware A* | 100% | 29.6 | 125.0 | 124.6 |

**Risk-Aware A*** acceptă un traseu cu 4% mai lung, dar reduce riscul cu **22%** și costul total cu **36%**.

> Într-un context operațional cu persoane prezente sau echipamente sensibile, această diferență poate fi decisivă.

---

# Rezultate: baseline și RL pe hărți noi

| Algoritm | Success | Coliziuni | Pericole | Timeout |
|---|---:|---:|---:|---:|
| Random | 0% | 40.7 | 1.0 | 0% |
| Rule-Based | 50% | 0.0 | 0.0 | 50% |
| Tabular Q | 0% | 23.8 | 1.0 | 0% |
| Feature-Based Q | 0% | 31.4 | 0.8 | 20% |

**Interpretare:** agenții RL au nevoie de mai mult training sau de hărți familiare pentru a performa — confirmat de profilul `same_map_learning` unde Tabular Q-Learning devine relevant.

**Rule-Based** evită coliziunile complet, dar se blochează în 50% din cazuri — compromis tipic pentru euristici reactive.

---

# Concluzia experimentală principală

**Nu există o strategie universală** — alegerea depinde de contextul operațional:

| Context | Strategie recomandată | Motivul |
|---|---|---|
| Hartă complet cunoscută, viteză importantă | A* | cel mai scurt drum |
| Prezența persoanelor / zone critice | Risk-Aware A* | risc cu 22% mai mic |
| Același spațiu repetat (depozit fix) | Tabular Q-Learning | se specializează pe locație |
| Locații variate, hartă necunoscută | Feature-Based Q-Learning | transferă tipare locale |
| Resurse de calcul minime | Rule-Based | euristic, fără planificare |

Simulatorul permite **cuantificarea acestor diferențe înainte de deployment**, nu după.

---

# Componenta Q-Learning energetică — AI interpretabil

Un studiu de caz pentru **reinforcement learning interpretabil și auditabil**:

- stare: `(rând, coloană, nivel_energie)` — direct inspecționabil;
- energie discretizată în 4 buckets — același loc, 4 politici diferite în funcție de resurse;
- Q-table de `20 × 20 × 4 × 5 = 8.000` intrări — compactă, explicabilă;
- scenarii A (energie infinită), B (energie limitată), C (obstacole dinamice), WAREHOUSE.

**Relevanță reală:** sistemele critice au nevoie de AI care poate fi auditat — nu o rețea neuronală cu milioane de parametri, ci o politică care poate fi citită și verificată.

---

# Rezultate Q-Learning energetic

| Scenariu | Success last 100 | Greedy pași | Energie finală | Ce demonstrează |
|---|---:|---:|---:|---|
| A (energie infinită) | 100% | 34 | 88 | convergență de bază |
| B (energie limitată) | 96% | 38 | 84 | navigare conștientă de resurse |
| C (obstacole dinamice) | 100% | 12 | 88 | adaptare la schimbări de mediu |
| WAREHOUSE (20×20 fix) | 100% | 77 | 67 | specializare pe hartă reală |

Q-Learning tabular demonstrează că **un agent simplu și interpretabil poate rezolva navigare cu constrângeri de resurse** — relevant pentru sisteme embedded cu putere computațională limitată.

---

# Interfața web — simulator accesibil

Aplicația web transformă simulatorul dintr-un script de cercetare într-un instrument utilizabil:

- **configurare vizuală** a scenariului, profilului și algoritmilor;
- **generare și vizualizare** hartă cu heatmap de risc suprapus;
- **comparație Monte Carlo** cu statistici extinse per algoritm;
- **analiză avansată:** distribuții (reward, steps, risk), CI95%, heatmap per hartă, scatter risc-recompensă, heatmap de ocupanță, breakdown eșecuri;
- **export CSV/PNG** pentru raportare și prezentări;
- **laborator Q-Learning energetic** pentru studiul interpretabilității.

> Un cercetător sau inginer poate rula comparații fără a scrie cod.

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

# Aplicabilitate și extensibilitate

Simulatorul este proiectat să fie adaptat la domenii specifice:

| Domeniu | Adaptare necesară | Ce rămâne neschimbat |
|---|---|---|
| Depozite automatizate | hartă reală din blueprint | toți agenții, metricile |
| Drone de livrare | zone interzise ca DANGER | Risk-Aware A*, metrici risc |
| Roboți medicali | cost coliziune mai mare | RewardConfig, framework |
| Vehicule autonome | `movement_noise` mai mare | profilul `stochastic_execution` |

Arhitectura modulară (environment / agents / simulation / experiments) permite înlocuirea oricărui component fără a reface întregul sistem.

---

# Limitări și direcții de extindere

**Limitările actuale** sunt deliberate pentru o teză de licență:

- GridWorld este discret — nu înlocuiește simulatoare fizice (ROS, Gazebo), ci le **precedă** pentru selecția strategiei;
- agenți single-agent — multi-agent este extensia naturală pentru flote de roboți;
- RL tabular generalizează limitat — DQN sau PPO sunt pași următori pentru grile mari.

**Direcții concrete de extindere:**

- import de hărți reale (YAML, imagine bitmap) în locul generării procedurale;
- agenți multi-agent cu negociere de trasee;
- variante DQN/PPO pentru spații de stare continue;
- medii parțial observabile (senzori cu rază limitată);
- obstacole dinamice (persoane, alte vehicule).

---

# Concluzie

Lucrarea construiește un **cadru de evaluare comparativă** pentru strategii de navigare sigură.

Valoarea principală: permite să răspunzi la întrebarea practică înainte de deployment —

> **„Dată fiind misiunea și constrângerile mele de siguranță, care strategie merită implementată?"**

Răspunsul nu este universal: depinde de cât de critice sunt zonele periculoase, dacă harta este cunoscută sau nu, dacă robotul operează în locații repetate sau variate.

Simulatorul face aceste diferențe **măsurabile, reproductibile și comunicabile**.

---

# Mulțumesc!

**Teză de licență:** Simulator Grid-Based pentru Evaluarea Strategiilor de Navigare Sigură în Medii Generate Procedural

*Cod sursă, experimente și rezultate disponibile în repository.*
