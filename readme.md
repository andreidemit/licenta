# Simularea Comportamentului Inteligent și Navigare Autonomă

## Direcția curentă: Safe Navigation Simulator

**Titlu conceptual:** „Simularea și evaluarea strategiilor de navigare sigură pentru agenți autonomi în medii grid-based necunoscute”.

Proiectul a fost extins dintr-un demo centrat pe Q-Learning într-un cadru modular de simulare. Q-Learning-ul rămâne disponibil, dar este acum doar una dintre strategiile comparate în același simulator, alături de agenți euristici și algoritmi de planificare.

### Arhitectura nouă

| Strat | Fișiere principale | Rol |
|---|---|---|
| Environment | `environment/grid_world.py`, `environment/map_generator.py`, `environment/cell_types.py`, `environment/risk_model.py` | Reprezentarea hărții, reward-ul, riscul și generarea procedurală BFS-validată |
| Agents | `agents/base_agent.py`, `agents/random_agent.py`, `agents/rule_based_agent.py`, `agents/astar_agent.py`, `agents/q_learning_agent.py`, `agents/feature_q_learning_agent.py` | Strategii interschimbabile rulate de același simulator |
| Simulation | `simulation/simulator.py`, `simulation/episode_result.py`, `simulation/actions.py`, `simulation/metrics.py` | Motor generic de episod, acțiuni comune, tranziții și metrici |
| Experiments | `experiments/compare_agents.py`, `experiments/run_experiment.py`, `experiments/configs.py` | Evaluări Monte Carlo și comparații între algoritmi |
| UI/API | `web/backend/app.py`, `web/frontend/src/features/safe-navigation/*` | Endpoint-uri și interfață React pentru simulatorul experimental |

Separarea importantă este că reward-ul aparține mediului (`GridWorld.step()`), agenții aleg acțiuni printr-o interfață comună (`BaseAgent`), iar `Simulator` poate rula orice agent fără să știe dacă acesta învață sau planifică.

### Algoritmi implementați

- **RandomAgent** — baseline simplu, alege aleator.
- **RuleBasedAgent** — evită pereți/pericole imediate și se apropie de goal.
- **AStarAgent** — planifică rapid drumuri pe hărți noi cu euristică Manhattan.
- **RiskAwareAStarAgent** — extinde A* cu hartă de risc; preferă trasee mai sigure chiar dacă sunt mai lungi.
- **TabularQLearningAgent** — Q-table pe coordonate absolute; util pe harta de training, dar generalizează slab la hărți noi.
- **FeatureBasedQLearningAgent** — Q-learning pe features locale: pereți, pericole, direcția goal-ului și bucket de distanță, pentru transfer mai bun pe hărți necunoscute.

Nu există DQN sau rețele neuronale; scopul este simularea, comparația și evaluarea strategiilor, nu deep learning.

### Metrici

Pentru fiecare episod se colectează: `success`, `total_reward`, `steps`, `collisions`, `danger_entries`, `total_risk_exposure`, `path_length`, `timeout`, `reached_goal`, `computation_time_ms`.

Pentru evaluări agregate se calculează: `success_rate`, `average_reward`, `average_steps`, `average_collisions`, `collision_rate`, `average_danger_entries`, `danger_entry_rate`, `average_risk_exposure`, `average_total_cost`, `timeout_rate`, `average_computation_time_ms`.

### Rulare simulator web

```bash
python -m pip install -r web/backend/requirements.txt
python -m web.backend

cd web/frontend
npm install
npm run dev
```

Pagina principală (`/`) este acum **Safe Navigation Simulator**. Laboratorul vechi Q-Learning rămâne disponibil sub `/lab`.

În UI poți:

- alege algoritmul;
- genera hărți random easy/medium/hard/custom;
- rula un episod și vedea traseul;
- activa/dezactiva path, risk heatmap și coordonate;
- compara A* cu Risk-Aware A*;
- rula Tabular Q-Learning pe o hartă fixă și observa limitele pe hărți noi;
- rula Monte Carlo comparison între agenți și vedea tabel/grafice simple.

### Rulare Monte Carlo din CLI

```bash
PYTHONPATH=. python -m experiments.run_experiment \
  --scenario medium \
  --maps 5 \
  --episodes-per-map 2 \
  --training-episodes 100
```

### Poveste experimentală susținută

1. Tabular Q-Learning învață bine o hartă fixă.
2. Când harta se schimbă, performanța scade deoarece starea este coordonata absolută.
3. A* găsește rapid drumuri pe hărți noi, dar optimizează mai ales distanța.
4. Risk-Aware A* poate alege un traseu mai lung, dar cu expunere mai mică la risc.
5. Feature-Based Q-Learning învață tipare locale de siguranță care pot fi reutilizate pe hărți nevăzute.
6. Monte Carlo evaluation permite comparații statistice robuste între algoritmi și dificultăți de mediu.

