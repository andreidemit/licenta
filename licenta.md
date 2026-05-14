# Universitatea din București
# Facultatea de Matematică și Informatică
# Departamentul de Informatică

---

# Simulator Grid-Based pentru Evaluarea Strategiilor de Navigare Sigură în Medii Generate Procedural

**Lucrare de Licență**

**Autor:** Andrei Demit
**Coordonator științific:** Lect. univ. dr. Florentina Suter
**Specializarea:** Informatică

**București, 2026**

---

## Rezumat

### Rezumat în Limba Română

Lucrarea de față prezintă proiectarea, implementarea și analiza experimentală a unui simulator grid-based pentru evaluarea strategiilor de navigare sigură în medii necunoscute, generate procedural. Scopul lucrării nu este doar verificarea binară a faptului că un agent ajunge sau nu la destinație, ci compararea strategiilor după mai multe criterii relevante pentru navigarea autonomă: rata de succes, riscul acumulat, coliziunile, costul traseului, eficiența și capacitatea de generalizare pe hărți noi.

Valoarea proiectului constă în transformarea problemei din „agentul a ajuns la țintă?” în întrebarea mai matură „care strategie este mai potrivită pentru navigare sigură în medii necunoscute?”. În acest sens, sistemul compară strategii bazate pe aleatoriu, reguli, planificare și învățare: Random Agent, Rule-Based Agent, A*, Risk-Aware A*, Tabular Q-Learning, Feature-Based Q-Learning și hibridul experimental Feature-Risk A*. Toți agenții sunt rulați în același tip de mediu GridWorld, ceea ce permite o comparație coerentă între comportamente diferite.

Simulatorul include un generator procedural de hărți validat prin BFS, un model explicit de risc (`RiskModel`) care calculează o hartă de influență în jurul celulelor periculoase — cu costuri discrete de 100.0, 10.0, 5.0 și 2.0 pentru distanțele Manhattan 0, 1, 2 și 3 — și o infrastructură de evaluare Monte Carlo pe distribuții de medii. Performanța nu este judecată pe o singură hartă fixă, ci pe mai multe hărți generate cu seed-uri controlate, iar intervalele de încredere de 95% sunt calculate prin bootstrap cu 1.000 de iterații și seed determinist 1.234. Metricile colectate includ `success_rate`, `average_reward`, `average_steps`, `average_collisions`, `average_danger_entries`, `average_risk_exposure`, `average_total_cost`, `timeout_rate` și `average_computation_time_ms`.

Pe lângă comparația statistică, aplicația include un motor de recomandare explicabilă (`experiments/recommendation.py`). Acesta normalizează metricile agregate Monte Carlo, calculează un scor pentru fiecare strategie și produce un ranking în funcție de obiectivul ales: echilibrat, siguranță, eficiență sau robustețe. Astfel, rezultatul final nu este doar un tabel de metrici, ci o recomandare argumentată: strategia potrivită, motivul recomandării și compromisurile observate. Opțional, un model lingvistic Gemma servit prin Ollama poate fi folosit ca analist textual al rezultatelor, dar numai peste datele produse de simulator; el nu înlocuiește motorul determinist de recomandare.

Cadrul comparativ este organizat în șase **profiluri experimentale** (`known_static`, `high_risk`, `stochastic_execution`, `same_map_learning`, `transfer_learning`, `training_cost`), fiecare simulând un context operațional distinct. Profilul `transfer_learning` este singurul cu `agent_lifecycle = shared_across_maps`: agenții Q sunt antrenați o singură dată pe hărți cu seed-uri offset cu `+50.000` față de hărțile de evaluare, iar politicile sunt testate pe seturi distincte. Celelalte profiluri folosesc `agent_lifecycle = per_map`, unde agentul este re-creat pentru fiecare hartă de evaluare.

`FeatureBasedQLearningAgent` folosește un vector de stare de 11 componente — bitmask de pereți (4 direcții), bitmask de pericole (4 direcții), direcția verticală față de obiectiv (−1/0/+1), direcția orizontală față de obiectiv (−1/0/+1) și un bucket de distanță Manhattan (0: ≤ 2, 1: ≤ 5, 2: > 5) — ceea ce îi permite generalizarea pe hărți nevăzute, spre deosebire de `TabularQLearningAgent` care indexează pe coordonate absolute.

Componenta Q-Learning energetică rămâne o parte importantă a lucrării, dar nu mai reprezintă singurul obiectiv. Aceasta funcționează ca studiu de caz pentru învățare prin consolidare tabulară cu homeostazie energetică: spațiul de stări este definit ca un triplet $(rând, coloană, nivel\_energie)$, unde nivelul de energie continuu este discretizat în patru grupe, rezultând un Q-table de dimensiune $20 \times 20 \times 4 \times 5 = 8.000$ de intrări. Această componentă arată cum o strategie de învățare poate lua decizii diferite în aceeași poziție în funcție de resursele interne ale agentului.

Lucrarea evaluează patru scenarii ale sistemului energetic: Scenariul A (energie foarte mare, navigare pură), Scenariul B (energie limitată la 100 de unități), Scenariul C (mediu dinamic, cu obstacole relocate în timpul antrenamentului) și WAREHOUSE (depozit industrial cu rafturi, stații de încărcare și zone de risc). Pachetul reproductibil generat de `src.final_report` pe grid 20×20, seed 42 și 2.000 de episoade obține rată de succes pe ultimele 100 de episoade de 100% în Scenariul A, 96% în Scenariul B, 100% în Scenariul C și 100% în scenariul WAREHOUSE. Evaluările greedy finale ajung la țintă în 34, 38, 12, respectiv 77 de pași.

În experimentul Monte Carlo pentru scenariul `medium` (5 hărți, 2 episoade per hartă, seed 42), A* și Risk-Aware A* ating ambele 100% succes, dar Risk-Aware A* reduce expunerea medie la risc de la 161.0 la 125.0 și costul total mediu de la 195.4 la 124.6. Acest rezultat susține ideea centrală a lucrării: o strategie poate fi preferabilă nu pentru că ajunge mai des la țintă, ci pentru că ajunge cu risc mai mic și cost mai bun. Întregul sistem este expus printr-un backend FastAPI și o interfață React/Vite hostabilă în Azure Cloud, ceea ce transformă implementarea într-o aplicație demonstrabilă și reproductibilă, nu doar într-un script de antrenare.

**Cuvinte cheie:** simulare grid-based, navigare sigură, hărți generate procedural, risc, coliziuni, cost traseu, Q-Learning, A*, Monte Carlo, FastAPI, React, Azure Cloud.

---

### Abstract in English

This thesis presents the design, implementation and experimental analysis of a grid-based simulator for evaluating safe navigation strategies in unknown procedurally generated environments. The goal is not merely to check whether an agent reaches the destination, but to compare strategies using a richer set of criteria: success rate, accumulated risk, collisions, path cost, efficiency and generalisation to unseen maps.

The value of the project lies in reframing the problem from "did the agent reach the goal?" to "which strategy is more suitable for safe navigation in unknown environments?". The system compares random, rule-based, planning-based and learning-based approaches: Random Agent, Rule-Based Agent, A*, Risk-Aware A*, Tabular Q-Learning, Feature-Based Q-Learning and the experimental Feature-Risk A* hybrid. All agents are evaluated in the same GridWorld setting, which enables a coherent comparison of different behaviours.

The simulator includes a procedurally generated BFS-validated map generator, an explicit risk model (`RiskModel`) that computes an influence map around dangerous cells — with discrete costs of 100.0, 10.0, 5.0 and 2.0 for Manhattan distances 0, 1, 2 and 3 respectively — and a Monte Carlo evaluation pipeline across distributions of maps. Performance is not judged on a single fixed map, but across several maps with controlled seeds; 95% confidence intervals are computed via bootstrap with 1,000 iterations and a deterministic seed of 1,234. The collected metrics include `success_rate`, `average_reward`, `average_steps`, `average_collisions`, `average_danger_entries`, `average_risk_exposure`, `average_total_cost`, `timeout_rate` and `average_computation_time_ms`.

Beyond statistical comparison, the application includes an explainable recommendation engine (`experiments/recommendation.py`). It normalises aggregated Monte Carlo metrics, computes a score for each strategy and produces a ranking according to the selected objective: balanced, safety-first, efficiency-first or robustness-first. The final output is therefore not only a metric table, but an argued recommendation: the suitable strategy, the reason for the recommendation and the observed trade-offs. Optionally, a Gemma language model served through Ollama can act as a textual analyst over the simulator output, without replacing the deterministic recommendation engine.

The comparative framework is organised around six **experiment profiles** (`known_static`, `high_risk`, `stochastic_execution`, `same_map_learning`, `transfer_learning`, `training_cost`), each reproducing a distinct operational context. The `transfer_learning` profile is the only one with `agent_lifecycle = shared_across_maps`: Q-agents are trained once on maps whose seeds are offset by `+50,000` from the evaluation seeds, and policies are tested on disjoint sets. All other profiles use `agent_lifecycle = per_map`, re-creating the agent for each evaluation map.

`FeatureBasedQLearningAgent` represents its state as an 11-component vector — a wall bitmask (4 directions), a danger bitmask (4 directions), the vertical direction to the goal (−1/0/+1), the horizontal direction to the goal (−1/0/+1) and a Manhattan distance bucket (0: ≤ 2, 1: ≤ 5, 2: > 5) — enabling generalisation to unseen maps, unlike `TabularQLearningAgent` which indexes on absolute grid coordinates.

The energy-aware Q-Learning component remains an important part of the thesis, but it is no longer the only objective. It acts as a case study for tabular reinforcement learning with energy homeostasis: the state space is defined as a triplet $(row, column, energy\_level)$, where the continuous energy level is discretised into four buckets, yielding a Q-table of size $20 \times 20 \times 4 \times 5 = 8{,}000$ entries. This component shows how a learning strategy can choose different actions in the same location depending on the internal resources of the agent.

The work evaluates four scenarios of the energy-aware simulator: Scenario A (very high energy, pure navigation), Scenario B (energy capped at 100 units), Scenario C (dynamic environment, with obstacles relocated during training), and WAREHOUSE (an industrial warehouse layout with shelves, charging stations and risk zones). The reproducible final report generated by `src.final_report` on a 20×20 grid, seed 42 and 2,000 training episodes reaches 100% success in Scenario A, 96% in Scenario B, 100% in Scenario C and 100% in WAREHOUSE over the last 100 episodes. Final greedy evaluations reach the goal in 34, 38, 12 and 77 steps respectively.

In the Monte Carlo experiment for the `medium` scenario (5 maps, 2 episodes per map, seed 42), both A* and Risk-Aware A* reach 100% success, but Risk-Aware A* reduces average risk exposure from 161.0 to 125.0 and average total cost from 195.4 to 124.6. This result supports the central argument of the thesis: a strategy can be preferable not because it reaches the goal more often, but because it reaches it with lower risk and better cost. The whole system is exposed through a FastAPI backend and a React/Vite frontend that can be hosted in Azure Cloud, turning the implementation into a reproducible and demonstrable simulation application.

**Keywords:** grid-based simulation, safe navigation, procedurally generated maps, risk, collisions, path cost, Q-Learning, A*, Monte Carlo, FastAPI, React, Azure Cloud.

---

## Cuprins

1. Introducere
   - 1.1 Motivație și context
   - 1.2 Obiectivele lucrării
   - 1.3 Contribuții originale
   - 1.4 Structura lucrării
2. Stadiul Artei
   - 2.1 Simulare grid-based și evaluare pe agenți
   - 2.2 Reinforcement Learning — context general
   - 2.3 Q-Learning clasic și variante
   - 2.4 Algoritmi de planificare: A* și navigare risk-aware
   - 2.5 Navigare autonomă și siguranță operațională
   - 2.6 Poziționarea lucrării față de literatura existentă
3. Fundamentare Teoretică
   - 3.1 Procese Markov de Decizie (MDP)
   - 3.2 Ecuația Bellman și convergența Q-Learning
   - 3.3 Politica Epsilon-Greedy
   - 3.4 Discretizarea spațiului de stări
   - 3.5 Homeostazia energetică ca o constrângere de supraviețuire
   - 3.6 Simulare în timp discret
4. Proiectare și Implementare
   - 4.1 Arhitectura modulară a sistemului
   - 4.2 Mediul de simulare (environment.py)
   - 4.3 Modelul agentului (agent.py)
   - 4.4 Modulul Q-Learning (q_learning.py)
   - 4.5 Orchestratorul de antrenament (trainer.py)
   - 4.6 Interfața grafică Pygame (renderer.py)
   - 4.7 Modulul de analiză (analytics.py)
   - 4.8 Serviciul web, API-ul FastAPI și interfața React
     - 4.8.1 Backend FastAPI și rutele principale
     - 4.8.2 Pagina de analiză Monte Carlo (`/safe-navigation/monte-carlo`)
     - 4.8.3 Persistența stării între rute (`monteCarloStore.ts`)
   - 4.9 Cadrul de navigare sigură și comparație multi-agent
     - 4.9.1 Modelul de mediu (`GridWorld`, `RiskModel`, `RewardConfig`)
     - 4.9.2 Strategiile implementate
     - 4.9.3 Analiza algoritmilor comparați
     - 4.9.4 Vectorul de features al `FeatureBasedQLearningAgent`
     - 4.9.5 Profiluri experimentale și ciclul de viață al agentului
     - 4.9.6 Agregare statistică Monte Carlo și intervale de încredere
     - 4.9.7 Motorul de recomandare explicabilă
     - 4.9.8 Analist AI pentru interpretarea rezultatelor
   - 4.10 Deployment Azure Cloud
5. Experimentare și Rezultate
   - 5.1 Setup experimental
   - 5.2 Rezultate agregate pentru scenariile A, B, C și WAREHOUSE
   - 5.3 Scenariul A: Navigare cu energie foarte mare
   - 5.4 Scenariul B: Supraviețuire cu energie limitată
   - 5.5 Scenariul C: Mediu dinamic cu obstacole relocate
   - 5.6 Scenariul WAREHOUSE: depozit industrial simplificat
   - 5.7 Navigare sigură și comparație Monte Carlo
   - 5.8 Discuții
6. Aplicații în Lumea Reală
   - 6.1 Robotică industrială — depozite autonome
   - 6.2 Vehicule autonome de livrare
   - 6.3 Sisteme IoT și gestionarea energiei
   - 6.4 Drone pentru căutare și salvare
   - 6.5 Agricultură de precizie și roboți agricoli
   - 6.6 Sisteme medicale autonome
   - 6.7 Jocuri video și IA procedurală
   - 6.8 Comportament animal și neuroștiință computațională
7. Simulare Practică — Robotul de Depozit
   - 7.1 Prezentarea problemei
   - 7.2 Maparea pe arhitectura Q-Learning existentă
   - 7.3 Implementarea WarehouseEnvironment
   - 7.4 Rezultate și metrici
   - 7.5 Comparație cu abordări comerciale
8. Concluzii și Direcții Viitoare
   - 8.1 Concluzii principale
   - 8.2 Limitări ale abordării
   - 8.3 Direcții de cercetare viitoare
9. Bibliografie

---

## Capitolul 1: Introducere

### 1.1 Motivație și Context

Navigarea autonomă în medii necunoscute este o problemă de decizie secvențială în care succesul nu poate fi redus la întrebarea simplă „agentul a ajuns la destinație?”. În aplicații reale, o strategie care ajunge la țintă traversând zone periculoase, lovind obstacole sau consumând un traseu foarte scump poate fi inferioară unei strategii puțin mai lente, dar mai sigure și mai robuste. Roboții de depozit, dronele de inspecție, vehiculele autonome de livrare și agenții din jocuri trebuie să aleagă trasee nu doar posibile, ci potrivite pentru constrângerile mediului.

Lucrarea propune un simulator grid-based pentru evaluarea strategiilor de navigare sigură în medii generate procedural. În loc să optimizeze exclusiv atingerea țintei, simulatorul colectează metrici care descriu calitatea comportamentului: rata de succes, costul traseului, coliziunile, intrările în pericol, expunerea acumulată la risc, numărul de pași și timpul de calcul. Această abordare mută accentul de la o demonstrație punctuală la un cadru de simulare comparativă.

Din perspectiva tehnicilor de simulare, proiectul este relevant deoarece separă mediul, agentul, modelul de risc și mecanismul de evaluare. Hărțile sunt generate procedural, sunt validate topologic prin BFS și pot fi rulate repetat cu seed-uri controlate. Agenții sunt interschimbabili, astfel încât aceeași hartă poate fi parcursă de o strategie aleatoare, una euristică, un algoritm A*, o variantă A* sensibilă la risc sau un agent Q-Learning. Experimentele Monte Carlo permit evaluarea pe distribuții de hărți, nu doar pe un exemplu ales manual.

Componenta Q-Learning cu homeostazie energetică păstrează legătura cu învățarea prin consolidare și arată cum un agent poate dezvolta comportamente diferite în funcție de resursele interne. Totuși, în forma actuală, lucrarea nu mai este doar despre Q-Learning. Q-Learning devine una dintre strategiile analizate într-un simulator mai larg, alături de algoritmi de planificare și baseline-uri euristice. Această repoziționare face proiectul mai potrivit pentru o lucrare coordonată din zona tehnicilor de simulare.

### 1.2 Obiectivele Lucrării

Lucrarea de față urmărește atingerea unui set de obiective precise, organizate pe trei niveluri de complexitate crescândă.

**Obiectivul fundamental** este construirea unui simulator grid-based configurabil pentru evaluarea strategiilor de navigare sigură în medii necunoscute, generate procedural. Simulatorul trebuie să permită rularea mai multor agenți pe același tip de mediu și compararea lor prin metrici care descriu atât atingerea țintei, cât și siguranța traseului.