### Config exemplu

```json
{
  "scenario": "medium",
  "rows": 15,
  "cols": 15,
  "wall_probability": 0.2,
  "danger_probability": 0.1,
  "movement_noise": 0.0,
  "max_steps": 300,
  "risk_weight": 1.0,
  "training_episodes": 500,
  "test_episodes": 100,
  "random_seed": 42
}
```

---

**Titlu**: Simularea comportamentului inteligent: Navigare și supraviețuire autonomă bazată pe interacțiunea cu mediul.

**Descriere**: Această lucrare își propune dezvoltarea unei aplicații software pentru simularea și analiza proceselor cognitive de învățare într-un sistem bazat pe agenți autonomi. Spre deosebire de abordările clasice bazate pe seturi de date statice (Supervised Learning), proiectul se concentrează pe paradigma Învățării prin Consolidare (Reinforcement Learning). Agentul virtual va fi plasat într-un mediu necunoscut și va trebui să își dezvolte propria 'înțelegere' a lumii prin interacțiune directă (încercare și eroare). Obiectivul principal este implementarea algoritmului Q-Learning pentru a permite agentului să învețe relațiile cauzale dintre obiecte (obstacole, resurse) și consecințe (recompense, penalizări), simulând astfel procese cognitive fundamentale precum memoria, curiozitatea (explorarea) și planificarea. Aplicația va include o interfață grafică pentru vizualizarea în timp real a procesului de învățare și a evoluției performanței agentului în scenarii cu grade variate de complexitate.

Prin acest document detaliez arhitectura simulării, punând un accent major pe modelarea matematică a entităților, dinamica mediului, fluxurile de date și mecanismele de interacțiune.

---

## Ce vrem să obținem

### Obiectiv principal
O aplicație funcțională care demonstrează că un agent software poate **învăța singur** să navigheze și să supraviețuiască într-un mediu necunoscut, fără nicio programare explicită a regulilor — exclusiv prin interacțiune repetată cu mediul și feedback numeric (recompense/penalizări).

La finalul antrenamentului, agentul trebuie să fie capabil să:
- Găsească drumul optim (sau aproape optim) de la start la țintă;
- Gestioneze resursele limitate (energie) fără să moară înainte de a ajunge la țintă;
- Se adapteze parțial la schimbări ale mediului după antrenament.

### Rezultate concrete așteptate

| Livrabil | Descriere |
|---|---|
| **Aplicație Python/Pygame** | Simulare vizuală interactivă cu GUI |
| **Q-Table antrenată** | Politică optimă salvată pentru fiecare scenariu |
| **Export CSV** | Metrici per episod: pași, reward, epsilon, outcome |
| **Grafice convergență** | Rolling average reward — dovada că agentul a învățat |
| **3 scenarii validate** | A (navigare), B (supraviețuire), C (adaptabilitate) |

### Ce NU face proiectul (limitări asumate)
- Nu folosește rețele neuronale (Deep Q-Learning / DQN) — Q-Learning tabular clasic.
- Nu generalizează la medii complet nevăzute — agentul memorează o politică optimă per configurație de hartă, nu abstractizează reguli universale. Aceasta este o caracteristică a RL tabular, nu un defect de implementare.
- Nu pretinde să rezolve probleme de inteligență generală (cf. benchmark-uri precum ARC-AGI-3, 2026). Scopul este demonstrarea mecanismelor fundamentale de învățare prin interacțiune.

---

## Rulare recomandată pentru pachetul final

```bash
# regenerează experimentele standard și sumarul final
python -m src.final_report --episodes 2000 --save-qtables

# exportă și artefacte de observabilitate pentru o rulare scurtă
python -m src.main --train --episodes 50 --export-visuals --export-trajectory

# UI web experimental: backend FastAPI + frontend React
python -m pip install -r web/backend/requirements.txt
python -m web.backend

cd web/frontend
npm install
npm run dev

# demo vizual scurt
python -m src.main --train --scenario B --episodes 50 --visualize
```

Pentru evaluarea finală, fluxul recomandat este să regenerezi mai întâi artefactele standard din `data/`, apoi să folosești demo-ul scurt doar pentru ilustrare vizuală. Rulările sub 50 de episoade sunt utile pentru smoke checks, dar nu pentru raportarea rezultatelor finale.

Artefactele de observabilitate includ manifest JSON reproductibil, traseu lacom CSV/JSON și imagini PNG pentru hartă, politică, max-Q, vizite, eroare TD și traseul lacom final. Directorul de ieșire poate fi schimbat cu `--out-dir`.

În modul `--visualize`, feedback-ul în timp real este limitat intenționat la o viteză ușor de urmărit și include controale de redare: `SPACE` pauză/reluare, `.` avansează un singur pas când simularea este în pauză, iar `-`/`+` schimbă viteza. Panoul lateral este organizat pe carduri pentru agent, ultimul pas, progresul învățării, suprapuneri vizuale și controale. Indicatorul de pe grid arată ultima acțiune, recompensa pasului, delta de energie și eroarea TD. Suprapunerile pot fi schimbate cu `H/P/V/T/K/L/E`.

UI-ul web din `web/` este direcția recomandată pentru demo pe tot ecranul și fluxul complet: antrenare din browser, transmitere în timp real, panou React, salvare tabel Q și evaluare lacomă pe medii JSON noi. Backend-ul reutilizează motorul Python existent, deci algoritmul Q-Learning nu este rescris în JavaScript.

Frontend-ul folosește React Router cu pagini dedicate pentru fiecare flux:

- `/` — panoul de start cu acces rapid la toate funcțiile;
- `/antrenare` — formular cu previzualizare hartă, plus mod live fullscreen cu HUD pentru episodul curent;
- `/rulari` — listă filtrabilă de experimente (carduri sau tabel);
- `/rulari/:id` — detaliu cu sumar, grafice PNG, manifest JSON și descărcare artefacte;
- `/evaluare` — flux în 3 pași (alege tabel Q → alege scenariu → urmărește replay-ul cu HUD, timeline scrubable și viteză 0.5×–4×);
- `/editor-mediu` — pictează celule cu unealta selectată, validează drumul cu BFS, salvează ca JSON;
- `/comparatie` — selectează până la 4 rulări pentru comparație multi-run;
- `/legacy` — UI-ul vechi este păstrat ca fallback până la validarea utilizatorului.

Stack-ul UI: Tailwind CSS 3 + componente shadcn-style peste primitive Radix, framer-motion pentru animații, grafice SVG interne, react-router pentru navigare. Toate animațiile respectă `prefers-reduced-motion`.

În varianta web, rulările finalizate sunt indexate în `data/runs/index.json`, tabelele Q pot fi selectate direct din browser, iar artefactele unei rulări pot fi descărcate din panou. Editorul de medii permite vopsirea celulelor prin click pentru `Liber/Obstacol/Noroi/Hrană/Pericol/Pornire/Țintă`, validare BFS prin backend și salvare ca JSON sub `data/environments/`. Evaluarea acceptă fie un singur mediu JSON, fie o listă JSON de medii pentru comparații pe lot; traseul lacom selectat este suprapus pe grid.

```bash
# teste API web
python -m tests.test_web_api
```

## Deployment Azure recomandat

Pentru publicarea online a aplicației web, arhitectura recomandată este:

```text
Azure Static Web Apps
  React/Vite frontend din web/frontend

Azure Container Apps
  FastAPI backend din web/backend
  SSE live stream + training/evaluare Q-Learning

Azure Files
  mount la /app/data pentru runs, qtables, CSV/PNG/JSON, environments

Azure Container Registry
  imagine Docker backend

Azure Monitor + Application Insights + Log Analytics
  loguri backend, erori, lifecycle training job, health/cost visibility
```

### Fișiere de deployment incluse

| Fișier | Rol |
|---|---|
| `Dockerfile` | Construiește backend-ul FastAPI cu `src/` și `web/backend/` în aceeași imagine |
| `.dockerignore` | Exclude `data/`, `node_modules`, build outputs și fișiere locale din imagine |
| `infra/main.bicep` | Definește Static Web App, ACR, Storage Account/File Share, Log Analytics, Application Insights, Container Apps Environment și Container App |
| `infra/main.parameters.example.json` | Exemplu de parametri pentru infrastructură |
| `web/frontend/public/staticwebapp.config.json` | Fallback pentru React Router și headers pentru Static Web Apps |
| `web/frontend/.env.example` | Exemplu local pentru `VITE_API_URL` |
| `.github/workflows/azure-infra.yml` | Provisioning Bicep din GitHub Actions, fără Azure CLI local |
| `.github/workflows/azure-backend.yml` | Build/push imagine backend în ACR și update Container App |
| `.github/workflows/azure-frontend.yml` | Build React și deploy în Azure Static Web Apps |
| `scripts/validate_azure_local.sh` | Rulează testele locale, build frontend și smoke Docker când există Docker |
| `scripts/azure_smoke_test.sh` | Verifică health, CORS și rutele frontend după deployment |

### Variabile backend