**Obiectivele de nivel intermediar** vizează modelarea componentelor principale ale simulării: (1) generarea procedurală de hărți GridWorld validabile prin BFS; (2) definirea unui model de risc în funcție de apropierea față de pericole; (3) implementarea unei interfețe comune pentru agenți; (4) implementarea strategiilor Random, Rule-Based, A*, Risk-Aware A*, Tabular Q-Learning și Feature-Based Q-Learning; și (5) colectarea de metrici precum succes, risc, coliziuni, cost, pași și timp de calcul.

**Obiectivele de nivel avansat** includ evaluarea generalizării pe hărți generate procedural, rularea experimentelor Monte Carlo, analiza compromisului dintre traseu scurt și traseu sigur, expunerea simulatorului printr-un API web, construirea unei interfețe React pentru demonstrație și publicarea aplicației într-un mediu cloud Azure. Componenta Q-Learning energetică este păstrată ca studiu de caz complementar pentru învățare prin consolidare și supraviețuire energetică.

### 1.3 Contribuții Originale

Lucrarea aduce mai multe contribuții originale față de un proiect clasic de navigare pe grilă sau un tutorial standard de Q-Learning:

**Contribuția 1 — Simulator comparativ pentru navigare sigură.** Sistemul implementează un mediu GridWorld în care strategii diferite pot fi evaluate sub aceleași condiții. Această separare între mediu, agent și simulator permite compararea directă a strategiilor Random, Rule-Based, A*, Risk-Aware A*, Tabular Q-Learning, Feature-Based Q-Learning și Feature-Risk A* experimental.

**Contribuția 2 — Evaluare multi-criterială a siguranței.** Lucrarea nu măsoară doar succesul, ci și coliziunile, intrările în pericol, expunerea acumulată la risc, costul total, numărul de pași, timeout-urile și timpul de calcul. Această alegere permite analiza compromisurilor dintre eficiență și siguranță.

**Contribuția 3 — Generalizare pe hărți generate procedural.** Hărțile sunt generate cu seed-uri controlate și validate prin BFS. Experimentele Monte Carlo evaluează strategiile pe mai multe configurații, reducând dependența de o singură hartă favorabilă.

**Contribuția 4 — Model explicit de risc și planificare risk-aware.** Clasa `RiskModel` transformă apropierea de pericole într-un cost numeric cu valori discrete: 100.0 (celulă DANGER), 10.0 (distanță 1), 5.0 (distanță 2), 2.0 (distanță 3), 0.0 (distanță > 3). `RiskAwareAStarAgent` include acest cost în funcția $f(n) = g(n) + h(n) + w \cdot r(n)$, demonstrând cum o strategie poate prefera un traseu mai sigur chiar dacă acesta nu este strict cel mai scurt.

**Contribuția 5 — Componentă Q-Learning energetică interpretabilă.** Nucleul din `src/` păstrează un agent Q-Learning tabular cu homeostazie energetică. Discretizarea energiei în patru buckets și scenariile A/B/C/WAREHOUSE oferă un studiu de caz clar despre învățare prin consolidare cu resurse interne.

**Contribuția 6 — Motor de recomandare explicabilă.** Modulul `experiments/recommendation.py` transformă rezultatele Monte Carlo într-o decizie multi-criterială. Pentru obiectivele `balanced`, `safety_first`, `efficiency_first` și `robustness_first`, sistemul normalizează metricile pozitive și negative, calculează scoruri, ordonează strategiile și explică de ce un algoritm este recomandat în acel context.

**Contribuția 7 — Aplicație web și reproductibilitate operațională.** Motorul Python este expus printr-un backend FastAPI, iar frontend-ul React/Vite permite antrenarea, evaluarea, editarea mediilor, compararea rulărilor și rularea experimentelor de navigare sigură din browser. Pagina dedicată `/safe-navigation/monte-carlo` expune șapte tab-uri de analiză statistică (distribuții, CI bars, scatter risc-recompensă, heatmap per hartă, breakdown eșecuri, heatmap de ocupanță, export CSV/PNG). Modulul `monteCarloStore.ts` cu persistență în `sessionStorage` asigură că rezultatele Monte Carlo sunt disponibile la navigarea între rute fără re-rularea experimentului. Configurația Azure inclusă în repository demonstrează că aplicația poate fi publicată ca sistem cloud.

### 1.4 Structura Lucrării

Lucrarea este organizată în opt capitole, fiecare contribuind la construcția progresivă a argumentului central.

**Capitolul 2** prezintă stadiul artei în simularea pe grile, navigarea autonomă, planificarea traseului, Q-Learning și evaluarea siguranței. Capitolul poziționează lucrarea ca simulator comparativ, nu ca implementare izolată a unui singur algoritm.

**Capitolul 3** oferă fundamentarea matematică necesară: formalizarea Proceselor Markov de Decizie, derivarea și analiza ecuației Bellman, politica epsilon-greedy și justificarea teoretică a discretizării spațiului de stări.

**Capitolul 4** descrie în detaliu arhitectura modulară a sistemului implementat — nucleul Q-Learning energetic din `src/`, cadrul comparativ de navigare sigură din `agents/`, `environment/`, `simulation/` și `experiments/`, plus API-ul FastAPI, interfața React și infrastructura Azure.

**Capitolul 5** prezintă rezultatele experimentale pentru scenariile A, B, C și WAREHOUSE, apoi comparațiile Monte Carlo între strategiile de navigare sigură, cu accent pe risc, coliziuni, cost și generalizare.

**Capitolul 6** discută aplicabilitatea arhitecturii propuse în opt domenii din lumea reală, de la robotică industrială la neuroștiință computațională.

**Capitolul 7** detaliază implementarea `WarehouseEnvironment` și rezultatele obținute în contextul simulării unui depozit automat de tip Amazon-Kiva.

**Capitolul 8** sintetizează concluziile, discută limitările abordării și propune direcții concrete de cercetare viitoare.

### 1.5 Protocol de reproducere și pachet final de evaluare

Pentru a reduce riscul de nealiniere dintre cod, grafice, prezentare și afirmațiile din text, versiunea finală a proiectului include un flux standardizat de reproducere. Rularea recomandată pentru pachetul complet este:

```bash
python3 -m src.final_report --episodes 2000 --save-qtables
```

Această comandă execută scenariile A, B, C și WAREHOUSE, generează artefactele standard (`results_*`, `convergence_*`, `epsilon_*`, `success_*`) și scrie un sumar agregat în `data/final_summary_<grid>_<seed>_<episodes>.csv` și `.json`. Pentru demo-uri rapide sau verificări smoke, rulările mai scurte sunt acceptate, însă pentru raportarea rezultatelor finale se păstrează configurațiile standardizate din pachetul final.

---

## Capitolul 2: Stadiul Artei

### 2.1 Simulare Grid-Based și Evaluare pe Agenți

Mediile grid-based sunt utilizate frecvent în cercetare și educație deoarece oferă o reprezentare discretă, ușor de inspectat, pentru probleme de navigare, planificare și învățare. O hartă bidimensională împărțită în celule poate modela obstacole, zone periculoase, costuri diferite de deplasare, poziții de start și obiective. Deși este o simplificare față de un mediu fizic continuu, această reprezentare este suficient de expresivă pentru a analiza comportamente algoritmice importante.

În contextul acestei lucrări, mediul GridWorld nu este doar o scenă pentru un singur agent, ci un instrument de simulare comparativă. Aceeași hartă poate fi parcursă de mai multe strategii, iar rezultatele pot fi analizate statistic. Această abordare este potrivită pentru tehnici de simulare deoarece permite controlul parametrilor, repetabilitatea prin seed-uri, generarea de scenarii multiple și agregarea metricilor.

### 2.2 Reinforcement Learning — Context General

Reinforcement Learning (RL) este o paradigmă de învățare automată în care un agent dobândește cunoaștere prin interacțiunea directă cu un mediu, primind semnale de recompensă care orientează comportamentul viitor. Spre deosebire de învățarea supervizată, RL nu are nevoie de exemple etichetate; agentul descoperă singur ce comportamente sunt benefice prin încercare și eroare.

Cadrul formal al RL este cel al Proceselor Markov de Decizie (MDP). În această lucrare, Q-Learning este folosit pentru a ilustra învățarea unei politici în medii discrete. Totuși, RL este tratat ca una dintre familiile de strategii, alături de algoritmi euristici și algoritmi de planificare.

### 2.3 Q-Learning Clasic și Variante

Q-Learning este un algoritm de RL model-free și off-policy, propus de Watkins (1989). Agentul nu învață explicit funcția de tranziție a mediului, ci estimează direct valoarea acțiunilor printr-un tabel Q. Pentru un mediu discret și relativ mic, această abordare este interpretabilă și ușor de analizat: valorile pot fi inspectate, exportate și vizualizate ca heatmap-uri.

În proiect există două utilizări ale Q-Learning. Prima este componenta energetică din `src/`, unde starea include poziția și bucket-ul de energie. A doua este simulatorul de navigare sigură, unde `TabularQLearningAgent` învață pe coordonate absolute, iar `FeatureBasedQLearningAgent` folosește features locale pentru a încerca o generalizare mai bună pe hărți nevăzute.

### 2.4 Algoritmi de Planificare: A* și Navigare Risk-Aware

Navigarea autonomă precede reinforcement learning și include algoritmi clasici de planificare precum Dijkstra și A*. A* combină costul deja acumulat cu o euristică pentru distanța rămasă, de obicei distanța Manhattan în medii grid-based. În medii complet observabile, A* este eficient și oferă o bază solidă pentru comparația cu strategiile învățate.

Totuși, traseul cel mai scurt nu este întotdeauna cel mai sigur. O variantă risk-aware poate introduce în funcția de cost o penalizare pentru apropierea de zone periculoase. Astfel, agentul poate prefera o rută mai lungă, dar cu expunere mai mică la risc. Această idee este centrală pentru lucrare: strategia optimă depinde de criteriul de evaluare, nu doar de atingerea țintei.

### 2.5 Navigare Autonomă și Siguranță Operațională

În sisteme reale, siguranța traseului este la fel de importantă ca succesul final. Un robot de depozit care lovește rafturi, o dronă care intră într-o zonă periculoasă sau un vehicul autonom care alege o rută riscantă pot avea costuri operaționale mari chiar dacă ajung în cele din urmă la destinație. Din acest motiv, metricile de evaluare trebuie să includă coliziuni, expunere la risc, cost energetic sau operațional și stabilitate pe scenarii diferite.

Componenta de homeostazie energetică din lucrare se înscrie în aceeași direcție: agentul nu trebuie doar să ajungă la destinație, ci să ajungă fără să își epuizeze resursele. Aceasta conectează RL cu planificarea safety-aware și cu simularea comportamentelor autonome sub constrângeri.

### 2.6 Poziționarea Lucrării față de Literatura Existentă

Lucrarea se poziționează la intersecția dintre simularea pe grile, navigarea autonomă, planificarea traseului și învățarea prin consolidare. Originalitatea nu constă în inventarea unui algoritm nou, ci în construirea unui simulator coerent care permite evaluarea mai multor strategii pe aceeași clasă de medii și cu aceleași metrici.

Față de tutorialele standard de Q-Learning, lucrarea nu se oprește la întrebarea dacă un agent învață o hartă fixă. Față de o demonstrație simplă de A*, lucrarea nu optimizează doar distanța. Contribuția principală este comparația multi-criterială: succes, risc, coliziuni, cost, pași, timp de calcul și generalizare pe hărți generate procedural.

---

## Capitolul 3: Fundamentare Teoretică

### 3.1 Procese Markov de Decizie (MDP) — Definiție Formală

Un **Proces Markov de Decizie** (MDP) este un cadru matematic pentru modelarea deciziei secvențiale în medii cu tranziții stochastice. Formal, un MDP este definit de un tuplu $(S, A, P, R, \gamma)$, unde:

- $S$ este spațiul de stări — mulțimea tuturor stărilor posibile ale mediului;
- $A$ este spațiul de acțiuni — mulțimea tuturor acțiunilor disponibile agentului;
- $P: S \times A \times S \rightarrow [0,1]$ este funcția de tranziție — $P(s'|s,a)$ dă probabilitatea de a ajunge în starea $s'$ executând acțiunea $a$ din starea $s$;
- $R: S \times A \rightarrow \mathbb{R}$ este funcția de recompensă — $R(s,a)$ dă recompensa imediată pentru executarea acțiunii $a$ din starea $s$;
- $\gamma \in [0,1)$ este factorul de actualizare (discount factor) — controlează cât de mult valorează recompensele viitoare față de cele imediate.

**Proprietatea Markov** este esența MDP-urilor: tranziția din starea $s'$ și recompensa asociată depind doar de starea curentă $s$ și acțiunea $a$, nu de istoria completă a stărilor vizitate. Formal:

$$P(s_{t+1}|s_t, a_t, s_{t-1}, a_{t-1}, \ldots, s_0, a_0) = P(s_{t+1}|s_t, a_t)$$

Această proprietate simplifică dramatic complexitatea problemei: nu este necesar să se rețină istoria completă a interacțiunilor — starea curentă conține tot ce este relevant pentru deciziile viitoare.

**Aplicarea la sistemul nostru.** În contextul lucrării de față, componentele MDP sunt instanțiate astfel:

- $S = \{(r, c, e) \mid r \in [0, 19], c \in [0, 19], e \in \{0, 1, 2, 3\}\}$ — stările sunt triplete (rând, coloană, nivel de energie discretizat). Dimensiunea spațiului de stări este $20 \times 20 \times 4 = 1.600$ de stări distincte.
- $A = \{\text{UP}, \text{DOWN}, \text{LEFT}, \text{RIGHT}, \text{STAY}\}$ — cinci acțiuni discrete.
- $P$ este o funcție determinista în Scenariile A și B: $P(s'|s,a) = 1$ pentru un singur $s'$, în funcție de acțiunea aleasă și configurația grilei. În Scenariul C, după relocarea obstacolelor, funcția de tranziție se modifică brusc.
- $R$ include: $-1$ per pas (cost de timp), $+15$ la colectarea hranei, $-5$ la coliziunea cu un obstacol, $+100$ la atingerea destinației, $-100$ la moarte (energie epuizată sau celulă de pericol), $-2$ cost suplimentar pentru mlaștini.
- $\gamma = 0.95$ — recompensele viitoare sunt ușor devalorizate față de cele imediate, stimulând eficiența.

**Politica** unui agent este o funcție $\pi: S \rightarrow A$ (politică deterministă) sau $\pi: S \times A \rightarrow [0,1]$ (politică stocastică), care dictează ce acțiune să fie executată în fiecare stare. Obiectivul agentului este să găsească politica optimă $\pi^*$ care maximizează recompensa cumulativă actualizată:

$$\pi^* = \arg\max_{\pi} \mathbb{E}_{\pi}\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \mid s_0 = s\right]$$

### 3.2 Ecuația Bellman și Convergența Q-Learning

**Funcția de valoare** $V^{\pi}(s)$ asociată politicii $\pi$ și stării $s$ reprezintă recompensa cumulativă așteptată pornind din $s$ și urmând politica $\pi$:

$$V^{\pi}(s) = \mathbb{E}_{\pi}\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \mid s_0 = s\right]$$

**Funcția de valoare acțiune** (Q-funcția) $Q^{\pi}(s, a)$ extinde această definiție la perechi (stare, acțiune):

$$Q^{\pi}(s, a) = \mathbb{E}_{\pi}\left[\sum_{t=0}^{\infty} \gamma^t R(s_t, a_t) \mid s_0 = s, a_0 = a\right]$$

**Ecuațiile Bellman** exprimă relația de recurență dintre valorile stărilor succesive:

$$Q^{\pi}(s, a) = R(s, a) + \gamma \sum_{s'} P(s'|s,a) \cdot Q^{\pi}(s', \pi(s'))$$

**Ecuația Bellman de optimalitate** pentru Q-funcția optimă $Q^*(s, a)$:

$$Q^*(s, a) = R(s, a) + \gamma \sum_{s'} P(s'|s,a) \cdot \max_{a'} Q^*(s', a')$$

Dacă $Q^*$ este cunoscută, politica optimă se obține simplu ca:

$$\pi^*(s) = \arg\max_{a} Q^*(s, a)$$

**Algoritmul Q-Learning** estimează $Q^*$ prin actualizări iterative bazate pe experiențele reale ale agentului:

$$Q(s_t, a_t) \leftarrow Q(s_t, a_t) + \alpha \left[R_{t+1} + \gamma \max_{a'} Q(s_{t+1}, a') - Q(s_t, a_t)\right]$$

unde $\alpha \in (0,1]$ este rata de învățare, iar termenul în paranteze este **eroarea TD (Temporal Difference)**: diferența dintre estimarea curentă $Q(s_t, a_t)$ și ținta Bellman $R_{t+1} + \gamma \max_{a'} Q(s_{t+1}, a')$.

**Teorema de convergență** (Watkins & Dayan, 1992): Q-Learning converge la $Q^*$ cu probabilitate 1 dacă:
1. Toate perechile $(s, a)$ sunt vizitate de un număr infinit de ori;
2. Rata de învățare satisface condițiile Robbins-Monro: $\sum_t \alpha_t = \infty$ și $\sum_t \alpha_t^2 < \infty$;
3. Recompensele sunt mărginite: $|R(s, a)| < \infty$.

În implementarea noastră, condiția 1 este asigurată prin politica epsilon-greedy cu $\varepsilon > \varepsilon_{min} = 0.01$ (garantând explorare continuă); condiția 2 este aproximată printr-un $\alpha$ constant de 0.1 (o relaxare standard acceptată în practică); condiția 3 este satisfăcută prin definiție.

### 3.3 Politica Epsilon-Greedy — Exploatare vs. Explorare

Dilema exploatare-explorare (exploitation-exploration dilemma) este fundamentală în RL: dacă agentul exploatează mereu cunoașterea actuală (alege acțiunea cu Q maxim), poate rămâne blocat în politici suboptimale; dacă explorează mereu aleatoriu, nu converge la nimic util. Politica epsilon-greedy oferă o soluție pragmatică la această dilemă.

Formal, politica epsilon-greedy este definită ca:

$$\pi_{\varepsilon}(s) = \begin{cases} \arg\max_{a} Q(s, a) & \text{cu probabilitate } 1 - \varepsilon \\ \text{acțiune aleatorie uniformă} & \text{cu probabilitate } \varepsilon \end{cases}$$

**Decayul epsilon** este mecanismul prin care $\varepsilon$ scade gradual pe parcursul antrenamentului, deplasând comportamentul agentului de la explorare pură ($\varepsilon = 1$) la exploatare aproape completă ($\varepsilon \approx \varepsilon_{min}$). Decayul exponențial este cel mai utilizat:

$$\varepsilon_{t+1} = \max(\varepsilon_{min}, \varepsilon_t \cdot \varepsilon_{decay})$$

În implementarea noastră: $\varepsilon_{start} = 1.0$, $\varepsilon_{min} = 0.01$, $\varepsilon_{decay} = 0.995$. Numărul de episoade necesare pentru ca $\varepsilon$ să ajungă la $\varepsilon_{min}$ se calculează:

$$t^* = \left\lceil \frac{\ln(\varepsilon_{min}/\varepsilon_{start})}{\ln(\varepsilon_{decay})} \right\rceil = \left\lceil \frac{\ln(0.01)}{\ln(0.995)} \right\rceil \approx 917 \text{ episoade}$$

Prin urmare, agentul explorează intens primele ~500 de episoade, trece prin faza mixtă explorare-exploatare între episoadele 500–917, și exploatează aproape pur după episodul 917. Această dinamică explică forma tipică a curbelor de convergență observate experimental.

### 3.4 Discretizarea Spațiului de Stări

Algoritmul Q-Learning tabular necesită un spațiu de stări **discret și finit**. Coordonatele $(rând, coloană)$ sunt deja discrete prin natura grilei. Nivelul de energie, în schimb, este o variabilă continuă în intervalul $[0, E_{max}]$. Discretizarea sa este necesară pentru a putea fi folosită ca index în Q-table.

**Schema de discretizare** utilizată în lucrare împarte intervalul $[0, 100]$ în patru buckets de dimensiune egală:

| Bucket | Interval energie | Interpretare | Culoare GUI |
|--------|-----------------|--------------|-------------|
| 0 | $[0, 25)$ | Critic — moarte iminentă | Roșu |
| 1 | $[25, 50)$ | Scăzut — caută hrană | Portocaliu |
| 2 | $[50, 75)$ | Moderat — navigare atentă | Galben |
| 3 | $[75, 100]$ | Ridicat — navigare liberă | Verde |

**Justificarea teoretică.** Această discretizare poate fi privită ca o **augmentare a spațiului de stări**: starea augmentată $(r, c, e)$ satisface proprietatea Markov dacă starea originală $(r, c)$ o satisface, iar funcția de energie este deterministă. Adăugarea componentei energetice nu violează proprietatea Markov — dimpotrivă, o întărește, deoarece starea originală fără energia nu este Markov (acțiunile optime depind de energia curentă, care nu e vizibilă în $(r, c)$ singur).

**Granularitatea discretizării** este un compromis. Patru buckets oferă suficientă rezoluție pentru a distinge comportamente diferite (fuge de pericol, caută hrană, navighează direct), fără a exploda dimensiunea spațiului de stări. O discretizare mai fină (8 sau 16 buckets) ar crește Q-table-ul de 2x sau 4x, cu câștiguri marginale în acuratețea politicii.

**Fenomenul de aliasing.** O limitare a discretizării este că stări cu energii diferite dar în același bucket primesc aceleași valori Q. De exemplu, un agent cu energie 26% și unul cu 49% sunt tratați identic (bucket 1), deși situațiile lor energetice sunt destul de diferite. Această pierdere de informație este acceptabilă în contextul nostru, dar motivează cerțetarea unor scheme de discretizare adaptivă.

### 3.5 Homeostazia Energetică ca Constrângere de Supraviețuire

**Homeostazia**, în sens biologic, este procesul prin care un sistem viu menține parametrii interni în intervale funcționale optime. Temperatura corpului uman oscilează în jurul a 37°C, glicemia în jurul a 90 mg/dL — deviațiile semnificative duc la disfuncție sau moarte. Transferul acestui principiu în sisteme artificiale generează agenți care nu optimizează o recompensă exogenă, ci menținerea unor parametri interni.

În sistemul nostru, homeostazia energetică se manifestă prin **constrângerea de supraviețuire**: agentul nu poate ajunge la destinație dacă energia sa ajunge la zero. Formal, termenul terminal de moarte este definit ca:

$$\text{terminal}(s_t) = \begin{cases} \text{True} & \text{dacă } E_t = 0 \text{ sau } \text{tip\_celulă}(r_t, c_t) = \text{DANGER} \\ \text{False} & \text{altfel} \end{cases}$$

Această constrângere transformă Q-Learning dintr-un simplu optimizator de drum în un sistem care trebuie să echilibreze doi obiectivi posibil conflictuali: **minimizarea timpului de navigare** (ajunge rapid la destinație) și **menținerea energiei** (nu muri pe drum). Tensiunea dintre acești doi obiectivi este sursa comportamentelor interesante observate în Scenariul B: agentul dezvoltă o politică care face detour spre surse de hrană exact când energia scade sub bucket-ul 1 (< 50%), evitând detururile costisitoare când energia este suficientă.

Formal, politica energetică optimă există atunci când valoarea Q satisface:

$$Q^*(s, a) \approx Q^*(s, a) \text{ pentru } s = (r, c, e_1) \neq (r, c, e_2), e_1 \neq e_2$$

Adică, aceeași poziție poate avea valori Q și politici optime diferite, în funcție de nivelul de energie. Aceasta este garanția că adăugarea componentei energetice la stare îmbogățește real expresivitatea politicii, nu este redundantă.

### 3.6 Simulare în Timp Discret

Sistemul implementat funcționează în **timp discret**: la fiecare pas $t$, agentul observă starea $s_t$, alege o acțiune $a_t$, primește recompensa $R_t$ și trece în starea $s_{t+1}$. Această discretizare a timpului simplifică implementarea și analiza, dar introduce un set de ipoteze care merită menționate explicit.

**Ipoteza atomicității acțiunilor.** Fiecare acțiune durează exact un pas de timp, indiferent de natura sa. Mișcarea pe o celulă de mlaștină durează același pas ca mișcarea pe o celulă liberă, dar are cost energetic dublu și cost de recompensă suplimentar ($-2$). Aceasta este o simplificare față de realitate (unde mișcarea prin mlaștină ar dura fizic mai mult), acceptabilă în contextul simulării.

**Ipoteza observabilității complete.** Agentul cunoaște perfect propria poziție și nivelul de energie la fiecare pas. Nu există incertitudine privind localizarea sa. Aceasta este o proprietate a mediului complet observat (POMDP redus la MDP), justificată în contextul roboților cu localizare precisă (GPS intern, SLAM).

**Limita de pași per episod.** Fiecare episod are un număr maxim de $T_{max} = 500$ de pași. Dacă agentul nu a atins destinația sau nu a murit în acest timp, episodul se termină forțat cu o recompensă neutră (0) pentru episodul Scenariului A, sau negativ proportional cu energia rămasă. Această limită previne episoadele infinite în fazele timpurii ale antrenamentului, când agentul explorează aleatoriu.

---

## Capitolul 4: Proiectare și Implementare

### 4.1 Arhitectura Modulară a Sistemului

Sistemul este implementat ca o platformă modulară de simulare, cu trei straturi principale. Primul strat este motorul Q-Learning energetic din `src/`, responsabil de scenariile A, B, C și WAREHOUSE. Al doilea strat este cadrul comparativ de navigare sigură, împărțit în pachetele `agents/`, `environment/`, `simulation/` și `experiments/`. Al treilea strat este aplicația web: backend FastAPI, frontend React/Vite și infrastructură de deployment Azure. Această organizare permite separarea clară între modelul de simulare, algoritmii de decizie, experimentele statistice și interfața utilizatorului.

```
licenta/
├── src/
│   ├── __init__.py
│   ├── constants.py      # Parametri globali: dimensiuni, recompense, hiperparametri RL
│   ├── environment.py    # Mediu: grilă, generare procedurală, BFS, try_move()
│   ├── agent.py          # Agent: stare internă, discretizare energie, statistici
│   ├── q_learning.py     # RL: Q-table, Bellman update, epsilon-greedy
│   ├── trainer.py        # Orchestrare: bucla de antrenament, run_episode(), EpisodeResult
│   ├── renderer.py       # GUI: Pygame, heatmap Q-values, săgeți politică
│   ├── analytics.py      # Export: CSV, grafice Matplotlib, manifest JSON, PNG-uri
│   ├── serialization.py  # Serializare medii, Q-statistici și evenimente live
│   ├── simulation_service.py # Servicii reutilizate de CLI și FastAPI
│   ├── static_environment.py # Medii JSON custom pentru evaluare
│   ├── transitions.py    # Payload comun pentru evenimentele de tranziție
│   ├── final_report.py   # Pachet reproductibil A/B/C/WAREHOUSE
│   └── main.py           # Entry point: argparse, moduri manual/training
├── agents/
│   ├── random_agent.py
│   ├── rule_based_agent.py
│   ├── astar_agent.py
│   ├── q_learning_agent.py
│   └── feature_q_learning_agent.py
├── environment/
│   ├── grid_world.py     # Mediu generic pentru navigare sigură
│   ├── map_generator.py  # Generare procedurală easy/medium/hard/custom
│   └── risk_model.py     # Hartă de risc în jurul celulelor periculoase
├── simulation/
│   ├── simulator.py      # Motor generic care rulează orice BaseAgent
│   ├── episode_result.py
│   └── metrics.py        # Agregare Monte Carlo
├── experiments/
│   └── compare_agents.py # Comparație agenți pe hărți generate procedural
├── web/
│   ├── backend/          # FastAPI, SSE, job store, modele Pydantic
│   └── frontend/         # React/Vite, pagini de training/evaluare/comparație
├── infra/                # Bicep pentru Azure Static Web Apps + Container Apps
├── tests/
│   ├── test_quick.py
│   ├── test_convergence.py
│   ├── test_scenarios.py
│   ├── test_analytics.py
│   ├── test_persistence.py
│   ├── test_warehouse.py
│   ├── test_web_api.py
│   ├── test_transitions.py
│   └── test_safe_navigation.py
├── data/                 # Q-tables salvate, CSV-uri, grafice PNG
├── requirements.txt
└── Dockerfile
```

**Fluxul de date per pas** urmează un circuit clar: `Renderer` vizualizează starea curentă → `QLearning.choose_action()` selectează o acțiune pe baza stării furnizate de `Agent.get_state()` → `Environment.try_move()` procesează acțiunea și returnează un payload complet de tranziție (poziție nouă, cost energetic, energie câștigată, reward, flag terminal și motiv terminal) → `Agent.apply_action_result()` actualizează starea internă și energia → `QLearning.update()` aplică actualizarea Bellman → `Trainer` înregistrează rezultatul episodului.

Pentru aplicația web, fluxul este extins: frontend-ul React trimite cereri către FastAPI (`/api/train`, `/api/stream/{run_id}`, `/api/evaluate`, `/api/safe-navigation/*`), backend-ul construiește un `SimulationConfig`, creează un job în `JobStore`, rulează motorul Python și publică evenimente live prin Server-Sent Events. Artefactele finale sunt salvate sub `data/runs/` și pot fi descărcate din browser.

Dependențele sunt păstrate pe direcții clare: motorul Q-Learning din `src/` nu depinde de frontend, iar backend-ul web reutilizează funcțiile din `src.simulation_service` în loc să reimplementeze logica în JavaScript. Cadrul de safe navigation este separat de motorul energetic, ceea ce permite folosirea lui pentru comparații Monte Carlo fără să modifice scenariile A/B/C.

### 4.2 Mediul de Simulare (environment.py) — Generare Procedurală BFS-Validată

Modulul `environment.py` implementează grila 2D și toate mecanismele de interacțiune ale agentului cu mediul. Grila este reprezentată ca o matrice Python bidimensională de dimensiune $N \times M$ (implicit $20 \times 20$), fiecare celulă conținând un tip din enum-ul:

```python
class CellType(Enum):
    EMPTY   = 0  # Celulă liberă, traversabilă fără cost suplimentar
    OBSTACLE = 1  # Bloc solid, nu poate fi traversat
    MUD     = 2  # Traversabilă cu cost dublu de energie și -2 recompensă
    FOOD    = 3  # Consumabilă: +15 recompensă, +20 energie, dispare după colectare
    DANGER  = 4  # Moarte instant la intrare: -100 recompensă, terminal
    TARGET  = 5  # Destinație: +100 recompensă, terminal
    START   = 6  # Poziție inițială a agentului
```

**Generarea procedurală** utilizează un generator de numere pseudoaleatoare cu seed configurabil (`random.Random(seed)`), asigurând reproductibilitatea completă a experimentelor. Procesul de generare urmează pașii:

1. Inițializare grilă cu celule EMPTY;
2. Plasarea START și TARGET la distanță Manhattan minimă de $\lfloor N/2 \rfloor$ (pentru a garanta o problemă netrivială);
3. Populare aleatorie cu obstacole (densitate 15%), mlaștini (8%), hrană (5%) și pericol (3%);
4. **Validare BFS**: se verifică existența unui drum de la START la TARGET ocolind obstacolele;
5. Dacă validarea eșuează, se regenerează harta (cu un seed modificat) până la succes.

**Validarea BFS** este implementată ca o parcurgere în lățime standard pe grila 2D:

```python
def _validate_path_bfs(self) -> bool:
    """Returnează True dacă există un drum de la START la TARGET."""
    from collections import deque
    queue = deque([self.start_pos])
    visited = {self.start_pos}
    while queue:
        r, c = queue.popleft()
        if (r, c) == self.target_pos:
            return True
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if (0 <= nr < self.rows and 0 <= nc < self.cols
                    and (nr, nc) not in visited
                    and self.grid[nr, nc] != CellType.OBSTACLE):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False
```

Complexitatea BFS este $O(N \cdot M)$, neglijabilă față de costul episoadelor de antrenament.

**Metoda `try_move()`** este interfața principală prin care agentul interacționează cu mediul. Primește poziția curentă și acțiunea, apoi returnează un dicționar cu toate efectele tranziției: poziția nouă, costul energetic, energia câștigată, recompensa, flagul terminal și motivul terminării. Tratarea coliziunilor cu marginile grilei și cu obstacolele este implementată consistent: agentul rămâne pe loc și primește penalizarea de $-5$ pentru coliziune, fără schimbarea poziției.

### 4.3 Modelul Agentului (agent.py) — Stare Internă și Discretizare Energie

Clasa `Agent` din modulul `agent.py` encapsulează starea internă a agentului și metodele de actualizare a acesteia. Starea completă a agentului la momentul $t$ este:

```python
@dataclass
class AgentState:
    row: int          # Rândul curent în grilă (0..N-1)
    col: int          # Coloana curentă în grilă (0..M-1)
    energy: float     # Energia curentă, valoare continuă în [0, E_max]
```

Starea MDP utilizată pentru indexarea Q-table-ului este tripletul discretizat $(row, col, energy\_bucket)$, unde `energy_bucket` se calculează:

```python
def get_energy_bucket(self) -> int:
    """Returnează bucket-ul discret de energie (0-3)."""
    fraction = self.energy / self.max_energy
    if fraction < 0.25: return 0   # Critic
    if fraction < 0.50: return 1   # Scăzut
    if fraction < 0.75: return 2   # Moderat
    return 3                        # Ridicat
```

**Actualizarea energiei** per pas depinde de tipul celulei vizitate:

| Tip celulă | Consum energie | Recompensă adițională |
|------------|---------------|----------------------|
| EMPTY | $-1$ | — |
| MUD | $-2$ (dublu) | $-2$ |
| FOOD | $+20$ (câștig) | $+15$ |
| DANGER | $-E_{max}$ (moarte) | $-100$ |
| OBSTACLE | $0$ (nu se mișcă) | $-5$ |
| TARGET | — | $+100$ |

**Statistici per episod.** Agentul colectează metrici pe parcursul fiecărui episod: numărul de pași, recompensa totală, coverage-ul (procentul de celule unice vizitate), energia rămasă și motivul terminării episodului. Aceste metrici sunt returnate la finalul episodului ca un obiect `EpisodeResult`.

### 4.4 Modulul Q-Learning (q_learning.py) — Q-Table, Bellman, Epsilon-Greedy

Clasa `QLearning` implementează nucleul algoritmului de reinforcement learning. Q-table-ul este reprezentat ca o matrice NumPy cu dimensiunile `(GRID_ROWS, GRID_COLS, N_ENERGY_BUCKETS, N_ACTIONS)`:

```python
class QLearning:
    def __init__(self, rows: int, cols: int, n_energy: int = 4, n_actions: int = 5):
        self.q_table = np.zeros((rows, cols, n_energy, n_actions))
        self.alpha = ALPHA        # 0.1
        self.gamma = GAMMA        # 0.95
        self.epsilon = EPSILON_START  # 1.0
        self.epsilon_min = EPSILON_MIN  # 0.01
        self.epsilon_decay = EPSILON_DECAY  # 0.995
```

Dimensiunile pentru grila 20×20: $20 \times 20 \times 4 \times 5 = 8.000$ de valori Q, fiecare de tip `float64` (8 bytes) → **64 KB de memorie** pentru Q-table. Aceasta este o amprentă de memorie complet neglijabilă față de alternativele bazate pe rețele neurale.

**Selecția acțiunii** urmează politica epsilon-greedy:

```python
def choose_action(self, state: tuple[int, int, int]) -> int:
    """Selectează acțiunea conform politicii epsilon-greedy."""
    if random.random() < self.epsilon:
        return random.randint(0, self.num_actions - 1)  # Explorare
    r, c, e = state
    q_values = self.q_table[r, c, e]
    max_q = np.max(q_values)
    best_actions = np.where(q_values == max_q)[0]
    return int(np.random.choice(best_actions))  # Exploatare cu tie-break aleator
```

**Actualizarea Bellman** implementează ecuația Q-Learning standard:

```python
def update(self, state, action, reward, next_state, done):
    """Aplică actualizarea Bellman pentru o tranziție (s, a, r, s', done)."""
    r, c, e = state
    nr, nc, ne = next_state
    
    current_q = self.q_table[r, c, e, action]
    
    if done:
        target = reward
    else:
        target = reward + self.gamma * np.max(self.q_table[nr, nc, ne])
    
    # Actualizare Q cu rata de învățare alpha
    self.q_table[r, c, e, action] += self.alpha * (target - current_q)
```

**Decayul epsilon** se aplică la finalul fiecărui episod:

```python
def decay_epsilon(self):
    """Aplică decayul exponential al epsilon după fiecare episod."""
    self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
```

**Persistența Q-table-ului** este implementată prin serializare NumPy (`np.save`/`np.load`). Aceasta permite continuarea antrenamentului dintr-un checkpoint salvat și replay-ul unei politici deja învățate.

### 4.5 Orchestratorul de Antrenament (trainer.py)

Modulul `trainer.py` orchestrează bucla de antrenament, coordonând interacțiunile dintre mediu, agent și modulul Q-Learning. Structura centrală este `EpisodeResult`, care încapsulează toată informația relevantă pentru un episod:

```python
class EpisodeResult:
    __slots__ = ("episode_id", "total_steps", "total_reward", "epsilon",
                 "outcome", "coverage", "energy_remaining")
```

Metoda `run_episode()` execută un singur episod complet:

```python
def run_episode(self, episode_id, render_callback=None):
    self._reset_environment_for_episode()
    agent = Agent(start_pos=self.env.start_pos, energy=self.energy)
    state = agent.get_state()

    for step in range(self.max_steps):
        action = self.q.choose_action(state)
        result = self.env.try_move(agent.position, action)
        reason = agent.apply_action_result(result)
        next_state = agent.get_state()
        done = reason is not None

        self.q.update(state, action, result["reward"], next_state, done)
        state = next_state

        if done:
            break
```

Metoda `run_greedy_episode()` este utilizată pentru evaluarea politicii învățate, fără explorare, folosind `QLearning.get_best_action()` pe aceeași hartă de bază a episodului.

**Scenariul C** este implementat prin relocarea controlată a unei fracțiuni din obstacole la episodul 500, urmată de păstrarea acelei configurații ca nouă hartă de bază pentru episoadele următoare. Astfel, Q-table-ul rămâne intact, iar mediul chiar se schimbă persistent după switch-ul experimental.

### 4.6 Interfața Grafică Pygame (renderer.py) — Heatmap Q-Values, Săgeți Politică

Modulul `renderer.py` implementează vizualizarea interactivă a simulării utilizând biblioteca Pygame-CE (Community Edition). Fereastra de vizualizare este împărțită în două zone: grila de simulare (stânga) și panoul de statistici live (dreapta).

**Codificarea cromatică a celulelor:**

| Tip celulă | Culoare | Cod hex |
|------------|---------|---------|
| EMPTY | Gri deschis | `#E0E0E0` |
| OBSTACLE | Negru | `#1A1A1A` |
| MUD | Maro | `#8B4513` |
| FOOD | Verde | `#00AA00` |
| DANGER | Roșu | `#FF0000` |
| TARGET | Auriu | `#FFD700` |
| START | Albastru | `#0000FF` |

**Vizualizarea agentului** utilizează un cerc cu culoare variabilă: roșu pur când energia $\leq 20\%$, gradient spre verde la energie completă. Aceasta oferă un indicator vizual instant al stării energetice a agentului.

**Heatmap Q-Values:** La toggle-ul tastei `H`, celulele grilei sunt colorate proporțional cu $\max_a Q(s, a)$ pentru starea corespunzătoare (la nivelul de energie al agentului curent). Valorile Q sunt normalizate în intervalul $[0, 1]$ și mapate pe o scală cromatică de la albastru (valori mici) la roșu (valori mari), cu verde la valori medii. Aceasta permite vizualizarea intuitivă a „hărții de valori" pe care o percepe agentul.

**Săgeți de politică:** La toggle-ul tastei `P`, pe fiecare celulă liberă este desenată o săgeată indicând acțiunea preferată: $\arg\max_a Q(s, a)$. Săgețile sunt scalate proporțional cu certitudinea politicii — diferența dintre Q maxim și al doilea Q ca mărime — pentru a distinge celulele cu politică certă de cele ambigue.

### 4.7 Modulul de Analiză (analytics.py) — CSV, Grafice Convergență

Modulul `analytics.py` colectează și vizualizează datele de antrenament. La finalul fiecărui episod, un rând este adăugat în fișierul CSV. În versiunea curentă, exportul nu se limitează la pași, recompensă și epsilon, ci include și coliziuni, hrană colectată, pași prin noroi, intrări în pericol, energie consumată/câștigată, distribuția acțiunilor, eroarea TD medie și gradul de umplere al Q-table-ului:

```
episode_id, steps, total_reward, epsilon, outcome, coverage_pct, energy_remaining,
collisions, food_collected, mud_steps, danger_entries, energy_spent, energy_gained,
action_up, action_down, action_left, action_right, action_stay, mean_abs_td,
q_nonzero, q_fill_pct
...
2000, 38, 95.0, 0.0100, SUCCESS, 9.50, 84.0, ...
```

**Grafice generate automat** prin Matplotlib:

1. **Curba de recompensă** — `total_reward` per episod, cu medie mobilă pe 50 episoade;
2. **Rata de succes** — procent de episoade reușite pe ferestre de 100 episoade;
3. **Decayul epsilon** — curba $\varepsilon$ vs. numărul episodului;
4. **Distribuția pașilor** — histogramă a numărului de pași per episod succes;
5. **Energia minimă atinsă** — evoluția nivelului minim de energie per episod (relevant pentru Scenariile B și C).

Graficele sunt salvate automat ca fișiere PNG în directorul `data/`, cu denumiri descriptive. În plus, pachetul final produce:

- `manifest_<scenario>_<grid>_<seed>.json` cu configurația, sumarul, statistici despre hartă și lista artefactelor;
- `map_<scenario>_<grid>_<seed>.png` pentru vizualizarea hărții;
- `policy_e3_<scenario>_<grid>_<seed>.png` pentru politica greedy la nivel energetic ridicat;
- `q_heatmap_e3_<scenario>_<grid>_<seed>.png` pentru valorile Q maxime;
- `visit_heatmap_<scenario>_<grid>_<seed>.png` și `td_heatmap_<scenario>_<grid>_<seed>.png` pentru observabilitatea procesului de învățare;
- `greedy_trajectory_<scenario>_<grid>_<seed>.csv/.json` și `greedy_path_<scenario>_<grid>_<seed>.png` pentru traseul final;
- `scenario_comparison_ALL_<grid>_<seed>.png` pentru comparația între scenarii.

### 4.8 Serviciul Web, API-ul FastAPI și Interfața React

#### 4.8.1 Backend FastAPI și rutele principale

Versiunea curentă a proiectului nu este doar un simulator CLI/Pygame, ci și o aplicație web. Backend-ul din `web/backend/app.py` expune motorul Python prin FastAPI. Rutele principale sunt:

| Rută | Rol |
|------|-----|
| `/api/health` | Verifică disponibilitatea backend-ului |
| `/api/scenarios` | Listează scenariile A, B, C și WAREHOUSE |
| `/api/environments/preview` | Generează o previzualizare de hartă procedurală sau warehouse |
| `/api/train` | Creează un job de antrenare |
| `/api/stream/{job_id}` | Transmite evenimente live prin Server-Sent Events |
| `/api/runs` și `/api/runs/{id}` | Listează și inspectează rulările salvate |
| `/api/runs/{id}/artifacts/{key}/download` | Descarcă artefacte generate |
| `/api/qtables` | Listează tabele Q disponibile pentru evaluare |
| `/api/evaluate` | Rulează o politică greedy pe unul sau mai multe medii JSON |
| `/api/safe-navigation/status` | Verifică disponibilitatea modulului de navigare sigură |
| `/api/safe-navigation/algorithms` | Returnează lista algoritmilor expuși, cu explicații |
| `/api/safe-navigation/preview` | Generează previzualizare hartă GridWorld cu harta de risc suprapusă |
| `/api/safe-navigation/episode` | Rulează un episod al unui agent specificat |
| `/api/safe-navigation/monte-carlo` | Rulează experimentul Monte Carlo pentru toți algoritmii selectați |
| `/api/evaluation-scenarios` | Returnează profilurile experimentale disponibile |

Persistența rulărilor este gestionată de `JobStore`, care scrie indexul în `data/runs/index.json`. Backend-ul validează modelele de request prin Pydantic (`TrainRequest`, `EvaluateRequest`, `EnvironmentPayload`, `SafeNavigationRequest`, `MonteCarloRequest`) și protejează descărcarea artefactelor prin verificarea că fișierele cerute se află sub directorul controlat `RUNS_ROOT`.

Frontend-ul din `web/frontend/` este construit cu React, Vite, React Router, Tailwind CSS și componente UI de tip shadcn/Radix. Interfața include două zone funcționale:

1. **Laboratorul Q-Learning energetic**, disponibil sub `/lab`, cu pagini pentru antrenare, rulări, detalii de rulare, evaluare pe medii noi, editor de mediu și comparație multi-run.
2. **Simulatorul de navigare sigură**, disponibil pe ruta principală `/` și `/safe-navigation`, cu panou de configurare, vizualizare GridWorld, hartă de risc, replay al traseului, metrici și comparație Monte Carlo între algoritmi.

Separarea este intenționată: laboratorul Q-Learning arată homeostazia energetică și artefactele de licență, iar simulatorul de navigare sigură arată comparația algoritmică și legătura directă cu tehnicile de simulare statistică.

#### 4.8.2 Pagina de analiză Monte Carlo (`/safe-navigation/monte-carlo`)

Pagina dedicată de analiză statistică este disponibilă la ruta `/safe-navigation/monte-carlo` și este montată în `web/frontend/src/app/router.tsx`. Aceasta afișează rezultatele ultimului experiment Monte Carlo rulat și include șapte tab-uri funcționale:

| Tab | Componentă | Ce vizualizează |
|-----|------------|-----------------|
| **Distribuții** | `RewardDistribution.tsx` | Boxplot-uri per agent pentru recompensă, pași sau expunere la risc; comutator de metrică |
| **Intervale de încredere** | `MetricCIBars.tsx` | Bare cu error bars CI 95% bootstrap pentru `success_rate`, `collision_rate`, `danger_entry_rate`, `timeout_rate`, `average_reward`, `average_steps`, `average_risk_exposure` |
| **Risc / Recompensă** | `RiskRewardScatter.tsx` | Scatter Pareto: un punct = un episod, dimensiune = număr pași, culoare = agent |
| **Per-hartă** | `PerMapHeatmap.tsx` | Heatmap agent × `map_seed` colorat după `success_rate` |
| **Eșecuri** | `FailureBreakdown.tsx` | Stacked bar: episoade reușite / coliziune terminală / intrare în pericol / timeout |
| **Ocupare grilă** | `OccupancyHeatmap.tsx` | Heatmap SVG agregat din toate path-urile per agentul selectat |
| **Export** | `ExportPanel.tsx` | CSV rezumat + CSV episoade brute, JSON complet, PNG per chart |

Toate componentele Recharts primesc datele din starea globală `MonteCarloAnalysisPage.tsx`, care coordonează filtrele de algoritm și ciclul de viață al rezultatelor.

#### 4.8.3 Persistența stării între rute (`monteCarloStore.ts`)

Un utilizator care navighează de la Wizard-ul Safe Navigation la pagina de analiză și înapoi nu trebuie să re-ruleze experimentul Monte Carlo. Modulul `web/frontend/src/features/safe-navigation/monteCarloStore.ts` implementează un store reactiv cu persistență în `sessionStorage`.

Arhitectura este un singur obiect React Context + hook personalizat `useMonteCarloStore()`. La fiecare finalizare a unui experiment, rezultatul complet este serializat în `sessionStorage['monteCarlo']`. La montarea paginii de analiză, store-ul este inițializat din `sessionStorage`. Dacă tab-ul sau browser-ul este închis, datele sunt pierdute — comportamentul intenționat pentru a nu stoca gigabytes de date de sesiune.

```typescript
// Pattern de utilizare în componentele consumer
const { result, setResult, clearResult } = useMonteCarloStore();
```

Separarea dintre persistență (sessionStorage) și stare reactivă (React Context) permite rerenderizare corectă fără polling și fără refetch de la backend.

### 4.9 Cadrul de Navigare Sigură și Comparație Multi-Agent

#### 4.9.1 Modelul de mediu (`GridWorld`, `RiskModel`, `RewardConfig`)

Cadrul separat de navigare sigură utilizează un mediu `GridWorld` cu tipuri de celule `EMPTY`, `WALL`, `DANGER`, `START` și `GOAL`. Spre deosebire de `src/environment.py`, acesta nu include energie sau hrană — modelul este centrat exclusiv pe navigare cu risc.

Clasa `RiskModel` din `environment/risk_model.py` calculează o hartă de influență în funcție de distanța Manhattan față de celulele `DANGER`:

| Distanță Manhattan față de DANGER | Cost de risc |
|---:|---:|
| 0 (celulă DANGER) | 100.0 |
| 1 | 10.0 |
| 2 | 5.0 |
| 3 | 2.0 |
| > 3 | 0.0 |

Aceasta modelează realitatea: **apropierea de o zonă periculoasă are cost chiar fără intrare directă** (zona de siguranță din jurul echipamentelor industriale, distanța față de persoane). Costurile sunt parametrizabile prin `RiskModel(danger_cost, distance_1_cost, distance_2_cost, distance_3_cost)`.

Funcția de recompensă este configurabilă prin `RewardConfig`:

| Componentă | Valoare implicită | Semnificație |
|------------|------------------:|--------------|
| goal | +100 | Recompensă pentru atingerea obiectivului |
| danger | -100 | Penalizare terminală pentru intrarea în pericol |
| wall | -10 | Penalizare pentru coliziune |
| step | -1 | Cost de timp per pas |
| closer | +2 | Shaping pentru apropierea de obiectiv |
| farther | -2 | Penalizare pentru îndepărtare |

Recompensele de shaping (`closer`/`farther`) accelerează convergența Q-Learning fără a modifica politica optimă (potential-based shaping). Parametrul `movement_noise` din `GridWorld` introduce stochasticitate în execuție: cu probabilitate `movement_noise`, acțiunea este deviată lateral față de intenția agentului.

#### 4.9.2 Strategiile implementate

Fiecare strategie modelează o paradigmă diferită de luare a deciziei. Interfața comună `BaseAgent` din `agents/base_agent.py` impune metodele `select_action(observation)`, `learn(transition)`, `reset()`, `state_key(observation)` și opțional `explain()`.

| Strategie | Paradigmă | `requires_training` | Observabilitate hartă |
|---|---|---|---|
| `RandomAgent` | Baseline aleator | Nu | Nu |
| `RuleBasedAgent` | Euristică locală (evită pereți/pericole, reduce distanța Manhattan) | Nu | Parțial (vecini imediate) |
| `AStarAgent` | Planificare globală (dijkstra cu euristică Manhattan) | Nu | Completă |
| `RiskAwareAStarAgent` | Planificare cu cost de risc inclus în funcția $f(n) = g(n) + h(n) + w \cdot r(n)$ | Nu | Completă |
| `TabularQLearningAgent` | RL pe coordonate absolute | Da | Nu (model-free) |
| `FeatureBasedQLearningAgent` | RL pe vector de features locale | Da | Nu (model-free) |
| `FeatureRiskAwareAStarAgent` | Hibrid experimental: penalizări locale învățate + Risk-Aware A* | Da | Completă în planificare, experiență în costuri locale |

#### 4.9.3 Analiza algoritmilor comparați

Pentru ca evaluarea să fie relevantă, fiecare algoritm nu este tratat doar ca o implementare tehnică, ci ca o strategie cu un rol experimental clar. Întrebările urmărite sunt: ce rol are în simulator, când este mai potrivit, în ce scenarii poate deveni cea mai bună alegere și dacă există analogii reale în produse, framework-uri sau sisteme folosite în industrie.

**RandomAgent — baseline statistic.** Rolul său este să stabilească nivelul minim de performanță. Dacă un algoritm sofisticat nu depășește consistent agentul aleator, înseamnă că există o problemă de modelare, recompensă, training sau evaluare. RandomAgent nu are strategie, nu memorează, nu planifică și nu învață; el eșantionează uniform din spațiul de acțiuni. Este util în teste de regresie, validarea metricilor și verificarea dificultății scenariului. Poate fi „cel mai bun” doar în cazuri artificiale: hartă trivială, acțiuni aproape echivalente sau lipsa totală a timpului de calcul pentru altă strategie. În lumea reală, nu este folosit ca algoritm operațional de navigare sigură; analogia de piață este rolul de baseline în simulatoare, testare stochastică și faze de explorare din reinforcement learning.

**RuleBasedAgent — euristică reactivă locală.** Rolul său este să reprezinte o strategie simplă, explicabilă și foarte ieftină computațional. Agentul verifică vecinii imediați, elimină pereții și pericolele directe, apoi alege acțiunea care reduce distanța Manhattan față de obiectiv. Este mai bun decât RandomAgent când mediul are coridoare simple și nu cere detururi complexe. Devine atractiv când resursele de calcul sunt mici, când este nevoie de comportament determinist și când siguranța locală este mai importantă decât optimalitatea globală. Poate fi cel mai bun în scenarii mici, cu obstacole rare, fără capcane topologice și fără necesitatea unei hărți globale. În sisteme reale, reguli reactive similare apar frecvent ca straturi de siguranță: evitarea obstacolelor apropiate, oprire de urgență, păstrarea distanței minime sau filtre de tip „nu intra în zonă interzisă”. De obicei, ele nu sunt singurul planner, ci completează planificatoare mai avansate.

**AStarAgent — planificare globală pentru drum scurt.** Rolul său este să ofere un reper puternic pentru scenariile în care harta este cunoscută. A* combină costul parcurs $g(n)$ cu o estimare euristică $h(n)$ a distanței până la obiectiv; în proiect se folosește distanța Manhattan. Este mai bun când mediul este static, complet observabil, iar criteriul principal este eficiența traseului. Poate fi cea mai bună alegere în profilul `known_static`, în depozite cu hartă fixă, în jocuri sau în sisteme unde se cere un drum rapid fără fază de training. În lumea reală, familia A* este folosită în framework-uri de robotică și pathfinding: ROS 2 Navigation2 include Smac Planner, care implementează algoritmi A*-based, inclusiv un planner 2D cost-aware, Hybrid-A* și State Lattice [36]. Motoarele de joc folosesc sisteme de navigație și pathfinding pe reprezentări precum navmesh-uri; Unity documentează explicit folosirea navigation meshes pentru deplasarea inteligentă a personajelor [39].

**RiskAwareAStarAgent — planificare globală cu siguranță explicită.** Rolul său este să testeze ipoteza centrală a lucrării: drumul cel mai scurt nu este întotdeauna drumul cel mai potrivit. Agentul modifică funcția de cost astfel încât apropierea de zone periculoase să fie penalizată: $f(n) = g(n) + h(n) + w \cdot r(n)$. Este mai bun când pericolele au zonă de influență, când există persoane, echipamente fragile, zone interzise sau cost mare al incidentelor. Poate fi cel mai bun în profilul `high_risk` și în situații în care A* și Risk-Aware A* au aceeași rată de succes, dar diferă prin risc și cost. În experimentul `medium`, acesta este exact cazul: ambele ajung la 100% succes, însă Risk-Aware A* reduce expunerea la risc și costul total. În lumea reală, ideea este apropiată de planificarea pe costmaps: Nav2 folosește costmaps pentru zone cu cost mare, iar Inflation Layer adaugă costuri cu decădere exponențială în jurul obstacolelor pentru a evita trecerea prea aproape de coliziuni [37]. Smac Planner 2D este descris de Nav2 ca planner A* cost-aware [36].

**TabularQLearningAgent — învățare specializată pe coordonate absolute.** Rolul său este să reprezinte varianta cea mai interpretabilă de reinforcement learning. Agentul nu primește un model al mediului, ci învață din tranziții și recompense. Starea este poziția absolută $(rând, coloană)$, iar Q-table-ul conține valoarea fiecărei acțiuni în fiecare celulă. Este mai bun când aceeași hartă este folosită repetat, când mediul este mic și finit, iar training-ul offline este acceptabil. Poate fi cel mai bun în profilul `same_map_learning`, de exemplu pentru un robot care lucrează zilnic în același layout și poate acumula experiență specifică acelui spațiu. Limitarea majoră este generalizarea: dacă se schimbă harta, coordonatele învățate nu mai au aceeași semnificație. În piață, Q-Learning tabular pur este rar folosit direct în produse moderne deoarece nu scalează bine, dar principiul RL este folosit în simulatoare comerciale și educaționale. AWS DeepRacer, de exemplu, folosește reinforcement learning într-un simulator 3D și permite exportul modelului antrenat pentru un vehicul fizic autonom la scară mică [38].

**FeatureBasedQLearningAgent — învățare pe reguli locale generalizabile.** Rolul său este să reducă dependența de coordonate absolute. În loc să învețe „în celula (7, 4) merg dreapta”, agentul învață pe baza contextului local: există perete sus/jos/stânga/dreapta, există pericol în vecinătate, în ce direcție este obiectivul și cât de departe este acesta. Este mai bun când hărțile diferă, dar păstrează tipare locale asemănătoare: coridoare, obstacole, zone de risc și obiective. Poate deveni cel mai bun în profilul `transfer_learning`, cu suficient training pe hărți diverse, deoarece același vector de features poate apărea în medii diferite. Limitarea este aliasing-ul: două poziții pot avea același context local, dar pot necesita decizii diferite din cauza structurii globale a hărții. În lumea reală, sistemele comerciale de RL folosesc rareori exact această variantă simplă, dar folosesc aceeași idee generală: învățarea unei politici pe reprezentări care abstractizează observațiile brute. DeepRacer folosește observații din senzori și o funcție de recompensă pentru a învăța comportamente de conducere în simulare, ceea ce reprezintă o versiune mult mai avansată a aceleiași familii de abordări [38].

**FeatureRiskAwareAStarAgent — hibrid experimental între learning și planning.** Această strategie nu pretinde că înlocuiește A* sau Q-Learning-ul, ci creează o structură extensibilă în care experiența locală poate modifica costurile folosite de planificare. Agentul pornește de la Risk-Aware A*, dar în timpul training-ului acumulează penalizări pentru tipare locale care au dus la risc, coliziuni sau intrări în pericol. În evaluare, aceste penalizări se adaugă peste harta de risc explicită. Rolul său în lucrare este experimental: arată cum poate fi conectată învățarea pe features locale cu planificarea sigură, fără a introduce rețele neuronale și fără a inventa rezultate în afara metricilor produse de simulator.

Tabelul următor sintetizează alegerea practică:

| Algoritm | Rol în lucrare | Când este mai bun | Scenariu în care poate fi cel mai bun | Analog real / piață |
|----------|----------------|-------------------|--------------------------------------|---------------------|
| Random | Baseline minim | Testare, control statistic | Hărți triviale sau acțiuni echivalente | Baseline în simulatoare și RL |
| Rule-Based | Euristică locală explicabilă | Medii simple, calcul minim | Obstacole rare, reacție rapidă | Straturi reactive de siguranță |
| A* | Planner global pentru drum scurt | Hartă cunoscută, mediu static | `known_static`, cost de training zero | ROS/Nav2 Smac Planner, game pathfinding |
| Risk-Aware A* | Planner global orientat spre siguranță | Zone periculoase, cost mare al incidentelor | `high_risk`, medii cu persoane | Costmaps, inflation layers, cost-aware planners |
| Tabular Q-Learning | RL interpretabil pe coordonate | Aceeași hartă repetată | `same_map_learning` | RL tabular educațional/prototipuri |
| Feature-Based Q-Learning | RL cu transfer local | Hărți variate cu tipare comune | `transfer_learning` cu training suficient | RL pe reprezentări/features, simulatoare autonome |
| Feature-Risk A* | Hibrid experimental | Când vrem costuri locale învățate peste planificare sigură | `stochastic_execution` / `transfer_learning` explorator | Cost learning + cost-aware planning |

#### 4.9.4 Vectorul de features al `FeatureBasedQLearningAgent`

`FeatureBasedQLearningAgent` reprezintă starea ca un tuple de 11 componente, extras prin metoda `state_key(observation)`:

```python
# 4 componente: bitmask pereți în direcțiile UP/DOWN/LEFT/RIGHT
walls[0..3]   # 1 dacă celula vecină este WALL sau în afara grilei, 0 altfel

# 4 componente: bitmask pericole în direcțiile UP/DOWN/LEFT/RIGHT
dangers[0..3] # 1 dacă celula vecină este DANGER, 0 altfel

# Direcția verticală față de obiectiv: -1 (obiectiv mai sus), 0 (același rând), +1 (mai jos)
goal_vertical

# Direcția orizontală față de obiectiv: -1 (stânga), 0 (aceeași coloană), +1 (dreapta)
goal_horizontal

# Bucket distanță Manhattan față de obiectiv: 0 (≤ 2), 1 (≤ 5), 2 (> 5)
distance_bucket
```

Vectorul complet este `tuple(walls + dangers + [goal_vertical, goal_horizontal, distance_bucket])`. Reprezentarea este **independentă de coordonatele absolute** — același tuple poate apărea în colțul stâng-sus sau în centrul hărții, ceea ce permite agentului să transfere politica pe hărți nevăzute. Totuși, granularitatea limitată (bucket-uri de distanță, nu distanța exactă) introduce aliasing în stări cu configurații locale identice, dar contexte globale diferite.

#### 4.9.5 Profiluri experimentale și ciclul de viață al agentului

Modulul `experiments/compare_agents.py` definește șase **profiluri experimentale** în dicționarul `EXPERIMENT_PROFILES`. Fiecare profil include parametrul `agent_lifecycle` care controlează cum sunt create și reutilizate instanțele de agent:

| Profil | Context operațional | `agent_lifecycle` | Algoritm avantajat |
|--------|---------------------|-------------------|--------------------|
| `known_static` | Hartă complet cunoscută, condiții deterministe | `per_map` | A*, Risk-Aware A* |
| `high_risk` | Siguranța este obiectiv explicit, ponderat mai mult decât distanța | `per_map` | Risk-Aware A* |
| `stochastic_execution` | Acțiunile pot devia lateral (`movement_noise > 0`) | `per_map` | Risk-Aware A*, Feature-Based Q, Feature-Risk A* |
| `same_map_learning` | Training și evaluare pe aceeași hartă (coordonatele sunt stabile) | `per_map` | Tabular Q-Learning |
| `transfer_learning` | Training pe hărți cu seed-uri diferite față de evaluare | `shared_across_maps` | Feature-Based Q-Learning, Feature-Risk A* experimental |
| `training_cost` | Compară costul de antrenare (episoade off-policy) cu costul de planificare | `per_map` | A*, Risk-Aware A*, Feature-Based Q, Feature-Risk A* |

**Ciclul de viață `per_map`**: la fiecare hartă de evaluare, agentul este re-creat cu stare inițializată. Dacă agentul necesită training (`requires_training = True`), are loc o fază de antrenament izolată pe acea hartă înainte de evaluarea greedy. Politicile **nu se transferă** între hărți — fiecare măsurătoare reflectă o sesiune de învățare independentă.

**Ciclul de viață `shared_across_maps`** (exclusiv `transfer_learning`): un singur agent este antrenat pe hărți cu seed-uri `base_seed + 50_000 + i` (offset de 50.000), apoi evaluat pe hărțile standard cu seed-urile `base_seed + i`. Separarea seed-urilor garantează că hărțile de training și evaluare sunt structural distincte, permițând măsurarea transferului de politici.

#### 4.9.6 Agregare statistică Monte Carlo și intervale de încredere

Modulul `simulation/metrics.py` implementează funcția `aggregate_results(results)` care primește lista de `EpisodeResult` și returnează statistici agregate per agent și per hartă.

Intervalele de încredere de 95% sunt calculate prin **bootstrap non-parametric**:
- **Iterații**: 1.000 de reeșantionări cu revenire
- **Seed determinist**: 1.234 (reproductibil, dar nu independent între agenți)
- **Statistică**: media reeșantionată; percentilele α/2 și 1−α/2 definesc CI

```python
_BOOTSTRAP_SAMPLES = 1000
_BOOTSTRAP_SEED = 1234

def _bootstrap_ci(values, confidence=0.95, iterations=_BOOTSTRAP_SAMPLES, seed=_BOOTSTRAP_SEED):
    rng = random.Random(seed)
    means = [sum(rng.choices(values, k=len(values))) / len(values) for _ in range(iterations)]
    means.sort()
    alpha = (1 - confidence) / 2
    return _percentile(means, alpha * 100), _percentile(means, (1 - alpha) * 100)
```

Distributiile agregate includ: `mean`, `std`, percentilele `p05`, `p25`, `p50`, `p75`, `p95`, `min` și `max` pentru recompensă, pași și expunere la risc. Defalcarea `per_map[]` returnează success_rate per agent per `map_seed`, folosită de componenta `PerMapHeatmap` din frontend.

#### 4.9.7 Motorul de recomandare explicabilă

Funcționalitatea centrală adăugată peste comparația Monte Carlo este motorul de recomandare din `experiments/recommendation.py`. Acesta primește sumarul produs de `aggregate_results(results)` și transformă tabelul de metrici într-o decizie multi-criterială. Recomandarea nu este hardcodată pe `RiskAwareAStarAgent` sau pe un alt algoritm; scorul este calculat exclusiv din rezultatele reale ale simulării.

Obiectivele disponibile sunt:

| Obiectiv | Ce prioritizează |
|----------|------------------|
| `balanced` | Echilibru între succes, risc, cost, pași și erori operaționale |
| `safety_first` | Risc mic, coliziuni puține, intrări rare în pericol |
| `efficiency_first` | Pași puțini și cost total redus, păstrând succesul relevant |
| `robustness_first` | Rată de succes mare, timeout mic și intervale de încredere stabile |

Pentru fiecare agent, metricile pozitive și negative sunt normalizate pe intervalul observat în experiment. `success_rate` crește scorul direct, în timp ce `average_risk_exposure`, `average_total_cost`, `average_steps`, `collision_rate`, `danger_entry_rate` și `timeout_rate` sunt inversate: o valoare mai mică produce scor mai mare. Dacă sunt disponibile intervale de încredere, lățimea lor contribuie la componenta de stabilitate, utilă mai ales în obiectivul `robustness_first`.

Ieșirea API-ului Monte Carlo include:

```json
{
  "recommendation": {
    "objective": "safety_first",
    "recommended_algorithm": "Risk-Aware A*",
    "ranking": [
      {
        "rank": 1,
        "algorithm": "Risk-Aware A*",
        "score": 0.91,
        "metrics": {
          "success_rate": 1.0,
          "average_risk_exposure": 125.0,
          "average_total_cost": 124.6
        }
      }
    ],
    "explanation": "...",
    "tradeoffs": ["..."]
  }
}
```

Frontend-ul afișează recomandarea ca panou separat: strategia recomandată, obiectivul folosit, scorul, ranking-ul și compromisurile. Astfel, profesorul sau utilizatorul nu trebuie să interpreteze manual toate graficele înainte de a decide; aplicația explică ce strategie este mai potrivită pentru situația configurată și de ce.

#### 4.9.8 Analist AI pentru interpretarea rezultatelor

Peste motorul determinist de recomandare este adăugat un strat opțional de interpretare textuală bazat pe un model lingvistic local sau cloud. În implementarea curentă, backend-ul FastAPI poate apela un model Gemma servit prin Ollama. Verificarea de disponibilitate folosește endpoint-ul OpenAI-compatible, iar generarea explicației poate reveni la endpoint-ul nativ `/api/chat` cu `think=false`, pentru a evita expunerea câmpului de reasoning al modelelor Gemma.

Această componentă nu are rol de decizie. Ranking-ul, scorurile și strategia recomandată rămân calculate în `experiments/recommendation.py`, exclusiv din metricile Monte Carlo. Modelul lingvistic primește doar trei categorii de date:

- configurația experimentului (`config`);
- sumarul agregat Monte Carlo (`summary`);
- recomandarea deterministă (`recommendation`).

Promptul sistemului limitează explicit comportamentul modelului: acesta nu are voie să inventeze metrici, să contrazică ranking-ul sau să recalculeze scorurile. Rolul său este să explice în limbaj natural de ce o strategie a fost recomandată, ce compromisuri apar între siguranță și eficiență și ce limitări trebuie menționate, de exemplu număr mic de hărți, episoade puține sau instabilitate statistică.

API-ul expus de backend include:

| Endpoint | Rol |
|----------|-----|
| `/api/safe-navigation/analysis/status` | Verifică dacă analistul AI este activ și disponibil |
| `/api/safe-navigation/analysis/explain` | Generează o explicație pentru rezultatul Monte Carlo și recomandarea curentă |

În interfața React, panoul „Analist AI” apare după rularea Monte Carlo și oferă întrebări rapide, precum explicarea recomandării, motivul pentru care alți algoritmi nu au câștigat sau următorul experiment recomandat. Astfel, aplicația rămâne un simulator decizional bazat pe metrici reale, iar modelul lingvistic funcționează ca suport pedagogic pentru interpretarea rezultatelor.

### 4.10 Deployment Azure Cloud

Repository-ul include și infrastructura pentru publicarea aplicației în Azure Cloud. Arhitectura de deployment este:

```text
Azure Static Web Apps
  React/Vite frontend din web/frontend

Azure Container Apps
  Backend FastAPI + motorul Python de simulare

Azure Container Apps GPU, opțional
  Ollama/Gemma pentru panoul Analist AI, cu ingress intern

Azure Files
  Persistență pentru data/runs, Q-table-uri, CSV, JSON și PNG
  Cache separat pentru modelele Ollama la /root/.ollama

Azure Container Registry
  Imagini Docker pentru backend și, opțional, containerul Ollama

Application Insights + Log Analytics
  Observabilitate, loguri și erori backend
```

Fișierul `Dockerfile` construiește imaginea backend-ului, iar `Dockerfile.ollama` construiește imaginea opțională pentru Ollama/Gemma. `infra/main.bicep` definește resursele Azure: Static Web App, Container Registry, Storage Account, File Share pentru date, File Share pentru cache-ul Ollama, Log Analytics, Application Insights, Container Apps Environment, Container App backend și Container App LLM opțional. Workflow-urile GitHub Actions din `.github/workflows/` separă provisioning-ul infrastructurii, deployment-ul backend-ului, deployment-ul frontend-ului și deployment-ul containerului LLM.

Această componentă nu schimbă logica algoritmilor, dar este relevantă pentru demonstrație: aplicația poate fi accesată de coordonator sau comisie din browser, cu backend Python real, artefacte persistente și interfață completă pentru experimente. În varianta actuală, ruta principală prezintă simulatorul de navigare sigură, iar laboratorul Q-Learning rămâne disponibil ca flux complementar.

Pentru modelul Gemma 26B, varianta recomandată în Azure este un Container App GPU separat, de exemplu profil A100, cu `minReplicas=0` și `maxReplicas=1`. Backend-ul îl apelează prin URL intern, iar variabilele `LLM_ENABLED`, `LLM_BASE_URL` și `LLM_MODEL` controlează activarea. Dacă modelul este prea costisitor pentru demonstrație, aceeași interfață permite schimbarea tag-ului Ollama către un model mai mic, fără modificări ale API-ului sau UI-ului.

---

## Capitolul 5: Experimentare și Rezultate

### 5.1 Setup Experimental și Reproductibilitate

Evaluarea proiectului are două componente complementare. Prima componentă este pachetul Q-Learning energetic, generat prin modulul `src.final_report`, care rulează scenariile A, B, C și WAREHOUSE, exportă CSV-uri, grafice, imagini de hartă, heatmap-uri Q, trasee greedy și manifest JSON. A doua componentă este simulatorul de navigare sigură, care compară mai multe strategii pe hărți generate procedural și agregă metrici de risc, coliziuni și cost prin experimente Monte Carlo.

Comanda standard utilizată pentru pachetul Q-Learning energetic este:

```bash
python3 -m src.final_report --episodes 2000 --save-qtables
```

Configurația standard pentru scenariile A, B și C este:

| Parametru | Valoare |
|-----------|---------|
| Dimensiune grilă | 20×20 |
| Seed hartă | 42 |
| Episoade antrenare | 2.000 |
| Pași maximi per episod | 500 |
| Rata de învățare α | 0.1 |
| Factor de discount γ | 0.95 |
| Epsilon inițial | 1.0 |
| Epsilon minim | 0.01 |
| Epsilon decay | 0.995 |
| Niveluri energie | 4 buckets |
| Acțiuni | sus, jos, stânga, dreapta, stai |

Pentru scenariul WAREHOUSE, dimensiunea rămâne 20×20, dar harta nu este generată aleator: `WarehouseEnvironment` folosește un layout fix, cu rafturi, culoare, stații de încărcare și zone de pericol. Rezultatele raportate în acest capitol provin din `data/final_summary_20_42_2000.csv` și din artefactele asociate generate în directorul `data/`.

Metricile principale pentru componenta Q-Learning energetică sunt:

- **success_rate_last_100** — rata de succes pe ultimele 100 de episoade;
- **avg_reward_last_100** — recompensa medie pe ultimele 100 de episoade;
- **greedy_outcome** — rezultatul politicii greedy după antrenare;
- **greedy_steps** — numărul de pași al traseului greedy final;
- **greedy_reward** — recompensa totală a traseului greedy;
- **greedy_energy** — energia rămasă la finalul traseului greedy;
- **q_nonzero / q_total** — gradul de populare a Q-table-ului.

Pentru componenta de navigare sigură, experimentul standard folosit în această versiune a documentației este:

```bash
PYTHONPATH=. .venv/bin/python -m experiments.run_experiment \
  --scenario medium \
  --maps 5 \
  --episodes-per-map 2 \
  --training-episodes 100 \
  --seed 42
```

Acest experiment produce 60 de episoade agregate: 6 algoritmi × 5 hărți × 2 episoade per hartă. Configurația este suficient de mică pentru reproducere rapidă și suficient de clară pentru a ilustra diferența dintre succes, risc și cost.

### 5.2 Rezultate Agregate pentru Scenariile A, B, C și WAREHOUSE

Rezultatele finale generate de pachetul reproductibil sunt:

| Scenariu | Success last 100 | Reward mediu last 100 | Greedy outcome | Greedy pași | Greedy reward | Energie greedy | Q nenule / total |
|----------|-----------------:|----------------------:|----------------|------------:|--------------:|---------------:|-----------------:|
| A | 100.00% | 98.50 | target_reached | 34 | 99.00 | 88.0 | 1.982 / 8.000 |
| B | 96.00% | 86.86 | target_reached | 38 | 95.00 | 84.0 | 2.117 / 8.000 |
| C | 100.00% | 88.79 | target_reached | 12 | 89.00 | 88.0 | 2.335 / 8.000 |
| WAREHOUSE | 100.00% | 71.23 | target_reached | 77 | 72.00 | 67.0 | 4.609 / 8.000 |

Aceste valori arată că agentul învață politici funcționale în toate cele patru configurații. Diferențele dintre scenarii sunt importante:

- Scenariul A are cea mai simplă structură decizională, deoarece energia este setată la o valoare foarte mare și nu devine constrângere reală.
- Scenariul B introduce constrângerea energetică: agentul trebuie să evite epuizarea energiei și poate beneficia de celulele FOOD.
- Scenariul C testează adaptarea după schimbarea mediului; Q-table-ul nu este resetat, iar agentul continuă învățarea pe noua configurație.
- WAREHOUSE are cel mai mare număr de valori Q nenule, deoarece structura de depozit creează culoare lungi, multe stări vizitate repetat și politici mai specializate.

### 5.3 Scenariul A: Navigare cu Energie Foarte Mare

Scenariul A folosește aceeași hartă procedurală ca scenariile B și C, dar energia inițială este setată la o valoare foarte mare (`999999`). Agentul tot consumă energie la fiecare pas, însă epuizarea nu este o constrângere practică. Din acest motiv, problema se apropie de navigarea clasică spre țintă cu obstacole și penalizare per pas.

Rezultatul final este foarte stabil: rata de succes pe ultimele 100 de episoade este 100%, iar politica greedy ajunge la țintă în 34 de pași, cu reward 99.0. Q-table-ul are 1.982 intrări nenule din 8.000, ceea ce indică explorarea unei părți relevante din spațiul de stări, fără a vizita exhaustiv toate combinațiile poziție-energie-acțiune.

Artefactele asociate acestui scenariu sunt:

- `data/results_A_20_42.csv` — istoricul episoadelor;
- `data/convergence_A_20_42.png` — curba recompensei;
- `data/success_A_20_42.png` — rata de succes;
- `data/policy_e3_A_20_42.png` — politica greedy la energie ridicată;
- `data/q_heatmap_e3_A_20_42.png` — heatmap-ul valorilor Q;
- `data/greedy_path_A_20_42.png` — traseul greedy final.

### 5.4 Scenariul B: Supraviețuire cu Energie Limitată

Scenariul B este scenariul principal pentru homeostazia energetică. Agentul pornește cu 100 de unități de energie, consumă energie la deplasare, consumă mai mult pe noroi, câștigă energie prin colectarea hranei și moare dacă energia ajunge la zero sau intră într-o celulă DANGER.

Rata de succes pe ultimele 100 de episoade este 96%, iar politica greedy finală atinge ținta în 38 de pași, cu reward 95.0 și 84 unități de energie rămase. Comparativ cu Scenariul A, traseul greedy este mai lung, dar mai robust energetic. Această diferență susține ideea că aceeași poziție poate necesita acțiuni diferite în funcție de nivelul de energie.

Q-table-ul are 2.117 intrări nenule, mai mult decât în Scenariul A. Explicația este că agentul vizitează mai multe bucket-uri energetice, nu doar bucket-ul de energie ridicată. Aceasta confirmă rolul discretizării energiei în starea MDP: agentul nu învață doar unde se află, ci și ce poate permite starea sa internă.

### 5.5 Scenariul C: Mediu Dinamic cu Obstacole Relocate

Scenariul C testează adaptabilitatea la o schimbare structurală a mediului. În timpul antrenamentului, o fracțiune din obstacole este relocată, iar harta modificată devine noua hartă de bază pentru episoadele următoare. Q-table-ul nu este resetat; agentul păstrează cunoașterea acumulată și o actualizează în noul mediu.

Rezultatul final din pachetul standard este foarte bun: 100% succes pe ultimele 100 de episoade și traseu greedy de 12 pași. Q-table-ul are 2.335 intrări nenule, peste scenariile A și B, ceea ce este coerent cu necesitatea de a explora atât configurația inițială, cât și configurația post-relocare.

Interpretarea trebuie formulată prudent: nu este vorba despre transfer learning în sensul rețelelor neurale, ci despre reutilizarea valorilor Q într-un mediu parțial modificat. Totuși, experimental, agentul nu pornește de la zero după perturbare, iar valorile acumulate anterior pot accelera readaptarea atunci când zone importante ale hărții rămân similare.

### 5.6 Scenariul WAREHOUSE: Depozit Industrial Simplificat

Scenariul WAREHOUSE folosește clasa `WarehouseEnvironment`, care suprascrie generarea procedurală și construiește un layout fix 20×20. Harta conține:

- rafturi reprezentate ca obstacole;
- culoare traversabile;
- stații de încărcare reprezentate prin celule FOOD;
- zone de pericol reprezentând zone de operare pentru utilaje;
- poziție de start și destinație fixă.

Rezultatul final este 100% succes pe ultimele 100 de episoade, cu traseu greedy de 77 de pași, reward 72.0 și 67 energie rămasă. Numărul de intrări Q nenule este 4.609 / 8.000, semnificativ mai mare decât în A/B/C. Acest lucru arată că layout-ul de depozit produce o explorare mai largă a spațiului de stări, probabil din cauza culoarelor lungi, a blocurilor de rafturi și a numărului mai mare de trasee utile prin stațiile de încărcare.

Față de scenariile procedurale, WAREHOUSE nu urmărește să fie o simulare fidelă a unui depozit real cu roboți multipli, ci un studiu de caz: aceeași interfață `Environment` poate reprezenta un mediu structurat manual, apropiat conceptual de o problemă logistică.

### 5.7 Navigare Sigură și Comparație Monte Carlo

Pe lângă experimentele A/B/C/WAREHOUSE, cadrul de navigare sigură permite compararea algoritmilor pe distribuții de hărți prin șase **profiluri experimentale**, fiecare simulând un context operațional distinct.

#### Profiluri experimentale

| Profil | Context operațional real | `agent_lifecycle` | Algoritm avantajat |
|--------|--------------------------|-------------------|--------------------|
| `known_static` | Depozit cu plan fix, hartă complet accesibilă | `per_map` | A*, Risk-Aware A* |
| `high_risk` | Zonă cu persoane prezente, siguranța primează | `per_map` | Risk-Aware A* |
| `stochastic_execution` | Robot cu imprecizie mecanică, drift la acțiuni | `per_map` | Risk-Aware A*, Feature-Based Q |
| `same_map_learning` | Robot care operează repetat în același spațiu | `per_map` | Tabular Q-Learning |
| `transfer_learning` | Flotă pe locații diferite, politică transferată | `shared_across_maps` | Feature-Based Q-Learning |
| `training_cost` | Comparație cost offline (training) vs online (planificare) | `per_map` | A* fără training vs. Q cu training |

Concluzia principală este că **nu există o strategie universal optimă** — alegerea depinde de contextul operațional: dacă harta este disponibilă la planificare, dacă robotul operează repetat sau în locații variate, dacă siguranța este mai importantă decât distanța.

#### Scenariile predefinite

Scenariile predefinite sunt:

| Scenariu | Dimensiune | Probabilitate pereți | Probabilitate pericol |
|----------|-----------:|---------------------:|----------------------:|
| easy | 10×10 | 0.10 | 0.05 |
| medium | 15×15 | 0.20 | 0.10 |
| hard | 20×20 | 0.25 | 0.15 |

#### Algoritmii comparați

| Algoritm | Tip | Necesită antrenare | Observație |
|----------|-----|-------------------|------------|
| Random | baseline | Nu | Alege acțiuni aleatoriu |
| Rule-Based | euristic | Nu | Evită pericole imediate și reduce distanța Manhattan |
| A* | planificare | Nu | Caută traseu scurt cu euristică Manhattan |
| Risk-Aware A* | planificare cu cost de risc | Nu | $f(n) = g(n) + h(n) + w \cdot r(n)$ unde $r(n)$ este costul de risc al celulei |
| Tabular Q-Learning | RL tabular | Da | Învață Q pe coordonate absolute; nu generalizează pe hărți noi |
| Feature-Based Q-Learning | RL pe features locale | Da | Vector de 11 features; generalizează parțial pe hărți nevăzute |

#### Rezultate: profilul `known_static`, scenariu `medium`

Experimentul Monte Carlo standard folosit pentru documentare:

```bash
PYTHONPATH=. .venv/bin/python -m experiments.run_experiment \
  --scenario medium \
  --maps 5 \
  --episodes-per-map 2 \
  --training-episodes 100 \
  --seed 42 \
  --profile known_static
```

Rezultat: **60 episoade** agregate (6 algoritmi × 5 hărți × 2 episoade per hartă). Intervalele de încredere CI 95% sunt calculate prin bootstrap cu 1.000 de iterații și seed 1.234 — reproductibile, dar nu independente între agenți.

| Algoritm | Success rate | Reward mediu | Pași medii | Coliziuni medii | Intrări pericol | Expunere risc | Cost total | Timeout |
|----------|-------------:|-------------:|-----------:|----------------:|----------------:|--------------:|-----------:|--------:|
| A* | 100% | -34.40 | 28.40 | 0.00 | 0.00 | 161.00 | 195.40 | 0% |
| Risk-Aware A* | 100% | 0.40 | 29.60 | 0.00 | 0.00 | 125.00 | 124.60 | 0% |
| Rule-Based | 50% | -1255.70 | 174.40 | 0.00 | 0.00 | 1175.20 | 2430.90 | 50% |
| Random | 0% | -754.10 | 95.80 | 40.70 | 1.00 | 204.80 | 958.90 | 0% |
| Tabular Q-Learning | 0% | -637.00 | 103.40 | 23.80 | 1.00 | 238.80 | 875.80 | 0% |
| Feature-Based Q-Learning | 0% | -825.60 | 109.20 | 31.40 | 0.80 | 371.40 | 1197.00 | 20% |

Rezultatul cel mai important nu este că A* și Risk-Aware A* ating ambele 100% succes, ci **diferența de calitate a traseului**. Risk-Aware A* parcurge un traseu ușor mai lung (+4%), dar reduce expunerea la risc cu **22%** (161.0 → 125.0) și costul total cu **36%** (195.4 → 124.6). Aceasta ilustrează exact miza lucrării: o strategie poate fi mai potrivită pentru navigare sigură chiar dacă nu minimizează strict numărul de pași.

Agenții Random, Tabular Q-Learning și Feature-Based Q-Learning au performanțe slabe în configurația `known_static` cu training scurt (100 episoade). Interpretarea trebuie să fie prudentă: profilul `same_map_learning` arată că Tabular Q-Learning devine relevant când coordonatele sunt stabile — acolo succesul crește semnificativ după training suficient pe aceeași hartă. Profilul `transfer_learning` cu `shared_across_maps` arată că Feature-Based Q-Learning transferă parțial tipare locale, spre deosebire de Tabular Q care eșuează pe hărți nevăzute.

Această parte completează Q-Learning-ul energetic cu o comparație sistematică. Diferența dintre A* și Risk-Aware A* arată cum o funcție de cost modificată produce comportament mai sigur fără învățare. Diferența dintre Tabular Q și Feature-Based Q ilustrează problema generalizării: coordonatele absolute sunt precise pe harta de training, dar vectorul de features locale este direcția potrivită pentru transfer.

### 5.8 Discuții

Rezultatele indică trei concluzii complementare. Prima este că Q-Learning tabular este suficient de puternic pentru scenarii discrete moderate, mai ales când spațiul de stări este mic și interpretabil. A doua este că, pentru navigare pe hărți noi, algoritmii de planificare precum A* rămân foarte competitivi. A treia, cea mai importantă pentru scopul lucrării, este că succesul singur nu este o metrică suficientă: două strategii cu aceeași rată de succes pot avea profiluri foarte diferite de risc și cost.

Din perspectiva lucrării de licență, valoarea proiectului nu stă doar în obținerea unei politici Q bune, ci în platforma completă de simulare: generare procedurală validată BFS, scenarii parametrizabile, model de risc, agenți interschimbabili, export de date, artefacte vizuale, API web, interfață cloud și comparații Monte Carlo. Aceasta aliniază proiectul atât cu tematica de Reinforcement Learning, cât și cu disciplina de tehnici de simulare.


## Capitolul 6: Aplicații în Lumea Reală

### 6.1 Robotică Industrială — Depozite Autonome (Amazon Kiva)

Sistemul de roboți Amazon Kiva, ulterior integrat în Amazon Robotics, reprezintă un exemplu comercial relevant pentru principiile discutate în această lucrare. Roboții mobili din depozite trebuie să navigheze printre rafturi, să evite blocaje și să își gestioneze bateria în raport cu stațiile de încărcare. Problema este mai complexă decât scenariul WAREHOUSE din proiect, dar are aceeași structură conceptuală: navigare într-un mediu cu obstacole, constrângeri operaționale și resurse energetice limitate.

Diferențele față de simularea noastră sunt de scară și complexitate: harta unui depozit Amazon este continuă (nu discretizată pe grilă), există sute de agenți simultan (problema multi-agent), obstacolele sunt dinamice (alți roboți în mișcare), și constrângerile de timp real sunt stricte (robotul trebuie să reacționeze în milisecunde). Cu toate acestea, principiile fundamentale — navigare cu evitarea obstacolelor, gestionarea energiei, convergența prin trial-and-error — sunt aceleași.

Sistemul Amazon Robotics folosește o combinație de planificare centralizată (servere centrale care optimizează traseele tuturor roboților simultan) și control local (fiecare robot execută mișcări locale autonome pentru a evita coliziunile). Algoritmul central seamănă cu un Shortest Path augmentat cu constrângeri de baterie — similar cu politica optimă din Scenariul B al nostru, dar la scara a sute de mii de agenți.

Rezultatele implementării Amazon Robotics sunt remarcabile: creșterea vitezei de procesare a comenzilor cu 300–400%, reducerea suprafeței de depozit necesare cu 50% (prin ambalarea mai densă a rafturilor, posibilă deoarece nu mai sunt necesare culoaruri pentru muncitori) și reducerea erorilor de picking sub 0.5%. Aceste rezultate ilustrează impactul economic masiv al navigării autonome eficiente — un impact direct alimentat de cercetarea fundamentală în reinforcement learning.

### 6.2 Vehicule Autonome de Livrare (Last-Mile Delivery)

Livrarea „ultimului kilometru" (last-mile delivery) reprezintă ultima etapă a lanțului logistic și, paradoxal, cea mai costisitoare — estimările plasează costul ultimului kilometru la 28–53% din costul total al livrării (Savelsbergh & Van Woensel, 2016). Companiile DHL, FedEx și UPS explorează activ robotică și vehicule autonome pentru a reduce aceste costuri.

**Starship Technologies** operează o flotă de roboți de livrare autonomi pe trotuare, cu o autonomie de 6 ore și un spațiu de navigare similar cu grila noastră 2D: trotuarele formează un graf discret (intersecții = noduri, segmente = muchii) pe care robotul navighează de la depozit la destinatarul pachetului. Gestionarea bateriei (încărcare la depozit, monitorizarea nivelului pe traseu) este critică — un robot blocat pe trotuar cu bateria moartă este o problemă de relații publice și o pierdere economică directă.

**Nuro** și **Waymo** operează vehicule autonome pe drumuri publice, unde problema energetică este mai puțin critică (bateria e suficientă pentru sute de km), dar constrângerile de navigare sunt incomparabil mai complexe: trafic dens, condiții meteo, semnalizare rutieră, pietoni imprevizibili. Algoritmii de navigare din astfel de sisteme sunt inevitabil mai sofisticați decât Q-Learning tabular — combină planificarea pe grafuri rutiere (OpenStreetMap) cu predicția comportamentului altor participanți la trafic (rețele neurale) și controlul local (model predictiv de control, MPC). Cu toate acestea, ideea fundamentală de politică de decizie bazată pe stare (poziție + condiție internă) este comună.

**Drone de livrare** (Amazon Prime Air, Wing de la Google, Zipline) introduc dimensionalitate suplimentară față de navigarea pe sol: spațiul 3D de navigare, dinamica vântului, restricții de zbor (zonele aeroportuare, restricțiile de altitudine) și, în mod critic, consumul energetic mult mai sensibil la condițiile de zbor. O dronă care zboară împotriva vântului consumă de 2–3× mai multă energie decât în condiții calme — analogul direct al celulelor MUD din simularea noastră, care dublează costul energetic al traversării.

### 6.3 Sisteme IoT și Gestionarea Energiei în Rețele de Senzori

Rețelele de senzori wireless (WSN — Wireless Sensor Networks) sunt sisteme distribuite de noduri cu resurse limitate care colectează și transmit date din mediu. Problema gestionării energiei în WSN are o structură formal similară cu Scenariul B al nostru: fiecare nod are o baterie limitată, unele noduri pot fi reîncărcate prin energy harvesting (solar, vibrații), și obiectivul global este menținerea rețelei funcționale cât mai mult timp.

**Data Mule robotics** este o abordare în care un robot mobil navighează rețeaua de senzori, colectând date de la noduri și transportându-le la o stație de bază. Traseul robotului trebuie optimizat simultan pentru: colectarea completă a datelor de la toți senzorii, minimizarea consumului propriu de energie și timpulul total de rundă. Aceasta este exact problema „agentului nostru care colectează hrană (date) de la celulele FOOD (senzori) și le duce la TARGET (stația de bază)".

Lucrări în domeniu (Jain & Chang, 2004; Zhao & Guibas, 2004) demonstrează că abordările RL pot genera politici de navigare superioare celor statice pentru roboti Data Mule, în special în medii cu densitate variabilă de senzori și rate de generare a datelor heterogene.

**Energy harvesting mobile robots** sunt roboți care îsi reîncarcă bateria în timp ce navighează, prin panouri solare montate pe carcasă. Politica de navigare trebuie să țină cont de intensitatea luminii solare (variabilă în funcție de poziție și ora zilei) și să echilibreze colectarea de energie suplimentară cu progresul misiunii — o problemă multi-obiectiv cu structură similară homeostaziei energetice din lucrarea de față.

### 6.4 Drone pentru Căutare și Salvare în Medii Ostile

Operațiunile de căutare și salvare (Search and Rescue, SAR) reprezintă unul dintre cele mai critice și provocatoare domenii de aplicare a navigării autonome. Dronele SAR trebuie să acopere o suprafață cât mai mare în timp minim, cu baterie limitată, în condiții meteorologice adverse, localizând victime în medii structurate (clădiri colabate, păduri dense) sau nestructurate (câmpuri, suprafețe marine).

**Problema de căutare cu baterie limitată** are o structură MDP explicită: starea include poziția curentă a dronei, harta parțial explorată și nivelul bateriei; acțiunile sunt mișcările în spațiu; recompensa este proporțională cu suprafața nouă acoperită; constrângerea terminală este epuizarea bateriei înainte de returnarea la baza de încărcare. Structura este identică cu Scenariul B — înlocuiți TARGET cu baza de încărcare și FOOD cu orice zonă care oferă un câștig de informație.

Lucrări recente (Queralta et al., 2020; Macwan et al., 2011) demonstrează că RL este superioare abordărilor de tip lawn-mower (parcurgere sistematică a suprafeței) pentru operațiuni SAR în medii cu obstacole dinamice (vegetație dense care reduce vizibilitatea, clădiri parțial colabate). RL permite generarea de politici adaptate online la informația acumulată — dronele direcționează căutarea spre zonele unde probabilitatea de a găsi victime este maximă.

**Coordonarea flotelor de drone** introduce dimensionalitatea multi-agent: mai multe drone cu baterii independente trebuie să acopere o suprafață fără suprapuneri, cu reîncărcare la stații comune și transfer de informație despre zonele deja exploarate. Aceasta este o extensie directă a arhitecturii din lucrarea de față spre multi-agent RL, discutată în Capitolul 8 ca direcție de cercetare viitoare.

### 6.5 Agricultură de Precizie și Roboți Agricoli

**Agricultura de precizie** (precision agriculture) utilizează senzori și robotică pentru a optimiza utilizarea resurselor (îngrășăminte, apă, pesticide) la nivel de plantă individuală, în loc de aplicare uniformă pe suprafețe mari. Roboții agricoli (tractoare autonome, drone de monitorizare, roboți de recoltare) navighează câmpuri agricole cu structuri topologice similare grilelor noastre.

**John Deere** a lansat în 2022 primul tractor agricol complet autonom (modelul 8R), care navighează câmpul pe baza GPS și senzori de obstacole. Problema de planificare a traseului unui tractor autonom pe un câmp de 100 hectare este echivalentă cu problema noastră de navigare pe grilă, cu celule reprezentând benzi de teren (EMPTY = teren, OBSTACLE = arbori/construcții, MUD = zone umede cu tracțiune redusă, TARGET = capătul fiecărei benzi de lucru). Consumul de combustibil (sau bateria la tractoarele electrice) joacă rolul energiei din lucrarea noastră.

**FarmBot** este o platformă open-source de robot agricol la scară mică, care navighează pe un șasiu montat pe o grădină și efectuează sarcini precise (semănat, irigare, monitorizare). Deși controlul FarmBot curent este bazat pe scripturi, integrarea RL ar permite adaptarea la variații ale terenului, detectarea automată a dăunătorilor și optimizarea traseelor pe baza datelor senzoriale — exact tipul de adaptabilitate demonstrat în Scenariul C al lucrării de față.

**Roboții de recoltare** (startup-uri precum Harvest CROO Robotics, FFRobotics) navighează plantații de căpșuni sau citrice, localizând fructele coapte și recoltându-le selectiv. Constrângerile energetice sunt critice în aceste sisteme — un robot agricol care rămâne fără baterie la jumătatea rândului de plante poate distruge recolta prin blocare fizică sau poate cauza pierderi economice prin întârzieri. Gestionarea proactivă a bateriei (întoarcere la stația de încărcare înainte de epuizare) este implementată prin politici similare cu cele din Scenariul B.

### 6.6 Sisteme Medicale Autonome (Administrare Medicamente)

**TUG** (produs de Aethon, acum parte Omron) este un robot spitalicesc autonom care navighează coridoarele spitalelor pentru a livra medicamente, lenjerie, probe de laborator și alimente. Flote de TUG-uri sunt operaționale în sute de spitale din America de Nord și Europa. Problema de navigare a TUG este structurally identică cu simularea noastră: coridoarele spitalului formează o grilă, cu obstacole (uși închise, cărucioare medicale lăsate pe culoar), zone de pericol (secții sterile care nu pot fi traversate) și destinații multiple (farmacia, secțiile de spitalizare).

Particularitățile mediului spitalicesc adaugă constrângeri unice: traficul de personal medical este puternic variabil (nopțile sunt mai libere, orele de vizită mai aglomerate), prioritizarea automată a livrărilor urgente (medicamente critice > lenjerie), și necesitatea de a cede calea personalului medical în orice situație. Sistemul TUG curent folosește hartă pre-definită și planificator A*, dar există interes în comunitarea roboticii medicale pentru integrarea RL care ar permite adaptarea la variațiile dinamice ale traficului.

**Roboți de dezinfecție** (Xenex, UVD Robots) navighează sălile de spital pentru a dezinfecta suprafețele prin radiație UV. Eficiența dezinfecției depinde de distanța față de suprafețele tratate și de durata expunerii — un sistem RL poate optimiza traseul robotului pentru a maximiza acoperirea în timp minim, cu baterie limitată. Această problemă combină navigarea eficientă din Scenariul A cu gestionarea energiei din Scenariul B.

### 6.7 Jocuri Video și Inteligența Artificială Procedurală

Jocurile video au jucat un rol central în istoria RL: de la Atari DQN (Mnih et al., 2015) la AlphaGo (Silver et al., 2016) și OpenAI Five (Dota 2, 2019), jocurile au servit ca benchmark-uri pentru evaluarea algoritmilor RL. Mediile din jocuri video au proprietăți deosebit de convenabile pentru cercetare: sunt rapide (simulare în timp accelerat), reproductibile (seed-uri fixe), și au funcții de recompensă bine definite.

**Generarea procedurală de conținut** (PCG — Procedural Content Generation) este direct relevantă pentru această lucrare: grila noastră este generată procedural cu BFS-validare, exact tehnica utilizată în jocuri roguelike (Rogue, Nethack, Dwarf Fortress, Hades) pentru generarea de niveluri infinite cu solvabilitate garantată. Integrarea RL pentru navigarea NPC-urilor în niveluri procedural generate este o direcție activă de cercetare în game AI.

**Non-Player Characters (NPC)** cu comportamente de navigare Q-Learning sunt utilizate în jocuri comerciale, deși rareori menționate explicit. Unity ML-Agents (toolkit open-source de la Unity Technologies) permite antrenarea NPC-urilor cu algoritmi RL (PPO, SAC, Q-Learning) direct în motorul de joc. Comportamentele emergente generate — echipe de NPC care cooperează, inamici care se adaptează la strategia jucătorului — creează experiențe de joc mai bogate și mai imprevizibile.

**Jocul „Survival"** — supraviețuirea cu resurse limitate — este un gen de joc video direct inspirat de problema homeostaziei energetice. În jocuri ca The Long Dark, Minecraft (modul supraviețuire) sau Don't Starve, jucătorul trebuie să gestioneze simultan foamea, setea, temperatura și alte nevoi fiziologice. Un agent Q-Learning cu state augmentat energetic ar putea juca aceste jocuri cu strategii emergente non-triviale.

### 6.8 Comportament Animal și Neuroștiință Computațională

Una dintre cele mai fascinante conexiuni ale Q-Learning este cu neuroștiința: cercetările au descoperit că creierul mamifer implementează un algoritm similar Q-Learning la nivel neuronal. Dopamina, neurotransmițătorul asociat recompensei, pare să codifice eroarea de predicție temporală (Temporal Difference error) — adică exact termenul $R + \gamma V(s') - V(s)$ din actualizarea Q-Learning (Schultz, Dayan & Montague, 1997).

**Forajul optim** (optimal foraging theory) este o teorie din biologia comportamentală care modelează decizia animalelor de a alege patch-uri de hrană. Un animal trebuie să balanseze costul explorării (timp și energie pentru a găsi hrană nouă) versus exploatarea (consumul hranei din locul curent). Această dilemă este identică cu exploration-exploitation trade-off din Q-Learning, iar politica epsilon-greedy poate fi interpretată ca un model simplificat al strategiei de foraj optim.

**Navigarea spațială și celulele loc** (place cells) în hipocampul mamiferelor asigură o reprezentare internă a spațiului: fiecare celulă loc „se aprinde" când animalul se află într-o locație specifică. Aceasta este analogul direct al Q-table-ului nostru indexat pe $(rând, coloană)$ — o reprezentare tabulară a valorii locațiilor din mediu. Cercetări recente (Banino et al., 2018) demonstrează că rețelele neurale antrenate cu RL pentru navigare dezvoltă spontan reprezentări similare grid cells-urilor din entorhinal cortex — structuri neurale despre care se crede că implementează un sistem de coordonate interne.

**Homeostazia și drives biologice** sunt conceptualizate în psihologie prin **teoria reducerii drive-ului** (Hull, 1943): comportamentul animal este motivat de nevoia de a reduce stările de deficit (foame, sete, frig). Homeostatic RL (Keramati & Gutkin, 2011) formalizează matematic această teorie, demonstrând că un agent cu funcție de recompensă derivată din homeostaziei dezvoltă comportamente emergente similare cu cele observate la animale — exact comportamentul de pit-stop energetic observat în Scenariul B al lucrării de față.

---

## Capitolul 7: Simulare Practică — Robotul de Depozit

### 7.1 Prezentarea Problemei

Scenariul `WAREHOUSE` modelează o problemă simplificată de navigare într-un depozit industrial. Scopul nu este reproducerea completă a unui sistem comercial de roboți mobili, ci demonstrarea faptului că arhitectura Q-Learning implementată poate fi reutilizată pe un mediu structurat manual, diferit de hărțile generate aleator.

În această reprezentare, depozitul este o grilă 20×20 cu zone funcționale:

| Element din depozit | Reprezentare în simulator |
|--------------------|---------------------------|
| Culoar navigabil | `EMPTY` |
| Raft de depozitare | `OBSTACLE` |
| Intersecție aglomerată / zonă cu deplasare dificilă | `MUD` |
| Stație de încărcare | `FOOD` |
| Zonă de operare stivuitor | `DANGER` |
| Zonă de recepție | `START` |
| Zonă de expediere | `TARGET` |

Această mapare permite reutilizarea directă a funcției de tranziție, a sistemului energetic și a Q-table-ului. Agentul interpretează stațiile de încărcare ca surse de energie, rafturile ca obstacole, iar zonele de stivuitor ca stări terminale negative.

### 7.2 Implementarea WarehouseEnvironment

Clasa `WarehouseEnvironment` se află în `src/warehouse_scenario.py` și extinde clasa generică `Environment`. Spre deosebire de `Environment`, care construiește harta procedural prin densități de obstacole, noroi, hrană și pericol, `WarehouseEnvironment` folosește un layout fix definit printr-o listă de șiruri de caractere:

```python
_WAREHOUSE_LAYOUT = [
    list("S.................."),
    list("..................."),
    list("..................."),
    list(".WWW.WWW.WWW.WWW.WW."),
    ...
    list("D..................D"),
    list("..................."),
    list("....T.............."),
]
```

Simbolurile sunt mapate la `CellType` astfel:

```python
_SYMBOL_TO_CELL = {
    "S": CellType.START,
    "T": CellType.TARGET,
    "W": CellType.OBSTACLE,
    "F": CellType.FOOD,
    "M": CellType.MUD,
    "D": CellType.DANGER,
    ".": CellType.EMPTY,
}
```

Constructorul impune dimensiunea 20×20, deoarece layout-ul este proiectat manual pentru această grilă. Metoda `generate()` ignoră seed-ul și reconstruiește harta fixă, apoi validează existența unui drum cu BFS. Metoda `reset()` reface layout-ul inițial la fiecare episod, asigurând reproductibilitatea antrenamentului.

`WarehouseEnvironment` adaugă și metoda `get_warehouse_stats()`, care returnează statistici utile pentru raportare:

- numărul total de celule;
- numărul de rafturi;
- numărul de culoare libere;
- numărul de stații de încărcare;
- numărul de zone MUD;
- numărul de zone DANGER;
- distanța BFS optimă;
- coordonatele startului și ale țintei.

### 7.3 Rezultate Experimentale WAREHOUSE

În pachetul final, scenariul WAREHOUSE este rulat cu aceiași hiperparametri de bază ca scenariile A/B/C, dar cu harta fixă de depozit. Rezultatele din `data/final_summary_20_42_2000.csv` sunt:

| Metrică | Valoare |
|---------|--------:|
| Episoade | 2.000 |
| Rata succes ultimele 100 episoade | 100.00% |
| Reward mediu ultimele 100 episoade | 71.23 |
| Greedy outcome | target_reached |
| Greedy pași | 77 |
| Greedy reward | 72.00 |
| Energie rămasă greedy | 67.0 |
| Q nenule | 4.609 / 8.000 |

Comparativ cu scenariile procedurale, WAREHOUSE are cel mai mare număr de intrări Q nenule. Acest lucru este explicabil prin structura hărții: culoarele lungi, stațiile de încărcare și zonele de risc creează multe stări relevante, iar agentul explorează mai mult din spațiul de poziții și energie.

Traseul greedy este mai lung decât în scenariile A/B/C, dar acest lucru nu este un defect. Harta de depozit este mai restrictivă, iar rafturile formează blocuri care obligă agentul să circule prin culoare. Într-un mediu de depozit, eficiența nu se reduce doar la distanța Manhattan, ci include evitarea zonelor periculoase și menținerea energiei.

### 7.4 Artefacte Generate

Pentru scenariul WAREHOUSE, pachetul final produce aceleași tipuri de artefacte ca pentru scenariile procedurale:

| Artefact | Fișier |
|----------|--------|
| Istoric episoade | `data/results_WAREHOUSE_20_0.csv` |
| Curba recompensei | `data/convergence_WAREHOUSE_20_0.png` |
| Decăderea epsilon | `data/epsilon_WAREHOUSE_20_0.png` |
| Rata de succes | `data/success_WAREHOUSE_20_0.png` |
| Harta depozitului | `data/map_WAREHOUSE_20_0.png` |
| Politica greedy | `data/policy_e3_WAREHOUSE_20_0.png` |
| Heatmap valori Q | `data/q_heatmap_e3_WAREHOUSE_20_0.png` |
| Heatmap vizite | `data/visit_heatmap_WAREHOUSE_20_0.png` |
| Heatmap TD-error | `data/td_heatmap_WAREHOUSE_20_0.png` |
| Traseu greedy | `data/greedy_path_WAREHOUSE_20_0.png` |
| Q-table | `data/qtable_WAREHOUSE_20_0.npy` |
| Manifest | `data/manifest_WAREHOUSE_20_0.json` |

Aceste artefacte fac scenariul verificabil: un evaluator poate vedea harta, traseul, politica, valorile Q și istoricul episoadelor fără să ruleze din nou întregul antrenament.

### 7.5 Interpretare

Scenariul WAREHOUSE susține o concluzie importantă: arhitectura proiectului este reutilizabilă. `Trainer`, `Agent` și `QLearning` nu trebuie modificați pentru a lucra pe un mediu nou, atât timp cât mediul respectă contractul `Environment`: poziție de start, poziție țintă, grilă, `try_move()` și BFS pentru validare.

Totuși, scenariul rămâne o aproximare. Un depozit real ar include mai mulți roboți, obstacole dinamice, planificare centralizată, priorități de sarcini, rezervări de culoare și constrângeri de timp real. Implementarea curentă trebuie interpretată ca un studiu de caz educațional și experimental, nu ca o soluție industrială completă.


## Capitolul 8: Concluzii și Direcții Viitoare

### 8.1 Concluzii Principale

Lucrarea de față a demonstrat că un simulator grid-based poate fi folosit pentru evaluarea strategiilor de navigare sigură în medii necunoscute, generate procedural. Contribuția principală nu este doar antrenarea unui agent care ajunge la țintă, ci construirea unui cadru în care strategiile pot fi comparate după succes, risc, coliziuni, costul traseului, eficiență și generalizare.

**Concluzia 1 — Simulatorul mută analiza de la succes binar la calitatea traseului.** Întrebarea centrală nu mai este „agentul a ajuns sau nu?”, ci „care strategie este mai potrivită pentru navigare sigură în medii necunoscute?”. Metricile de risc, coliziuni și cost evidențiază diferențe pe care rata de succes le-ar ascunde.

**Concluzia 2 — Risk-Aware A* demonstrează valoarea planificării safety-aware.** În experimentul Monte Carlo `known_static` pe scenariu `medium`, A* și Risk-Aware A* ating ambele 100% succes, dar Risk-Aware A* reduce expunerea la risc cu 22% (161.0 → 125.0) și costul total cu 36% (195.4 → 124.6). Această diferență nu este capturată de o metrică de succes binar — tocmai de aceea cadrul multi-criterial este esențial.

**Concluzia 3 — Cele șase profiluri experimentale reproduc contexte operaționale reale.** `known_static` simulează un depozit cu hartă fixă, `high_risk` prioritizează siguranța față de distanță, `stochastic_execution` testează robustețea la zgomot în acțiuni, `same_map_learning` arată când Q-Learning tabular devine relevant, `transfer_learning` separă seed-urile de training și evaluare (offset +50.000) pentru a măsura transferul real de politici, iar `training_cost` compară costul offline al RL cu costul online al planificării.

**Concluzia 4 — Q-Learning rămâne relevant ca strategie interpretabilă.** Pe o grilă 20×20 cu 4 niveluri energetice și 5 acțiuni, Q-table-ul are 8.000 de intrări, suficient de puțin pentru a fi inspectabil și ușor de antrenat. Pachetul energetic obține 100% succes pe ultimele 100 de episoade în Scenariul A, 96% în Scenariul B, 100% în Scenariul C și 100% în WAREHOUSE.

**Concluzia 5 — Homeostazia energetică îmbogățește comportamentul agentului.** Adăugarea energiei în starea MDP face ca aceeași poziție din hartă să poată avea politici diferite în funcție de nivelul energetic. Agentul nu optimizează doar distanța până la țintă, ci și supraviețuirea, evitarea costurilor mari și folosirea surselor de energie atunci când acestea sunt relevante.

**Concluzia 6 — Platforma susține reproductibilitatea experimentală.** Modulul `src.final_report` generează într-un singur flux CSV-uri, grafice, manifest JSON, Q-table-uri, heatmap-uri și trasee greedy. Modulul `experiments/compare_agents.py` adaugă evaluare Monte Carlo pe hărți generate procedural cu CI 95% bootstrap (1.000 iterații, seed 1.234). Împreună, aceste fluxuri reduc riscul ca textul lucrării, prezentarea și codul să raporteze rezultate diferite.

**Concluzia 7 — Recomandarea explicabilă transformă simulatorul într-un instrument decizional.** Pe lângă tabele și grafice, sistemul produce un ranking al strategiilor pentru obiectivul selectat: echilibru, siguranță, eficiență sau robustețe. Această componentă răspunde direct întrebării lucrării: nu doar dacă agentul ajunge la țintă, ci ce strategie merită aleasă pentru condițiile configurate.

**Concluzia 8 — Aplicația web face proiectul demonstrabil și analiza accesibilă.** Backend-ul FastAPI și frontend-ul React/Vite permit rularea experimentelor din browser, vizualizarea traseelor și descărcarea artefactelor. Pagina dedicată `/safe-navigation/monte-carlo` cu șapte tab-uri (distribuții boxplot, CI bars, scatter risc-recompensă, heatmap per hartă, breakdown eșecuri, heatmap de ocupanță, export CSV/PNG) transformă datele statistice brute în analiză vizuală completă. Infrastructura Azure arată că sistemul poate fi publicat ca aplicație cloud, utilă pentru demonstrația în fața coordonatorului sau a comisiei.


### 8.2 Limitări ale Abordării

**Limitarea 1 — Scalabilitatea la spații de stări mari.** Dimensiunea Q-table-ului crește liniar cu produsul dimensiunilor fiecărei componente a stării. O grilă de 100×100 cu 8 buckets energetice ar necesita $100 \times 100 \times 8 \times 5 = 400.000$ intrări — gestionabil. Dar o grilă 1.000×1.000 (dimensiunea realistă a unui depozit mare) cu 16 buckets energetice și 8 acțiuni ar necesita $1.000 \times 1.000 \times 16 \times 8 = 128.000.000$ intrări — impractică atât ca memorie, cât și ca explorare completă.

**Limitarea 2 — Nucleul energetic este în principal determinist.** Scenariile A/B/C/WAREHOUSE presupun tranziții deterministe ($P(s'|s,a) \in \{0, 1\}$), cu excepția schimbării controlate din Scenariul C. Cadrul de navigare sigură include un parametru `movement_noise`, dar acesta nu este integrat în Q-Learning-ul energetic principal. Mediile reale au senzori cu zgomot, actuatori imperfecți și obstacole dinamice neplanificate.

**Limitarea 3 — Un singur agent.** Arhitectura este single-agent. Depozitele reale cu sute de roboți necesită algoritmi multi-agent RL care gestionează coordonarea, comunicarea și evitarea coliziunilor la nivel de flotă. Extinderea la multi-agent introduce complexitate exponențială în spațiul de stări și acțiuni combinate.

**Limitarea 4 — Funcție de recompensă manuală.** Funcția de recompensă din lucrarea de față este definită manual, bazată pe intuiție și cunoaștere expertă. În aplicații complexe din lumea reală, proiectarea funcției de recompensă (reward engineering) este o problemă dificilă, iar funcțiile slab proiectate pot conduce la comportamente neașteptate sau exploatare de loophole-uri.

**Limitarea 5 — Generalizare limitată pentru Q-table-ul absolut.** Q-table-ul energetic antrenat pe o hartă cu seed 42 nu se transferă direct la o hartă complet diferită. Cadrul de navigare sigură include un `FeatureBasedQLearningAgent`, care încearcă să reducă această limitare prin features locale, dar nucleul principal al lucrării rămâne tabular și dependent de coordonate absolute.

**Limitarea 6 — Aplicația cloud este prototip demonstrativ.** Backend-ul FastAPI, frontend-ul React și infrastructura Azure demonstrează fezabilitatea publicării aplicației, dar nu includ toate proprietățile unui produs de producție: autentificare, management avansat al costurilor, cozi de joburi distribuite, limitare per utilizator sau recuperare completă după întreruperi.

### 8.3 Direcții de Cercetare Viitoare

**Direcția 1 — Deep Q-Networks cu comparație sistematică.** Extinderea naturală a lucrării este implementarea DQN și compararea sistematică cu Q-Learning tabular pe aceleași scenarii. Ipoteza de testat: DQN va fi inferior pe grile mici (mai lent, mai instabil) dar superior pe grile mari (≥ 50×50), identificând exact pragul de dimensiune la care trecerea la rețele neurale devine justificată.

**Direcția 2 — Multi-Agent Q-Learning pentru flote de roboți.** Extinderea la scenarii cu 2–10 agenți simultani care navigează aceeași grilă fără coliziuni și cu optimizare globală a eficienței flotei. Abordările candidate includ Independent Q-Learning (fiecare agent învață independent, ignorând ceilalți), Cooperative Q-Learning (agenții partajează Q-table-ul) și abordările de tip QMIX (descompunerea funcției Q globale în contribuții individuale).

**Direcția 3 — Transfer Learning cross-scenarii.** Investigarea sistematică a capacității de transfer a Q-table-ului între scenarii cu hărți diferite, dimensiuni diferite și configurații de energie diferite. Ipoteza: există un nucleu de politici generalizabile (evitare obstacole, navigare spre gradient de valori) care se transferă, în timp ce politicile specifice hărții (memoria locală a obstacolelor) nu se transferă.

**Direcția 4 — Reward Shaping Avansat.** Explorarea funcțiilor de recompensă alternative sau augmentate — de exemplu, recompensă pozitivă proporțională cu apropierea de TARGET (potential-based shaping), penalizare pentru revisitarea celulelor deja parcurse (anti-loop), sau recompensă bonus pentru eficiența energetică. Analiza impactului fiecărui element de reward shaping asupra vitezei de convergență și calității politicii finale.

**Direcția 5 — Q-Learning Ierarhic pentru Planificare pe Două Niveluri.** Implementarea unui sistem ierarhic: un Q-Learning de nivel înalt alege sub-goaluri (waypoint-uri intermediare: prima hrană, primul culoar, etc.), iar un Q-Learning de nivel scăzut navighează la fiecare waypoint. Aceasta ar permite descompunerea problemelor complexe în sub-probleme mai simple, cu convergență mai rapidă și politici mai modulare.

**Direcția 6 — Medii Parțial Observabile (POMDP).** Eliminarea ipotezei observabilității complete: agentul vede doar celulele din raza sa senzorială (de exemplu, 3×3 în jurul poziției sale), nu harta completă. Aceasta modelizează mai realist roboții reali și necesită estimarea stării complete din observații parțiale — o problemă semnificativ mai dificilă, abordabilă prin Recurrent Q-Networks sau metode bazate pe credință (belief state).

---

## Bibliografie

1. **Bellman, R.** (1957). *Dynamic Programming*. Princeton University Press.

2. **Watkins, C. J. C. H.** (1989). *Learning from Delayed Rewards*. PhD Thesis, Cambridge University.

3. **Watkins, C. J. C. H., & Dayan, P.** (1992). Q-Learning. *Machine Learning*, 8(3-4), 279–292.

4. **Sutton, R. S., & Barto, A. G.** (2018). *Reinforcement Learning: An Introduction* (2nd ed.). MIT Press.

5. **Mnih, V., Kavukcuoglu, K., Silver, D., et al.** (2015). Human-level control through deep reinforcement learning. *Nature*, 518(7540), 529–533.

6. **Silver, D., Huang, A., Maddison, C. J., et al.** (2016). Mastering the game of Go with deep neural networks and tree search. *Nature*, 529(7587), 484–489.

7. **van Hasselt, H.** (2010). Double Q-Learning. *Advances in Neural Information Processing Systems*, 23, 2613–2621.

8. **Schaul, T., Quan, J., Antonoglou, I., & Silver, D.** (2015). Prioritized experience replay. *arXiv preprint* arXiv:1511.05952.

9. **Sutton, R. S.** (1991). Dyna, an integrated architecture for learning, planning, and reacting. *SIGART Bulletin*, 2(4), 160–163.

10. **Hart, P. E., Nilsson, N. J., & Raphael, B.** (1968). A formal basis for the heuristic determination of minimum cost paths. *IEEE Transactions on Systems Science and Cybernetics*, 4(2), 100–107.

11. **Dijkstra, E. W.** (1959). A note on two problems in connexion with graphs. *Numerische Mathematik*, 1(1), 269–271.

12. **Khatib, O.** (1986). Real-time obstacle avoidance for manipulators and mobile robots. *The International Journal of Robotics Research*, 5(1), 90–98.

13. **Keramati, M., & Gutkin, B. S.** (2011). A reinforcement learning theory for homeostatic regulation. *Advances in Neural Information Processing Systems*, 24, 82–90.

14. **Schultz, W., Dayan, P., & Montague, P. R.** (1997). A neural substrate of prediction and reward. *Science*, 275(5306), 1593–1599.

15. **Mei, Y., Lu, Y. H., Hu, Y. C., & Lee, C. S. G.** (2004). Deployment of mobile robots with energy and timing constraints. *IEEE Transactions on Robotics*, 22(3), 507–522.

16. **Queralta, J. P., Taipalmaa, J., Pullinen, B. C., et al.** (2020). Collaborative multi-robot search and rescue: Planning, coordination, perception and active vision. *IEEE Access*, 8, 211855–211870.

17. **Zhu, Y., Mottaghi, R., Kolve, E., et al.** (2017). Target-driven visual navigation in indoor scenes using deep reinforcement learning. *IEEE International Conference on Robotics and Automation (ICRA)*.

18. **Anderson, P., Chang, A., Chaplot, D. S., et al.** (2018). On evaluation of embodied navigation agents. *arXiv preprint* arXiv:1807.06757.

19. **Sartoretti, G., Kerr, J., Shi, Y., et al.** (2019). PRIMAL: Pathfinding via reinforcement and imitation multi-agent learning. *IEEE Robotics and Automation Letters*, 4(3), 2378–2385.

20. **Banino, A., Barry, C., Uria, B., et al.** (2018). Vector-based navigation using grid-like representations in artificial agents. *Nature*, 557(7705), 429–433.

21. **Savelsbergh, M., & Van Woensel, T.** (2016). 50th anniversary invited article—city logistics: Challenges and opportunities. *Transportation Science*, 50(2), 579–590.

22. **Jain, A., & Chang, E. Y.** (2004). Adaptive sampling for sensor networks. *Proceedings of the 1st International Workshop on Data Management for Sensor Networks*, 10–16.

23. **Macwan, A., Vilela, J., Nejat, G., & Benhabib, B.** (2011). A multirobot path-planning strategy for autonomous wilderness search and rescue. *IEEE Transactions on Cybernetics*, 41(6), 1454–1468.

24. **Liu, B., & Golley, J.** (2012). Optimal energy management strategies for mobile robot with battery constraints. *2012 IEEE/RSJ International Conference on Intelligent Robots and Systems*, 4221–4226.

25. **Thorndike, E. L.** (1911). *Animal Intelligence: Experimental Studies*. Macmillan.

26. **Hull, C. L.** (1943). *Principles of Behavior: An Introduction to Behavior Theory*. Appleton-Century-Crofts.

27. **Minsky, M.** (1961). Steps toward artificial intelligence. *Proceedings of the IRE*, 49(1), 8–30.

28. **Littman, M. L.** (1994). Markov games as a framework for multi-agent reinforcement learning. *Proceedings of the Eleventh International Conference on Machine Learning*, 157–163.

29. **OpenAI.** (2019). *Dota 2 with Large Scale Deep Reinforcement Learning*. arXiv preprint arXiv:1912.06680.

30. **Brockman, G., Cheung, V., Pettersson, L., et al.** (2016). OpenAI Gym. *arXiv preprint* arXiv:1606.01540.

31. **Amazon Robotics.** (2024). *Amazon Robotics Technology Overview*. Retrieved from https://www.aboutamazon.com/news/operations/10-years-of-amazon-robotics

32. **Aethon Inc.** (2023). *TUG Autonomous Mobile Robot — Technical Specifications*. Omron Corporation.

33. **John Deere.** (2022). *John Deere 8R Autonomous Tractor — Product Overview*. Deere & Company.

34. **Zipline International.** (2023). *Autonomous Drone Delivery Systems*. Retrieved from https://flyzipline.com

35. **Starship Technologies.** (2024). *Autonomous Delivery Robots — Fleet Operations Report*. Retrieved from https://www.starship.xyz

36. **Open Navigation LLC.** (2026). *Nav2 Smac Planner Documentation*. Retrieved from https://docs.nav2.org/configuration/packages/configuring-smac-planner.html

37. **Open Navigation LLC.** (2026). *Nav2 Inflation Layer Parameters*. Retrieved from https://docs.nav2.org/configuration/packages/costmap-plugins/inflation.html

38. **Amazon Web Services.** (2026). *DeepRacer on AWS — Solution Overview*. Retrieved from https://docs.aws.amazon.com/solutions/latest/deepracer-on-aws/solution-overview.html

39. **Unity Technologies.** (2023). *Unity Manual: Navigation and Pathfinding*. Retrieved from https://docs.unity.cn/520/Documentation/Manual/Navigation.html

---

*Lucrare depusă la Facultatea de Matematică și Informatică, Universitatea din București, în vederea obținerii titlului de Licențiat în Informatică.*

*București, Iunie 2026*

---

**Declarație de autenticitate**

Subsemnatul, Andrei Demit, declar pe propria răspundere că lucrarea de licență intitulată „Simulator Grid-Based pentru Evaluarea Strategiilor de Navigare Sigură în Medii Generate Procedural" este elaborată de mine, pe baza studiului literaturii de specialitate și a implementării originale, și nu conține fragmente plagiate din alte lucrări. Toate sursele bibliografice utilizate sunt citate conform normelor academice în vigoare.

*Semnătura:* _________________________ *Data:* _________________________