| Variabilă | Local implicit | Azure recomandat |
|---|---:|---|
| `APP_ENV` | `development` | `production` |
| `HOST` | `127.0.0.1` | `0.0.0.0` |
| `PORT` | `8000` | `8000` |
| `DATA_ROOT` | `data` | `/app/data` |
| `CORS_ORIGINS` | `*` | URL-ul Azure Static Web Apps |
| `APPLICATIONINSIGHTS_CONNECTION_STRING` | absent | din Application Insights |

### Comenzi locale Docker

```bash
./scripts/validate_azure_local.sh

# sau manual:
docker build -t qlearning-backend .
docker run --rm -p 8000:8000 \
  -e APP_ENV=production \
  -e HOST=0.0.0.0 \
  -e PORT=8000 \
  -e DATA_ROOT=/app/data \
  -v "$(pwd)/data:/app/data" \
  qlearning-backend

curl http://127.0.0.1:8000/api/health
```

### Provisioning Azure cu Bicep

Poți face provisioning-ul direct din GitHub Actions cu workflow-ul **Provision Azure infrastructure**. Este varianta recomandată dacă nu vrei să rulezi Azure CLI local.

Pași:

1. Configurează în GitHub secrets OIDC: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.
2. Rulează manual workflow-ul `.github/workflows/azure-infra.yml`.
3. Copiază output-urile din workflow summary în GitHub variables:
   - `AZURE_RESOURCE_GROUP`
   - `AZURE_CONTAINER_APP_NAME`
   - `AZURE_CONTAINER_REGISTRY`
   - `AZURE_STATIC_WEB_APP_NAME`
   - `VITE_API_URL`

Notă: identitatea Azure folosită de GitHub Actions trebuie să poată crea resource group-ul sau să aibă acces Contributor pe resource group-ul existent.

### Configurare OIDC pentru GitHub Actions

Dacă workflow-ul eșuează la pasul **Azure login**, cauza este aproape întotdeauna una dintre acestea:

1. `AZURE_CLIENT_ID`, `AZURE_TENANT_ID` sau `AZURE_SUBSCRIPTION_ID` lipsește ori este copiat greșit.
2. App Registration-ul din Azure nu are federated credential pentru repository/branch.
3. Identitatea nu are rolurile Azure necesare.

Configurare recomandată în Azure Portal:

1. Intră în **Microsoft Entra ID → App registrations → New registration**.
2. Copiază:
   - **Application (client) ID** → `AZURE_CLIENT_ID`
   - **Directory (tenant) ID** → `AZURE_TENANT_ID`
   - Subscription ID din Azure subscription → `AZURE_SUBSCRIPTION_ID`
3. În App Registration: **Certificates & secrets → Federated credentials → Add credential**.
4. Alege **GitHub Actions deploying Azure resources**.
5. Setează repository-ul și branch-ul folosit la deploy (`main` sau `master`).
6. Subject-ul trebuie să arate așa:

```text
repo:<owner>/<repo>:ref:refs/heads/main
```

Pentru branch `master`:

```text
repo:<owner>/<repo>:ref:refs/heads/master
```

Workflow-urile afișează acum subject-ul așteptat înainte de `azure/login`, ca să îl poți copia exact.

Roluri Azure necesare:

- Pentru provisioning complet din workflow: **Contributor** pe subscription sau resource group.
- Pentru role assignment-ul ACR Pull creat de Bicep: identitatea are nevoie și de **Owner** sau **User Access Administrator** la scope-ul relevant.
- Pentru deploy ulterior backend: permisiuni pe ACR și Container App.

După provisioning, poți reduce permisiunile identității folosite de deploy dacă vrei separare mai strictă între provisioning și deploy.

Alternativ, dacă vrei să rulezi local:

```bash
az group create --name rg-qlearning-lab --location westeurope

az deployment group create \
  --resource-group rg-qlearning-lab \
  --template-file infra/main.bicep \
  --parameters @infra/main.parameters.example.json
```

După provisioning, actualizează:

1. GitHub variable `VITE_API_URL` cu output-ul `backendUrl`.
2. GitHub variables: `AZURE_RESOURCE_GROUP`, `AZURE_CONTAINER_APP_NAME`, `AZURE_CONTAINER_REGISTRY`, `AZURE_STATIC_WEB_APP_NAME`.
3. GitHub secrets pentru Azure OIDC: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`.

Nu mai trebuie să creezi manual Azure Static Web Apps și nu mai trebuie să copiezi `AZURE_STATIC_WEB_APPS_API_TOKEN`: frontend workflow-ul citește tokenul din Azure cu OIDC.

### Constrângeri operaționale

- Container App este creat inițial cu `minReplicas=0` și `maxReplicas=1`, ca provisioning-ul infrastructurii să nu depindă de o revizie placeholder pornită cu succes.
- Workflow-ul de backend schimbă aplicația la `minReplicas=1` și `maxReplicas=1` când publică imaginea FastAPI reală.
- Limitarea la o singură replică pentru backend-ul real este intenționată: joburile de training și SSE sunt ținute în memorie, iar `index.json` este scris în Azure Files.
- Pentru scalare reală la mai multe replici, mută starea joburilor într-un serviciu extern (de exemplu Redis/Cosmos/Table Storage) și artefactele în Blob Storage.
- Infrastructura definește Container App-ul cu imagine placeholder pe portul 80, dar fără replica pornită. Workflow-ul de backend schimbă ingress-ul la portul 8000 când publică imaginea FastAPI reală.

### Smoke test Azure

După deployment:

```bash
FRONTEND_URL=https://<app>.azurestaticapps.net \
BACKEND_URL=https://<api>.azurecontainerapps.io \
./scripts/azure_smoke_test.sh
```

Checklist manual:

1. Deschide frontendul și rutele directe `/antrenare`, `/evaluare`, `/rulari`, `/comparatie`.
2. Verifică `https://<backend>/api/health`.
3. Pornește o rulare scurtă de training.
4. Confirmă că SSE live update apare în UI.
5. Confirmă că Q-table-ul și artefactele apar în `data/runs` prin Azure Files.
6. Descarcă un artefact din UI.
7. Repornește Container App și confirmă că rulările finalizate se reîncarcă din `index.json`.

### Cost control

- Creează un buget în Azure Cost Management sub limita abonamentului lunar.
- Păstrează Log Analytics retention redus (ex. 30 zile) pentru demo.
- Menține `maxReplicas=1` cât timp backend-ul păstrează job state in-memory.
- Monitorizează Container Apps, Storage și Log Analytics; acestea sunt principalele surse de cost pentru acest proiect.

---

### I. Paradigma de Simulare Aleasă

Pentru acest proiect, voi utiliza o **Arhitectură de Simulare cu Pași de Timp Discreți (Discrete Time Simulation / Time-Driven Simulation)**.

- **Definiție și Funcționare:** În acest model, timpul sistemului avansează în incremente fixe numite "Ticks" sau "Time Steps". Starea sistemului la momentul $t+1$ este o funcție deterministă (sau probabilistică) a stării sistemului la momentul $t$ și a acțiunilor efectuate.
    - **Unitatea de timp:** 1 Tick = 1 Ciclu complet de procesare: [Percepție -> Decizie -> Acțiune -> Reacția Mediului].
    - **Decuplarea Timpului:** Este esențial să separăm "Timpul Simulării" (Ticks) de "Timpul Real" (Wall-clock time). Viteza de execuție a simulării poate fi accelerată (pentru antrenament rapid) sau încetinită (pentru vizualizare și debugging), fără a afecta logica internă sau rezultatele învățării.
        
- **Motivație Teoretică:**
    - **Sincronizare:** Această paradigmă permite o sincronizare perfectă între procesul decizional al agentului (Algoritmul Q-Learning, care este prin natură iterativ) și actualizarea stării mediului.
    - **Reproductibilitate:** Eliminarea variațiilor de timp real (lag, performanța CPU) asigură că un experiment rulat de două ori cu același "seed" aleatoriu va produce exact aceleași rezultate.

### II. Modelarea Mediului (The Environment Model)

Mediul nu este doar un graf abstract, ci un spațiu fizic simulat cu reguli, constrângeri și proprietăți emergente.

#### 1. Topologia Spațiului și Sistemul de Coordonate

- **Structura Matematică:** Mediul este reprezentat ca o matrice bidimensională (Grid 2D) de dimensiune $N \times M$ (ex: 20x20 sau 50x50 pentru scenarii complexe).
- **Sistemul de Coordonate:** Folosim un sistem cartezian discret unde $x \in \{0, ..., N-1\}$ și $y \in \{0, ..., M-1\}$. Colțul stânga-sus este originea $(0,0)$.
- **Limitele Lumii (Boundaries):** Mediul este finit și mărginit ("Bounded World"). Tentativa de a ieși din limitele matricei (ex: $x < 0$) este tratată ca o coliziune cu un perete indestructibil.

#### 2. Generare Procedurală (Stochasticity & Validation)

Pentru a valida robustetea algoritmului de învățare (generalizare), agentul nu trebuie să memoreze o singură hartă.

- **Algoritmul de Generare:** Se va utiliza un generator pseudo-aleatoriu bazat pe un "Seed" numeric.
    1. Inițializare hartă goală.
    2. Plasare aleatorie a Țintei și a Agentului (asigurând distanța minimă Manhattan între ele).
    3. Plasare obstacole cu o densitate $\rho$ (ex: 30% din suprafață).
- **Validarea Topologiei (Flood Fill Check):** După generare, sistemul va rula un algoritm rapid de verificare (ex: BFS sau A*) pentru a garanta că există cel puțin un drum valid de la Agent la Țintă. Dacă harta este insolubilă, procesul de generare se repetă automat. Aceasta previne antrenarea agentului în scenarii imposibile, care ar corupe tabela Q.

#### 3. Elementele Statice și Dinamice (Ontologia Mediului)

Fiecare celulă $(x, y)$ are un tip $T$ și proprietăți asociate care influențează funcția de cost și recompensă:

- **Vid:**
    - _Proprietate:_ Traversabil.
    - _Cost:_ Metabolism bazal (Energie: -1/tick).
- **Obstacol:**
    - _Proprietate:_ Impenetrabil. Agentul rămâne în poziția anterioară.
    - _Feedback:_ Penalizare minoră pentru "lovire" (pentru a descuraja comportamentul redundant).
- **Zona Dificilă:**
    - _Proprietate:_ Traversabil, dar cu dificultate.
    - _Cost:_ Dublu față de normal (Energie: -2 sau -3/tick).
    - _Implicație:_ Agentul trebuie să decidă dacă un drum mai lung pe teren curat este mai eficient energetic decât un drum scurt prin "mlaștină".
- **Resurse:**
    - _Dinamică:_ Obiecte colectabile. Odată intrate în celulă, valoarea energiei agentului crește (ex: +20), iar resursa dispare din mediu.
    - _Regenerare (Opțional):_ Pentru scenarii de supraviețuire infinită, resursele pot reapărea după un interval $\Delta t$.
- **Pericole:**
    - _Proprietate:_ Stare terminală negativă (Game Over instantaneu) sau penalizare masivă continuă (-50).

### III. Modelarea Agentului

Agentul este o entitate autonomă complexă, compusă din trei subsisteme interconectate: Stare Internă, Sistem Senzorial și Modul Decizional.

#### 1. Starea Internă

Agentul simulează homeostazia unui organism simplu:
- **Nivel de Energie (**$E$**):** Variabilă scalară continuă $E \in [0, E_{max}]$.
    - _Ecuația de dinamică:_ $E_{t+1} = E_t - Cost_{mișcare} + Gain_{resurse}$.
    - _Condiție de oprire:_ Dacă $E \le 0$, episodul se termină cu eșec (s-au terminat toate resursele).
- **Poziția Curentă (**$P_t$**):** Vector $(x_t, y_t)$.
- **Memoria Cognitivă (Q-Table):** Structura de date centrală pentru învățare. Este o matrice (Look-up Table) de dimensiuni $Size(S) \times Size(A)$, inițializată cu zero sau valori mici aleatorii.

#### 2. Definiția Stării și Cunoașterea Agentului

Agentul **nu accesează harta globală**. El nu știe de la început unde sunt resursele, obstacolele sau ținta. Această cunoaștere se acumulează *implicit* în Q-Table pe parcursul antrenamentului, prin mii de episoade de interacțiune directă.

**Definiția formală a stării:**
$$S_t = (P_x, P_y, E_{discret})$$

| Componentă | Tip | Valori | Semnificație |
|---|---|---|---|
| $P_x$ | Întreg | $\{0, ..., N-1\}$ | Coloana curentă pe grid |
| $P_y$ | Întreg | $\{0, ..., M-1\}$ | Rândul curent pe grid |
| $E_{discret}$ | Întreg | $\{0, 1, 2, 3\}$ | Nivel energie discretizat |

**Pragurile de discretizare a energiei:**
- $E_{discret} = 0$ → Critic ($E < 25\%$)
- $E_{discret} = 1$ → Scăzut ($25\% \leq E < 50\%$)
- $E_{discret} = 2$ → Mediu ($50\% \leq E < 75\%$)
- $E_{discret} = 3$ → Înalt ($E \geq 75\%$)

**Dimensiunea Q-Table** pentru un grid 20×20:
$$|S| \times |A| = (20 \times 20 \times 4) \times 5 = 8.000 \text{ intrări}$$
Acest spațiu este mic și convergent — agentul poate explora toate stările relevante în câteva mii de episoade.

_Notă despre cunoaștere contextuală:_ Includerea $E_{discret}$ în stare permite agentului să învețe comportamente dependente de context: același nod $(P_x, P_y)$ poate merita o acțiune diferită când agentul e pe cale să moară de foame față de când e plin de energie. Fără această componentă, agentul ar adopta o politică unică per poziție, incapabilă să modeleze urgența supraviețuirii.

#### 3. Modul Decizional

Spațiul de acțiune $A$ este discret și finit:
- $\mathcal{A} = \{UP, DOWN, LEFT, RIGHT, STAY\}$
- Acțiunea `STAY` este relevantă strategic în medii cu inamici mobili sau resurse care se regenerează, permițând agentului să conserve energie (dacă costul de staționare < costul de mișcare).

### IV. Dinamica Simulării și Algoritmul Q-Learning

Acesta este motorul logic care guvernează evoluția sistemului.
#### 1. Bucla Principală (The Simulation Loop)

Pseudocod detaliat pentru un episod de antrenament:

```
INITIALIZARE Episod:
   Setează Agent la poziția de start, Energie = 100%.
   Generează/Resetează Harta.

WHILE (Agent.isAlive() AND !TargetReached):
    1. OBSERVĂ (S): Agentul construiește starea curentă S_t pe baza senzorilor.
    
    2. DECIDE (A): Selecția acțiunii pe baza politicii Epsilon-Greedy:
       Generăm un număr aleator r in [0, 1].
       IF r < epsilon:
           A_t = RANDOM (Explorare - încearcă ceva nou).
       ELSE:
           A_t = argmax Q(S_t, a) (Exploatare - alege cea mai bună acțiune cunoscută).
    
    3. ACȚIONEAZĂ: Execută A_t în mediu.
       - Calculează noua poziție potențială.
       - Verifică coliziuni (Pereți).
       - Actualizează poziția reală a agentului.
       - Consumă Energie.
    
    4. REACȚIE MEDIU (R, S'):
       - Observă noua stare S_{t+1}.
       - Calculează Recompensa R_{t+1} (Reward Signal).
       - Verifică condițiile terminale (Moarte sau Victorie).
    
    5. ÎNVAȚĂ (Q-Update):
       Aplică Ecuația Bellman pentru a actualiza valoarea estimată a acțiunii:
       Q(S, A) = Q(S, A) + alpha * [R + gamma * max(Q(S', a')) - Q(S, A)]
       
    6. ACTUALIZARE PARAMETRI:
       - Scade epsilon (Decay) pentru a reduce explorarea pe măsură ce agentul devine "expert".
    
    7. RENDER (Opțional): Desenează frame-ul dacă vizualizarea este activă.
```

#### 2. Sistemul de Recompense 

- **Pedeapsa Existențială:** $R = -1$ per pas.
    - _Efect:_ Motivează agentul să găsească cea mai rapidă soluție. Fără asta, agentul ar putea sta pe loc la infinit dacă nu există pericole.
- **Recompensă de Supraviețuire (Hrană):** $R = +15$.
    - _Efect:_ Suficient de mare pentru a justifica devierea de la traseu (care costă pași $\times -1$), dar nu atât de mare încât agentul să ignore Ținta finală doar pentru a mânca la infinit.
- **Pedeapsa de Coliziune:** $R = -5$.
- **Recompensă Finală (Țintă):** $R = +100$.
- **Pedeapsa Capitală (Moarte):** $R = -100$.

### V. Instrumentare și Vizualizare (Analytics)

#### 1. Vizualizare Avansată în Timp Real (GUI)

Interfața grafică va oferi debugging vizual:

- **Grid Map:** Randarea celulelor (Verde=Iarbă, Gri=Zid, Maro=Noroi, Galben=Hrană).    
- **Indicatori de strategie:** Desenarea unor săgeți peste fiecare celulă, indicând direcția preferată de agent conform Q-Table. Acest lucru permite observatorului să vadă "intenția" agentului înainte ca acesta să se miște.
- **Q-Value Heatmap:** Colorarea celulelor în funcție de valoarea maximă Q (roșu intens = pericol/valoare mică, verde intens = zonă foarte bună).

#### 2. Metrici de Performanță și Logging

Datele vor fi exportate în format CSV pentru analiză ulterioară:

- **Episode ID:** Indexul episodului.
- **Total Steps:** Numărul de pași efectuați.
- **Total Reward:** Scorul cumulat.
- **Epsilon Value:** Valoarea curentă a parametrului de explorare.
- **Outcome:** Rezultat (Succes / Deces Energie / Deces Capcană / Timeout).
- **Coverage %:** Procentul de celule unice vizitate (pentru a măsura gradul de explorare a hărții).

_Analiza Convergenței:_ Se va urmări "Evoluția Recompensei Medii mobile (Rolling Average Reward). Un grafic ascendent care se stabilizează indică faptul că agentul a "învățat".

### VI. Scenarii de Simulare Propuse (Case Studies)

Proiectul va testa ipoteze specifice prin trei scenarii distincte:

1. **Scenariul A: Navigare Pură**
    - _Condiții:_ Mediu static, Energie Infinită (sau foarte mare).
    - _Obiectiv:_ Validarea implementării Q-Learning. Agentul trebuie să conveargă către drumul optim (echivalent cu Dijkstra/A*).
    - _Metrică:_ Distanța parcursă vs. Distanța Manhattan optimă.
2. **Scenariul B: Dilema Supraviețuitorului**
    - _Condiții:_ Energie limitată strict. Drumul direct către țintă este imposibil fără realimentare. Resursele sunt plasate în zone lăturalnice.
    - _Ipoteză:_ Agentul va învăța o rută sub-optimă geometric, dar optimă funcțional (detur pentru hrană -> Țintă).
    - _Comportament Emergent:_ Se așteaptă oscilații în faza de învățare, urmate de stabilizarea pe un traseu de tip "pit-stop".
3. **Scenariul C: Mediu Dinamic și Adaptabilitate**
    - _Condiții:_ După $N$ episoade (când agentul a învățat harta), se introduc schimbări: se deschide un drum nou (scurtătură) sau se blochează drumul vechi.
    - _Obiectiv:_ Testarea plasticității. Cât de repede își poate agentul "uita" vechea politică pentru a se adapta noii realități? (Analiza influenței ratei de învățare $\alpha$).    - _Limitare asumată:_ Q-Learning tabular nu garantează convergență în medii non-staționate. Rezultatele Scenariului C sunt prezentate ca observație empirică, nu ca dovadă teoretică de adaptabilitate.

---

## VII. Aplicații Reale și Relevanță

Deși proiectul este o simulare academică, mecanismele implementate sunt direct analogice unor sisteme reale cu impact practic. Această secțiune argumentează relevanța lucrării dincolo de contextul academic.

### 1. Robotică și Navigare Autonomă

Problema fundamentală rezolvată — *un agent care învață să navigheze evitând obstacole și gestionând resurse limitate* — este identică cu cea a roboților autonomi în medii necunoscute.

- **Roboți de explorare** (NASA rovers, drone-uri de căutare-salvare): trebuie să găsească drumuri fezabile în medii nevăzute, fără hartă preconstruită.
- **Aspiratoare robotice** (Roomba și echivalente): problemă de acoperire a spațiului cu energie limitată (baterie), cu obstacole dinamice (mobilă mutată).
- **Diferența față de proiect:** sistemele reale folosesc DQN cu input din senzori fizici (LIDAR, cameră). Proiectul nostru implementează stratul decizional fundamental — același algoritm Bellman, același ciclu Observă→Decide→Acționează→Învață.

### 2. Optimizarea Rețelelor de Transport și Logistică

$$S_t = (\text{nod curent}, \text{combustibil rămas})$$

Această formulare este identică cu problema unui vehicul de livrare care:
- Trebuie să ajungă la destinație ($+100$ reward)
- Consumă combustibil per km parcurs ($-1$/pas)
- Poate face pit-stop la stații de alimentare ($+15$ energie)
- Trebuie să decidă dacă deturul merită costul extra (exact Scenariul B)

Companii precum **UPS, FedEx, Amazon Logistics** folosesc variante de RL pentru optimizarea rutelor în timp real.

### 3. Sisteme de Management al Energiei

Agentul care decide când să consume energie și când să se *conserve* ($STAY$) modelează direct:
- **Smart grids**: sisteme care decid când să cumpere/vândă energie în funcție de prețul pieței (stare = preț curent + stoc baterie)
- **Managementul bateriei în vehicule electrice**: algoritmii de regenerative braking decid când să recupereze energie și când să frâneze mecanic

### 4. Jocuri și Inteligență Artificială în Gaming

Genul de simulare implementat este precursorul direct al:
- **NPC behavior** (comportamentul personajelor non-jucător în jocuri video): inamici care "învață" tactici ale jucătorului
- **Procedural content generation**: medii generate procedural (similar cu generatorul nostru cu seed) sunt standard în jocuri ca Minecraft, Hades, Dead Cells
- **Game AI research**: benchmark-ul ARC-AGI-3 (lansat martie 2026) testează exact această capacitate — un agent care explorează un mediu de tip joc, fără instrucțiuni, și deduce singur regulile și obiectivele

### 5. Analogia Biologică: Modelarea Comportamentului Animal

Proiectul simulează explicit mecanisme cognitive studiate în neuroștiință:

| Element simulat | Corespondent biologic |
|---|---|
| Q-Table | Memoria procedurală (ganglionii bazali) |
| Epsilon-Greedy | Echilibrul explorare/exploatare (cortex prefrontal) |
| $E_{discret}$ în stare | Homeostazia — comportament modificat de foame |
| Reward $+100$ la țintă | Dopamina — reinforcement la succes |
| Epsilon decay | Consolidarea deprinderilor prin repetare |

Sistemele de RL au fost validate ca modele computaționale ale învățării la animale (Schultz et al., 1997 — descoperire premiată cu Nobel în 2024 indirect prin Premiul Nobel pentru Fizică acordat lui Hopfield & Hinton).
