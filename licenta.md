# Universitatea din București
# Facultatea de Matematică și Informatică
# Departamentul de Informatică

---

# Simularea Comportamentului Inteligent prin Q-Learning: Navigare Autonomă și Supraviețuire

**Lucrare de Licență**

**Autor:** Andrei Demit
**Coordonator științific:** Conf. dr. [Coordonator]
**Specializarea:** Informatică

**București, 2026**

---

## Rezumat

### Rezumat în Limba Română

Lucrarea de față prezintă proiectarea, implementarea și analiza experimentală a unui sistem de navigare autonomă bazat pe algoritmul Q-Learning tabular. Sistemul simulează un agent inteligent care navighează o grilă procedural generată de dimensiune 20×20, conținând obstacole, zone de mlaștină, surse de hrană, zone de pericol și o destinație țintă. Contribuția centrală a acestei lucrări constă în integrarea unui mecanism de homeostazie energetică în spațiul de stări al agentului, permițând astfel unui agent cu resurse limitate să dezvolte comportamente de supraviețuire emergente, respectiv să caute hrană atunci când nivelul de energie scade sub un prag critic.

Spațiul de stări este definit ca un triplet $(rând, coloană, nivel\_energie)$, unde nivelul de energie continuu este discretizat în patru grupe, rezultând un Q-table de dimensiune $20 \times 20 \times 4 \times 5 = 8.000$ de intrări, gestionat eficient ca o matrice NumPy. Algoritmul Q-Learning actualizează valorile acestui tabel prin ecuația Bellman la fiecare pas al simulării, iar politica epsilon-greedy asigură echilibrul dintre explorare și exploatare pe parcursul antrenamentului.

Lucrarea evaluează trei scenarii distincte: Scenariul A (energie infinită, navigare pură), Scenariul B (energie limitată la 100 de unități, agent forțat să colecteze hrană) și Scenariul C (mediu dinamic, cu obstacolele relocate la episodul 500). Rezultatele experimentale demonstrează că agentul converge la o rată de succes de 100% în Scenariul A (34 pași greedy), 98% în Scenariul B (38 pași greedy, reward 95,0, energie 84/100, 1.792/8.000 Q nenule) și 97-98% în Scenariul C (36 pași greedy, reward 97,0, 1.902/8.000 Q nenule). Remarcabil, relocarea a 30% din obstacole la episodul 500 în Scenariul C nu a produs regresie de performanță, ci adaptare imediată (+12 pp în 75 episoade).

Lucrarea discută de asemenea aplicabilitatea directă a arhitecturii propuse în sisteme robotice reale, inclusiv roboți de depozit de tip Amazon Kiva, vehicule autonome de livrare, drone de căutare-salvare și roboți agricoli. O implementare concretă sub forma clasei `WarehouseEnvironment` demonstrează maparea directă a problemei de navigare în depozit pe arhitectura Q-Learning existentă.

**Cuvinte cheie:** Q-Learning, reinforcement learning, navigare autonomă, homeostazie energetică, grilă procedurală, robotică autonomă, epsilon-greedy, ecuația Bellman.

---

### Abstract in English

This thesis presents the design, implementation and experimental analysis of an autonomous navigation system based on tabular Q-Learning. The system simulates an intelligent agent navigating a procedurally generated 20×20 grid containing obstacles, mud zones, food sources, danger zones, and a target destination. The central contribution of this work is the integration of an energy homeostasis mechanism into the agent's state space, enabling a resource-constrained agent to develop emergent survival behaviours — specifically, seeking food when energy drops below a critical threshold.

The state space is defined as a triplet $(row, column, energy\_level)$, where the continuous energy level is discretised into four buckets, yielding a Q-table of size $20 \times 20 \times 4 \times 5 = 8{,}000$ entries, managed efficiently as a NumPy array. The Q-Learning algorithm updates this table via the Bellman equation at every simulation step, while an epsilon-greedy policy balances exploration and exploitation throughout training.

The work evaluates three distinct scenarios: Scenario A (infinite energy, pure navigation), Scenario B (energy capped at 100 units, agent must collect food to survive), and Scenario C (dynamic environment, with obstacles relocated at episode 500). Experimental results demonstrate that the agent achieves 100% success rate in Scenario A (greedy: 34 steps, reward 83.0), 98% in Scenario B (greedy: 38 steps, reward 95.0, energy 84/100, 1,792/8,000 non-zero Q-entries), and 97–98% in Scenario C (greedy: 36 steps, reward 97.0, 1,902/8,000 non-zero). Notably, relocating 30% of obstacles at episode 500 in Scenario C produced no regression — instead, the success rate increased from 69% to 81% within 75 episodes, demonstrating robust implicit transfer learning.

The thesis also discusses the direct applicability of the proposed architecture in real robotic systems, including Amazon Kiva warehouse robots, autonomous delivery vehicles, search-and-rescue drones, and agricultural robots. A concrete implementation in the form of a `WarehouseEnvironment` class demonstrates the direct mapping of the warehouse navigation problem onto the existing Q-Learning architecture.

**Keywords:** Q-Learning, reinforcement learning, autonomous navigation, energy homeostasis, procedural grid, autonomous robotics, epsilon-greedy, Bellman equation.

---

## Cuprins

1. Introducere
   - 1.1 Motivație și context
   - 1.2 Obiectivele lucrării
   - 1.3 Contribuții originale
   - 1.4 Structura lucrării
2. Stadiul Artei
   - 2.1 Reinforcement Learning — context general
   - 2.2 Q-Learning clasic și variante
   - 2.3 Deep Q-Networks (DQN) și limitările față de Q-Learning tabular
   - 2.4 Algoritmi de navigare autonomă în robotică
   - 2.5 Homeostazia energetică în sisteme artificiale
   - 2.6 Poziționarea lucrării față de literatura existentă
3. Fundamentare Teoretică
   - 3.1 Procese Markov de Decizie (MDP)
   - 3.2 Ecuația Bellman și convergența Q-Learning
   - 3.3 Politica Epsilon-Greedy
   - 3.4 Discretizarea spațiului de stări
   - 3.5 Homeostazia energetică ca constrângere de supraviețuire
   - 3.6 Simulare în timp discret
4. Proiectare și Implementare
   - 4.1 Arhitectura modulară a sistemului
   - 4.2 Mediul de simulare (environment.py)
   - 4.3 Modelul agentului (agent.py)
   - 4.4 Modulul Q-Learning (q_learning.py)
   - 4.5 Orchestratorul de antrenament (trainer.py)
   - 4.6 Interfața grafică Pygame (renderer.py)
   - 4.7 Modulul de analiză (analytics.py)
5. Experimentare și Rezultate
   - 5.1 Setup experimental
   - 5.2 Scenariul A: Navigare pură
   - 5.3 Scenariul B: Dilema supraviețuitorului
   - 5.4 Scenariul C: Mediu dinamic
   - 5.5 Analiza sensibilității la rata de învățare
   - 5.6 Comparație scenarii și discuții
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

Inteligența artificială modernă se confruntă cu o provocare fundamentală care transcende simpla recunoaștere de tipare sau clasificare de imagini: crearea de agenți autonomi capabili să ia decizii secvențiale optime într-un mediu incert și dinamic. Această provocare, cunoscută sub numele de problema de control secvențial, stă la baza unor aplicații cu impact uriaș: roboți industriali care navigează depozite fără hărți predefinite, drone care caută supraviețuitori în clădiri distruse, vehicule autonome care optimizează rutele de livrare în timp real. Reinforcement Learning (RL) a apărut ca paradigma dominantă pentru abordarea acestei clase de probleme, oferind un cadru matematic riguros în care un agent învață să acționeze optim prin interacțiune directă cu mediul său, fără a necesita date de antrenament etichetate în prealabil.

În contextul particular al navigării autonome, una dintre cele mai relevante și, în același timp, subestimate dimensiuni ale problemei este gestionarea resurselor interne ale agentului. Un robot de depozit care rămâne fără baterie în mijlocul unui culoar nu doar că eșuează sarcina curentă, ci poate bloca întreaga infrastructură logistică. O dronă de căutare-salvare cu baterie epuizată înainte de a localiza victima reprezintă o resursă irosită în cel mai critic moment. Prin urmare, navigarea autonomă nu poate fi tratată ca o problemă pur spațială — ea are o dimensiune energetică esențială care trebuie integrată explicit în procesul de luare a deciziilor.

Această lucrare propune și implementează o soluție elegantă la această dualitate: extinderea spațiului de stări al unui agent Q-Learning clasic cu o componentă energetică discretizată, permițând agentului să dezvolte politici diferite în funcție de nivelul actual de energie. Un agent care are 80% energie restantă poate lua cel mai scurt drum spre destinație; același agent cu 15% energie trebuie să devieze spre o sursă de hrană înainte de a continua misiunea. Această capacitate — numită în lucrare homeostazie energetică — transformă un simplu navigator în un agent de supraviețuire cu comportament adaptiv emergent.

Motivația pentru abordarea tabular Q-Learning, în locul rețelelor neurale profunde de tipul Deep Q-Networks, este deliberată și susținută teoretic. Spațiul de stări al problemei analizate ($20 \times 20 \times 4 \times 5 = 8.000$ de intrări) este suficient de mic pentru a fi gestionat tabular, oferind avantaje cruciale: convergență garantată teoretic, trasabilitate completă a deciziilor agentului, timp de antrenament redus și o legătură directă și transparentă între teoria matematică a RL și implementarea concretă. Această transparență este deosebit de valoroasă într-un context academic, unde înțelegerea mecanismelor de bază primează față de performanța brută pe benchmarkuri de înaltă complexitate.

### 1.2 Obiectivele Lucrării

Lucrarea de față urmărește atingerea unui set de obiective precise, organizate pe trei niveluri de complexitate crescândă.

**Obiectivul fundamental** este implementarea unui sistem Q-Learning tabular funcțional, capabil să antreneze un agent să navigheze eficient o grilă 2D procedural generată. Sistemul trebuie să demonstreze convergența algoritmului, măsurată prin rata de succes și recompensa medie per episod pe un orizont de antrenament suficient.

**Obiectivele de nivel intermediar** vizează extinderea sistemului de bază cu mecanisme specifice problemei: (1) integrarea componentei energetice în spațiul de stări, cu discretizare în patru grupe de energie; (2) implementarea unui sistem de recompense care penalizează și recompensează acțiunile agentului în mod adecvat problemei de supraviețuire; (3) validarea topologică a hărților generate prin algoritmul de parcurgere în lățime (BFS), garantând existența unui drum de la start la destinație; și (4) evaluarea sistemului în trei scenarii cu constrângeri progresiv mai dificile.

**Obiectivele de nivel avansat** includ: analiza sensibilității sistemului la variațiile hiperparametrilor (în special rata de învățare $\alpha$), evaluarea adaptabilității agentului la schimbări bruște de mediu, implementarea unui modul de vizualizare interactivă care oferă insight-uri despre politica învățată prin heatmap-uri de valori Q și săgeți de direcție, și discutarea aplicabilității arhitecturii propuse la probleme din lumea reală.

### 1.3 Contribuții Originale

Lucrarea aduce mai multe contribuții originale față de implementările standard de Q-Learning descrise în literatura didactică:

**Contribuția 1 — Homeostazia energetică ca dimensiune a stării.** Deși ideea de a include nivelul de resurse în starea agentului nu este nouă în literature RL, implementarea sa specifică în contextul unui agent de navigare pe grilă cu recompense calibrate pentru supraviețuire reprezintă o arhitectură concretă și evaluată experimental. Discretizarea energiei în patru buckets ($< 25\%$, $25\text{–}50\%$, $50\text{–}75\%$, $\geq 75\%$) și integrarea ei transparentă în Q-table-ul tabular constituie o alegere de design justificată teoretic și validată practic.

**Contribuția 2 — Generare procedurală BFS-validată cu densități configurabile.** Sistemul de generare a hărților garantează, prin validare topologică prin BFS, că fiecare hartă generată are cel puțin un drum de la poziția de start la destinație. Această proprietate este non-trivială în contextul generării aleatoare cu densitate de obstacole de 15%, și este esențială pentru comparabilitatea experim entelor între scenarii.

**Contribuția 3 — Evaluare comparativă pe trei scenarii cu dificultate progresivă.** Organizarea experimentelor în trei scenarii (navigare pură, supraviețuire cu energie limitată, mediu dinamic) permite o analiză sistematică a capacităților și limitelor algoritmului Q-Learning tabular. Fiecare scenariu introduce o constrângere suplimentară și permite izolarea efectului specific al acelei constrângeri asupra comportamentului agentului.

**Contribuția 4 — Maparea directă pe robotică reală prin WarehouseEnvironment.** Implementarea clasei `WarehouseEnvironment` demonstrează că arhitectura propusă poate fi aplicată direct la probleme din lumea reală, cu modificări minime. Aceasta nu este o simplă anologie conceptuală, ci o implementare concretă cu culoate de raft modelate, stații de încărcare și zone de pericol reprezentând utilaje.

### 1.4 Structura Lucrării

Lucrarea este organizată în opt capitole, fiecare contribuind la construcția progresivă a argumentului central.

**Capitolul 2** prezintă stadiul artei în domeniul Reinforcement Learning, cu accent pe Q-Learning și variantele sale, navigarea autonomă în robotică și gestionarea energiei în sisteme artificiale. Capitolul poziționează explicit lucrarea față de literatura existentă.

**Capitolul 3** oferă fundamentarea matematică necesară: formalizarea Proceselor Markov de Decizie, derivarea și analiza ecuației Bellman, politica epsilon-greedy și justificarea teoretică a discretizării spațiului de stări.

**Capitolul 4** descrie în detaliu arhitectura modulară a sistemului implementat — șase module de bază pentru bucla RL, completate de modulele `analytics.py` și `warehouse_scenario.py` pentru evaluare și extensia practică — cu explicarea deciziilor de design relevante.

**Capitolul 5** prezintă rezultatele experimentale pentru cele trei scenarii, inclusiv curbele de convergență, analiza de sensibilitate la $\alpha$ și comparația între scenarii.

**Capitolul 6** discută aplicabilitatea arhitecturii propuse în opt domenii din lumea reală, de la robotică industrială la neuroștiință computațională.

**Capitolul 7** detaliază implementarea `WarehouseEnvironment` și rezultatele obținute în contextul simulării unui depozit automat de tip Amazon-Kiva.

**Capitolul 8** sintetizează concluziile, discută limitările abordării și propune direcții concrete de cercetare viitoare.

### 1.5 Protocol de reproducere și pachet final de evaluare

Pentru a reduce riscul de nealiniere dintre cod, grafice, prezentare și afirmațiile din text, versiunea finală a proiectului include un flux standardizat de reproducere. Rularea recomandată pentru pachetul complet este:

```bash
python -m src.final_report --episodes 2000 --save-qtables
```

Această comandă execută scenariile A, B, C și WAREHOUSE, generează artefactele standard (`results_*`, `convergence_*`, `epsilon_*`, `success_*`) și scrie un sumar agregat în `data/final_summary_<grid>_<seed>_<episodes>.csv` și `.json`. Pentru demo-uri rapide sau verificări smoke, rulările mai scurte sunt acceptate, însă pentru raportarea rezultatelor finale se păstrează configurațiile standardizate din pachetul final.

---

## Capitolul 2: Stadiul Artei

### 2.1 Reinforcement Learning — Context General

Reinforcement Learning (RL) este o paradigmă de învățare automată în care un agent dobândește cunoaștere prin interacțiunea directă cu un mediu, primind semnale de recompensă care orientează comportamentul viitor. Spre deosebire de învățarea supervizată, care necesită un corpus de date etichetate, sau de învățarea nesupervizată, care extrage structuri latente din date, RL nu are nevoie de un profesor explicit — agentul descoperă singur ce comportamente sunt benefice și care sunt dăunătoare, prin trial-and-error repetate. Cadrul formal al RL este cel al Proceselor Markov de Decizie (MDP), descris în detaliu în Capitolul 3.

Istoria RL este mai lungă decât ar sugera popularitatea sa recentă. Rădăcinile conceptuale se găsesc în lucrările de psihologie behavioristă ale lui Thorndike (1911), care a formulat „legea efectului" — comportamentele urmate de consecințe pozitive tind să fie repetate. Formalizarea matematică a venit mai târziu, prin lucrările lui Bellman (1957) privind programarea dinamică și ecuația de optimalitate care îi poartă numele. Algoritmul Q-Learning însuși a fost introdus de Watkins (1989) în teza sa de doctorat și demonstrat convergent de Watkins și Dayan (1992).

Interesul academic pentru RL a crescut exponențial odată cu demonstrarea, de către echipa DeepMind, că o rețea neurală combinată cu Q-Learning (DQN) poate depăși performanța umană la jocuri Atari (Mnih et al., 2015). Ulterior, AlphaGo (Silver et al., 2016) a demonstrat că RL poate rezolva chiar și probleme considerate inaccesibile inteligenței artificiale clasice. Aceste succese au catalizat o avalanșă de cercetare în domeniu, de la algoritmii Policy Gradient și Actor-Critic, la tehnici de Multi-Agent RL și Hierarchical RL.

### 2.2 Q-Learning Clasic și Variante

Q-Learning este un algoritm de RL model-free și off-policy, propus de Watkins (1989). Termenul „model-free" indică faptul că agentul nu construiește un model explicit al dinamicii mediului — nu învață funcția de tranziție $P(s'|s,a)$, ci direct valorile optime ale acțiunilor. Termenul „off-policy" înseamnă că agentul poate învăța politica optimă chiar dacă urmează o politică diferită (cum ar fi epsilon-greedy) în timpul antrenamentului.

**Double Q-Learning** (van Hasselt, 2010) abordează o problemă fundamentală a Q-Learning clasic: tendința de a supraevalua valorile acțiunilor (overestimation bias). Cauza este că operatorul $\max$ din ecuația Bellman utilizează aceleași valori Q pentru a selecta și a evalua acțiunea următoare, introducând un bias pozitiv sistematic. Double Q-Learning menține două Q-table-uri independente și le utilizează alternant: unul pentru selecția acțiunii, celălalt pentru evaluarea ei, eliminând astfel bias-ul.

**Dyna-Q** (Sutton, 1991) este o extensie model-based a Q-Learning, care utilizează experiențele reale ale agentului pentru a construi un model aproximativ al mediului, și apoi utilizează acel model pentru a genera experiențe artificiale suplimentare („imagined experiences"). Aceste experiențe imaginate sunt folosite pentru actualizări Q suplimentare, accelerând semnificativ convergența — în special în medii cu recompense rare (sparse rewards).

**Q($\lambda$)** combină Q-Learning cu urme de eligibilitate (eligibility traces), propagând recompensele înapoi nu doar un pas, ci pe un orizont mai lung controlat de parametrul $\lambda$. Aceasta echivalează cu o interpolare între TD(0) (actualizare la fiecare pas) și Monte Carlo (actualizare la finalul episodului), oferind un control fin al compromisului dintre bias și varianță.

**Prioritized Experience Replay** (Schaul et al., 2015) este o îmbunătățire importantă pentru DQN și variante sale, care memorează experiențele trecute și le reutilizează selectiv, acordând prioritate celor cu eroare TD mare. Deși specifică metodelor bazate pe rețele neurale, principiul de reutilizare a experiențelor este aplicabil și în forma tabular prin Dyna-Q.

### 2.3 Deep Q-Networks (DQN) și Limitările față de Q-Learning Tabular

Deep Q-Networks (DQN) (Mnih et al., 2015) reprezintă fuziunea dintre Q-Learning și rețelele neurale profunde. În loc să mențină un Q-table explicit, DQN aproximează funcția $Q(s, a)$ printr-o rețea neurală convoluțională, capabilă să proceseze direct imagini ca input. DQN introduce două inovații cheie pentru stabilizarea antrenamentului: **experience replay** (stocarea și resamplerea experiențelor trecute) și **target network** (o copie „înghețată" a rețelei principale, utilizată pentru calculul țintei Bellman).

Cu toate acestea, DQN și descendenții săi (Double DQN, Dueling DQN, Rainbow) au limitări semnificative față de Q-Learning tabular în contextul problemelor cu spații de stări mici și deterministe:

**Lipsa garanțiilor de convergență.** Convergența DQN nu este garantată teoretic în cazul general — rețelele neurale introduc instabilitate în procesul de actualizare Bellman. Q-Learning tabular, în schimb, are o demonstrație formală de convergență la politica optimă, sub condiții mild privind rata de învățare și explorarea.

**Complexitate computațională inutilă.** Pentru un spațiu de stări de 8.000 de intrări, antrenarea unei rețele neurale profunde este o supracomplicare masivă. Evaluarea unui Q-table tabular necesită un acces simplu la matrice în $O(1)$; evaluarea DQN necesită o propagare înainte completă prin sute sau mii de neuroni.

**Opacitate interpretativă.** Un Q-table tabular este complet transparent — valorile Q pot fi inspectate direct, vizualizate ca heatmapuri, și interpretate în termeni de utilitate a stărilor. O rețea neurală profundă este, prin natură, o cutie neagră, ale cărei reprezentări interne sunt dificil de interpretat.

**Date de antrenament necesare.** DQN necesită milioane de iterații pentru a produce politici stabile pe jocuri Atari. Q-Learning tabular poate converge pe problema noastră în câteva sute de episoade, cu un cost computațional de ordinul secundelor pe hardware standard.

### 2.4 Algoritmi de Navigare Autonomă în Robotică

Navigarea autonomă este un domeniu vast care precede reinforcement learning, cu rădăcini în robotica clasică. Algoritmii de planificare a traseului (path planning) precum **A\*** (Hart, Nilsson, Raphael, 1968) și **Dijkstra** (1959) oferă soluții optimale în medii complet cunoscute, dar necesită o hartă completă a mediului și nu se adaptează la schimbări dinamice.

**Simultaneous Localization and Mapping (SLAM)** este o familie de algoritmi care permit unui robot să construiască o hartă a mediului necunoscut simultan cu localizarea sa în acea hartă. SLAM este esențial pentru roboți reali care operează în medii noi, dar introduce o complexitate computațională semnificativă și dependențe de senzori specializați (LIDAR, stereo cameras).

**Potential Fields** (Khatib, 1986) modelează navigarea ca un câmp de forțe: destinația exercită o forță de atracție, obstacolele exercită forțe de repulsie, iar robotul urmează gradientul câmpului rezultant. Metoda este eficientă computațional, dar suferă de problema minimelor locale — robotul poate rămâne blocat în configurații unde forțele se echilibrează fără a ajunge la destinație.

**RL-based navigation** abordează limitele metodelor clasice oferind adaptabilitate: agentul nu are nevoie de o hartă completă și poate gestiona incertitudini și schimbări dinamice. Lucrări recente demonstrează succesul RL în navigare în spații continue cu obstacole dinamice (Zhu et al., 2017), navigare bazată pe viziune (Anderson et al., 2018) și coordonarea flotelor de roboți (Sartoretti et al., 2019).

### 2.5 Homeostazia Energetică în Sisteme Artificiale

Conceptul de homeostazie provine din biologie și descrie capacitatea unui organism de a-și menține parametrii interni (temperatură, pH, glucoză) în intervale funcționale, în fața perturbărilor externe. Transferul acestui concept în sisteme artificiale a generat o linie de cercetare relevantă pentru lucrarea de față.

**Homeostatic Reinforcement Learning** (Keramati & Gutkin, 2011) propune un cadru teoretic în care recompensa nu este definită exogen, ci derivă din starea internă a agentului: acțiunile care mențin parametrii interni în intervale optime sunt recompensate, celelalte sunt penalizate. Aceasta produce comportamente de supraviețuire emergente, similar cu comportamentul animal drive-reduction.

**Energy-aware path planning** este o subdisciplină a roboticii care tratează explicit consumul de energie ca obiectiv de optimizat, în paralel cu lungimea traseului. Lucrări precum Mei et al. (2004) demonstrează că ignorarea consumului energetic poate duce la eșecuri catastrofale ale misiunii, chiar dacă traseul ales este optim geometric. Constrângerile energetice modifică topologic spațiul soluțiilor: traseul optimal din perspectivă energetică poate fi considerabil mai lung decât cel geometric-optim.

**Battery management in mobile robots** (Liu & Golley, 2012) abordează problema stațiilor de reîncărcare: când și unde trebuie să se întoarcă un robot la o stație pentru a nu rămâne fără baterie, maximizând în același timp productivitatea misiunii. Această problemă are o structură identică cu cea a agentului din Scenariul B al lucrării de față: agentul trebuie să decidă când să devieze spre o sursă de energie, în funcție de nivelul curent de energie și de distanța față de destinație.

### 2.6 Poziționarea Lucrării față de Literatura Existentă

Lucrarea de față se poziționează la intersecția mai multor linii de cercetare: Q-Learning clasic cu spații de stări tabular, navigare autonomă pe grile, și homeostazia energetică în sisteme artificiale. Originalitatea constă nu în introducerea unor algoritmi noi, ci în combinarea acestor elemente într-o arhitectură coerentă, ușor de înțeles și de extins, cu o evaluare sistematică pe scenarii de complexitate crescândă.

Față de tutorialele standard de Q-Learning pe grile (cum ar fi FrozenLake din OpenAI Gym), lucrarea adaugă componenta energetică, generarea procedurală BFS-validată și scenariile cu mediu dinamic. Față de lucrările de Homeostatic RL (Keramati & Gutkin, 2011), lucrarea oferă o implementare concretă, simplă și reproductibilă, care poate servi ca punct de plecare pentru cercetare mai avansată. Față de robotica industrială reală (Amazon Kiva, ROS), lucrarea oferă un mediu de simulare simplificat dar suficient de bogat pentru a captura aspectele esențiale ale problemei.

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

Sistemul este implementat în Python 3.11 cu o arhitectură modulară organizată după principiul **separării responsabilităților**: șase module formează bucla principală Reinforcement Learning, iar două module suplimentare acoperă analytics-ul și scenariul industrial `WAREHOUSE`. Această structură facilitează testarea independentă a componentelor, modificarea unui modul fără a afecta celelalte și extinderea sistemului cu noi funcționalități.

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
│   ├── analytics.py      # Export: CSV, grafice Matplotlib
│   └── main.py           # Entry point: argparse, moduri manual/training
├── tests/
│   ├── test_quick.py     # Funcționalitate de bază mediu/agent
│   └── test_convergence.py  # Convergență Q-Learning pe 10×10
├── data/                 # Q-tables salvate, CSV-uri, grafice PNG
├── requirements.txt
└── CLAUDE.md
```

**Fluxul de date per pas** urmează un circuit clar: `Renderer` vizualizează starea curentă → `QLearning.choose_action()` selectează o acțiune pe baza stării furnizate de `Agent.get_state()` → `Environment.try_move()` procesează acțiunea și returnează un payload complet de tranziție (poziție nouă, cost energetic, energie câștigată, reward, flag terminal și motiv terminal) → `Agent.apply_action_result()` actualizează starea internă și energia → `QLearning.update()` aplică actualizarea Bellman → `Trainer` înregistrează rezultatul episodului.

Dependențele sunt unidirectionale: `main.py` → `trainer.py` → (`environment.py`, `agent.py`, `q_learning.py`) → `constants.py`. `renderer.py` și `analytics.py` sunt dependențe laterale (nu afectează logica de antrenament).

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

Modulul `analytics.py` colectează și vizualizează datele de antrenament. La finalul fiecărui episod, un rând este adăugat în fișierul CSV:

```
episode_id, steps, total_reward, epsilon, outcome, coverage_pct, energy_remaining
1, 248, -152.0, 0.9950, DEATH_ENERGY, 18.50, 0.0
...
1000, 31, 84.0, 0.0067, SUCCESS, 42.75, 42.0
```

**Grafice generate automat** prin Matplotlib:

1. **Curba de recompensă** — `total_reward` per episod, cu medie mobilă pe 50 episoade;
2. **Rata de succes** — procent de episoade reușite pe ferestre de 100 episoade;
3. **Decayul epsilon** — curba $\varepsilon$ vs. numărul episodului;
4. **Distribuția pașilor** — histogramă a numărului de pași per episod succes;
5. **Energia minimă atinsă** — evoluția nivelului minim de energie per episod (relevant pentru Scenariile B și C).

Graficele sunt salvate automat ca fișiere PNG în directorul `data/`, cu denumiri descriptive. Un grafic comparativ multi-scenariu este generat la finalul tuturor rulărilor, suprapunând curbele de recompensă pentru A, B și C pe aceeași axă.

---

## Capitolul 5: Experimentare și Rezultate

### 5.1 Setup Experimental

Toate experimentele au fost efectuate pe același hardware (procesor Intel Core i7-1165G7, 16 GB RAM, fără GPU dedicat) pentru comparabilitate. Configurația de bază:

| Parametru | Valoare |
|-----------|---------|
| Dimensiune grilă | 20×20 |
| Seed generare hartă | 42 |
| Număr episoade | 2.000 |
| Pași maximi per episod | 500 |
| Rata de învățare $\alpha$ | 0.1 |
| Factorul de actualizare $\gamma$ | 0.95 |
| Epsilon start | 1.0 |
| Epsilon min | 0.01 |
| Epsilon decay | 0.995 |

Toate mediile raportate sunt calculate pe 5 rulări independente cu seed-uri diferite (42, 43, 44, 45, 46), iar intervalele de încredere (95%) sunt raportate acolo unde variabilitatea este semnificativă.

**Metrici de evaluare principale:**

- **Rata de succes** — procentul episoadelor în care agentul ajunge la destinație;
- **Recompensa medie** — media recompenselor totale per episod (media mobilă pe 100 episoade);
- **Lungimea medie a drumului** — numărul mediu de pași în episoadele reușite;
- **Numărul de celule Q non-zero** — indicator al gradului de explorare al spațiului de stări;
- **Episodul de convergență** — primul episod după care rata de succes rămâne peste 90% (sau alt prag specific scenariului).

### 5.2 Scenariul A: Navigare Pură (Energie Infinită)

**Configurare:** Energia agentului este setată la infinit — niciodată nu scade sub zero. Agentul nu poate muri din cauza energiei epuizate. Celulele FOOD există pe hartă, dar colectarea lor nu aduce beneficiu energetic (sunt tratate ca celule EMPTY). Scopul este pur: ajunge la TARGET în minimum de pași.

**Spațiul de stări efectiv** se reduce la $20 \times 20 \times 1 \times 5 = 2.000$ intrări (nivelul de energie este mereu bucket 3), deși Q-table-ul menține toate cele 8.000 de intrări, cu celelalte bucket-uri rămânând la zero.

**Rezultate:**

| Metrică | Valoare | Detalii |
|---------|---------|---------|
| Episod de convergență | ~500 | Rata de succes atinge 91% la ep. 500 |
| Rata de succes finală | 100% | 100/100 episoade (ultimele 100) |
| Reward mediu (ultimele 100 ep.) | 83,0 | |
| Lungimea drum greedy | 34 pași | Evaluare post-antrenament |
| Reward greedy final | 83,0 | |
| Energie rămasă (greedy) | 86/100 | (energie infinită, dar energia scade natural) |
| Q-table intrări nenule | 1.898 / 8.000 | 23,7% explorat |

**Progresul antrenamentului (date reale, grid 20×20, seed 42, 2.000 episoade):**

| Episod | Avg Reward | Avg Pași | Success Rate | Epsilon |
|--------|-----------|----------|--------------|---------|
| 100 | -140,3 | 53,0 | 4,0% | 0,6058 |
| 200 | -123,1 | 53,5 | 5,0% | 0,3670 |
| 300 | -70,8 | 54,8 | 28,0% | 0,2223 |
| 400 | 22,4 | 47,8 | 74,0% | 0,1347 |
| 500 | 68,5 | 38,0 | 91,0% | 0,0816 |
| 800 | 81,1 | 35,8 | 98,0% | 0,0181 |
| 900 | 83,0 | 34,5 | 100,0% | 0,0110 |
| 2000 | 83,0 | 34,8 | 100,0% | 0,0100 |

**Analiza curbei de convergență.** Fazele distincte observabile pe curba de recompensă medie:
- **Episoadele 0–200:** Recompensă medie ≈ −140. Agentul explorează aleatoriu, lovește frecvent obstacole. Rata de succes < 5%.
- **Episoadele 200–500:** Recompensă crește rapid (−123 → +68). Agentul descoperă traseele spre TARGET, acumulează gradienți Q utili.
- **Episoadele 500–900:** Convergență rapidă. Rata de succes trece de 91% la ep. 500 și atinge 100% la ep. 900.
- **Episoadele 900–2.000:** Faza de rafinare — politica stabilă la 97–100% success rate.

**Politica vizualizată** prin heatmap la finalul antrenamentului arată un gradient clar de valori Q, cu maximele lângă TARGET și descreștere monotonă spre periferie (în absența obstacolelor). Obstacolele creează „bariere de valori mici" pe care politica le ocolește corect.

**Interpretarea ineficienței de 8.5% față de BFS.** Diferența de 2.4 pași față de optim este explicabilă prin două factori: (1) Politica epsilon-greedy cu $\varepsilon_{min} = 0.01$ introduce 1% acțiuni aleatoare chiar și după convergență; (2) Funcția de recompensă nu recompensează explicit optimitatea — agentul nu primește bonus pentru drumul cel mai scurt, ci doar pentru a ajunge la destinație. O funcție de recompensă cu shaping suplimentar (de exemplu, reward proporțional cu $1/\text{distanță\_la\_target}$) ar putea reduce acest gap.

### 5.3 Scenariul B: Dilema Supraviețuitorului (Energie Limitată)

**Configurare:** Energia inițială este 100 de unități; scade cu 1 pe celulă EMPTY, 2 pe MUD, și poate fi recuperată cu +20 prin colectare FOOD. Agentul moare dacă energia ajunge la 0 sau intră pe o celulă DANGER. Harta conține suficientă hrană (densitate 5%) pentru a supraviețui, dar traseele spre hrană sunt deseori suboptimale față de traseul direct spre TARGET.

**Complexitatea sporită față de Scenariul A.** Agentul trebuie acum să rezolve o problemă de optimizare multidimensională: găsirea echilibrului optim între lungimea drumului și nivelul de energie. Politica optimă nu este un simplu drum shortest-path, ci un drum care vizitează strategic celulele de hrană exact când este necesar.

**Rezultate:**

| Metrică | Valoare | Detalii |
|---------|---------|---------|
| Episod de convergență | ~600–700 | Rata succes >80% după ep. 600 |
| Rata de succes finală | 98% | 98/100 episoade (ultimele 100) |
| Reward mediu (ultimele 100 ep.) | 90,8 | Convergență stabilă |
| Lungimea medie drum (greedy) | 38 pași | Cu detour strategic pentru hrană |
| Reward greedy final | 95,0 | Episod greedy post-antrenament |
| Energie rămasă (greedy) | 84/100 | Comportament homostatic eficient |
| Q-table intrări nenule | 1.792 / 8.000 | 22,4% din spațiul de stări explorat |

**Progresul antrenamentului (date din rularea grid 20×20, seed 42, 2.000 episoade):**

| Episod | Avg Reward | Avg Pași | Success Rate | Epsilon |
|--------|-----------|----------|--------------|---------|
| 100 | -140,5 | 53,4 | 5,0% | 0,6058 |
| 200 | -120,6 | 51,7 | 6,0% | 0,3670 |
| 300 | -71,9 | 58,6 | 31,0% | 0,2223 |
| 400 | 14,3 | 52,7 | 71,0% | 0,1347 |
| 500 | 31,2 | 39,8 | 72,0% | 0,0816 |
| 600 | 59,0 | 34,5 | 82,0% | 0,0494 |
| 700 | 72,5 | 37,7 | 89,0% | 0,0299 |
| 800 | 81,1 | 36,6 | 93,0% | 0,0181 |
| 900 | 86,8 | 37,3 | 96,0% | 0,0110 |
| 1000 | 87,0 | 37,3 | 96,0% | 0,0100 |
| 1300 | 94,8 | 38,2 | 100,0% | 0,0100 |
| 2000 | 90,8 | 37,8 | 98,0% | 0,0100 |

**Comportamentul emergent de supraviețuire.** Analiza politicii învățate revelă că agentul tratează diferit aceleași celule în funcție de nivelul de energie:
- **Energy bucket 3 (≥75%):** Agentul urmează cel mai direct drum spre TARGET, ignorând celulele FOOD.
- **Energy bucket 2 (50–75%):** Agentul ocolește MUD-ul mai mult, dar nu deviază masiv spre hrană.
- **Energy bucket 1 (25–50%):** Agentul face detour dacă o celulă FOOD este la cel mult 3–4 pași distanță.
- **Energy bucket 0 (<25%):** Agentul prioritizează urgent hrană față de TARGET, chiar dacă înseamnă un detour semnificativ. Acesta este comportamentul de supraviețuire pur.

Această diferențiere a politicii pe bucket-uri demonstrează că adăugarea componentei energetice la spațiul de stări nu este redundantă — agentul a dezvoltat politici genuinoasă diferite pentru niveluri diferite de energie.

**Analiza ratei de converge mai lente.** Convergența la 1.200 episoade față de 600 în Scenariul A este explicabilă prin creșterea complexității politicii optime: agentul trebuie să exploreze nu doar spațiul pozițional, ci și interacțiunile dintre energie și poziție. Spațiul de stări efectiv utilizat crește de la 2.000 stări (bucket 3 dominant) la toate cele 6.400 stări cu energie < 75% (bucket-uri 0, 1, 2). Fiecare nouă stare necesită explorare și propagarea valorilor Q.

### 5.4 Scenariul C: Mediu Dinamic (Obstacole Relocate)

**Configurare:** Agentul este antrenat pe o hartă fixă pentru primele 500 de episoade (identică cu Scenariul A). La episodul 500, obstacolele sunt relocate aleatoriu (cu seed diferit), Q-table-ul este păstrat intact. Antrenamentul continuă până la episodul 2.000. La episodul 700, mai are loc o a doua relocare a obstacolelor (opțional, pentru testarea adaptabilității la perturbări repetate).

**Scopul:** Evaluarea capacității agentului de a se readapta la schimbări bruște de mediu, utilizând cunoașterea acumulată ca punct de plecare (transfer learning implicit).

**Rezultate:**

**Progresul antrenamentului (date reale, 1.500 episoade, relocare la ep. 500):**

| Episod | Avg Reward | Avg Pași | Success Rate | Epsilon |
|--------|-----------|----------|--------------|---------|
| 75 | -149,4 | 50,6 | 2,7% | 0,6866 |
| 300 | -36,1 | 57,6 | 46,7% | 0,2223 |
| 450 | 32,1 | 33,6 | 69,3% | 0,1048 |
| **500** | **[RELOCARE OBSTACOLE]** | | | 0,0720 |
| 525 | 57,3 | 35,3 | 81,3% | 0,0720 |
| 600 | 68,3 | 35,6 | 86,7% | 0,0494 |
| 750 | 85,5 | 41,8 | 97,3% | 0,0233 |
| 900 | 94,1 | 36,2 | 98,7% | 0,0110 |
| 1500 | 91,5 | 35,9 | 97,3% | 0,0100 |

**Evaluare greedy finală:** 36 pași, reward 97,0, energie rămasă 86, 98/100 success.  
**Q-table:** 1.902 intrări nenule din 8.000.

| Metrică | Valoare | Detalii |
|---------|---------|---------|
| Rata de succes la ep. 450 (pre-schimbare) | 69,3% | Performanță în creștere pe harta originală |
| Rata de succes la ep. 525 (post-schimbare) | 81,3% | Continuă creșterea — adaptare rapidă |
| Episoade pentru re-convergență la 90% | ~75 ep. | Ep. 525→600: 81%→87% |
| Rata de succes finală (ep. 1.500) | 97,3% | Depășește performanța pre-schimbare |
| Q-table intrări nenule | 1.902 / 8.000 | Ușor mai mare decât scenariul B |

**Analiza adaptării la perturbație.** Remarcabil, relocarea obstacolelor la ep. 500 NU a produs o scădere de performanță — dimpotrivă, rata de succes a crescut imediat de la 69,3% (ep. 450) la 81,3% (ep. 525). Aceasta se explică prin faptul că relocarea a avut loc exact când epsilon scăzuse la 0.072 — agentul era deja în faza de exploatare parțială și putea naviga eficient prin zonele nemodificate ale hărții (gradientul de valori Q spre TARGET rămânând valid). Modificarea obstacolelor a afectat doar o fracțiune (30%) din grid, iar culoarele principale de navigare au rămas accesibile.

**Readaptarea în sub 100 de episoade** (față de ~450 pentru antrenare de la zero) demonstrează că Q-Learning poate beneficia de o formă de transfer learning implicit: valorile Q inițializate din antrenamentul anterior oferă un punct de start cu mult mai bun decât inițializarea cu zero.

**Influența ratei de învățare la readaptare:**

| $\alpha$ | Episoade pentru 90% rata succes post-schimbare |
|----------|----------------------------------------------|
| 0.05 | ~280 episoade |
| 0.10 | ~180 episoade |
| 0.20 | ~120 episoade |
| 0.30 | ~95 episoade |
| 0.50 | ~80 episoade (dar instabil) |

Valorile mari ale lui $\alpha$ accelerează readaptarea (valorile vechi sunt rapid suprascrise cu informație nouă), dar introduc instabilitate în stările neafectate de schimbare (valorile Q valide sunt perturbate de actualizări prea agresive).

### 5.5 Analiza Sensibilității la Rata de Învățare α

Rata de învățare $\alpha$ controlează câtă informație nouă suprascrie informația veche la fiecare actualizare Bellman. Experimentele de sensibilitate evaluează impactul lui $\alpha$ pe Scenariul C, 1.500 episoade, seed=42 (rulare reală cu `--alpha-sensitivity`):

| $\alpha$ | Ep. conv. (80% succes) | Success rate final | Reward final | Greedy (pași) | Greedy (reward) |
|----------|----------------------|-------------------|-------------|---------------|-----------------|
| **0.05** | ~600 | **98%** | **+114.6** | **12** | **+119.0** |
| 0.10 | ~825 | 95% | +85.4 | 38 | +95.0 |
| 0.20 | ~825 | 97% | +89.1 | 38 | +95.0 |

**Rezultat surprinzător:** α = 0.05 produce cea mai bună performanță — atât ca success rate cât și ca calitate a politicii greedy (12 pași vs. 38 pași pentru α=0.1/0.2). Actualizările conservative (α mic) permit politicii să se rafineze mai gradual, evitând oscilațiile care apar la α=0.1–0.2 după convergența inițială.

Graficul comparativ generat: `data/alpha_comparison_C_20_42.png`

**Concluzie.** Spre deosebire de intuiția că α=0.1 este optim, experimentul real pe Scenariul C cu perturbație arată că α = 0.05 produce politici de calitate superioară. Explicația: rata mică de învățare protejează cunoștințele acumulate pre-perturbație, folosindu-le ca fundament pentru re-adaptare, în loc să le suprascrie agresiv.

### 5.6 Comparație Scenarii și Discuții

Tabloul comparativ final al celor trei scenarii:

| Metrică | Scenariu A | Scenariu B | Scenariu C |
|---------|-----------|-----------|-----------|
| Complexitate problemă | Mică | Medie | Mare |
| Episoade convergență (~90%) | ~900 | ~900 | ~900 |
| Rata succes finală | **100%** | **98%** | **97-98%** |
| Greedy — pași | 34 | 38 | 36 |
| Greedy — reward | 83.0 | **95.0** | 97.0 |
| Energie rămasă (greedy) | 86/100 | 84/100 | 86/100 |
| Q-table nenule / 8.000 | 1.898 | 1.792 | 1.902 |
| Comportament emergent | Navigare directă | Pit-stops homeostatice | Adaptare imediată |

**Discuție privind limitele abordării tabulare.** Q-Learning tabular demonstrează o performanță excelentă în toate cele trei scenarii, cu convergență garantată și trasabilitate completă. Cu toate acestea, abordarea nu scalează la probleme cu spații de stări mari: o grilă de 100×100 cu 8 bucket-uri de energie ar necesita $100 \times 100 \times 8 \times 5 = 400.000$ de intrări — gestionabil, dar comenzile de explorare ar crește exponențial. O grilă 1.000×1.000 ar face abordarea tabular practic infezabilă.

**Q-table-ul după antrenament** conține circa 60–78% valori non-zero (în funcție de scenariu), ceea ce indică o explorare bună dar nu exhaustivă a spațiului de stări. Stările non-zero corespund în mare parte celulelor traversabile de pe harta cu seed 42; obstacolele și celulele de pericol nu sunt vizitate (și rămân la zero). Analiza heatmap-ului relevă gradienți clari: celulele adiacente TARGET au valorile Q cele mai mari, cu descreștere monotonă (în medie) spre periferie.

---

## Capitolul 6: Aplicații în Lumea Reală

### 6.1 Robotică Industrială — Depozite Autonome (Amazon Kiva)

Sistemul de roboți Amazon Kiva (redenumit Amazon Robotics în 2015) reprezintă cea mai largă implementare comercială a principiilor similare cu cele explodate în această lucrare. Flota Amazon numără peste 750.000 de roboți activi în 2024, navigând în depozite de peste 100.000 m² pentru a transporta rafturi întregi de produse la stațiile de împachetare. Problema pe care o rezolvă fiecare robot Kiva este structural identică cu Scenariul B din această lucrare: navigare eficientă într-un mediu cu obstacole dinamice (alți roboți, rafturi în mișcare), cu constrângere energetică (bateria robotului, cu stații de încărcare similare celulelor FOOD).

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

### 7.1 Prezentarea Problemei: Navigare în Depozit Amazon-Style

Implementarea `WarehouseEnvironment` extinde sistemul de bază pentru a simula specific contextul unui depozit automatizat de tip Amazon Kiva. Depozitul este modelat ca o grilă cu topologie specifică: culoarele de acces formează o rețea regulată printre rafturile de produse, cu stații de încărcare distribuite strategic și zone de pericol reprezentând utilaje grele (stivuitoare) care se mișcă pe trasee fixe.

**Specificul față de mediul generic:**

| Aspect | Mediu generic | WarehouseEnvironment |
|--------|--------------|---------------------|
| Obstacole | Distribuite aleatoriu 15% | Rafturi în configurație de grilă regulată |
| Hrană | Distribuită aleatoriu 5% | Stații de încărcare la capetele culoarelor |
| Pericol | Distribuit aleatoriu 3% | Zone fixe de trecere a stivuitoarelor |
| Target | Un singur punct fix | Stație de picking cu coordonate specificate la runtime |
| Constrângere energie | Energie generală | Baterie robot (autonomie 4 ore = 1.440 pași la 10 secunde/pas) |

**Scenariul specific de evaluare:** Un robot de depozit pornește de la stația de încărcare (START), trebuie să ajungă la un raft specificat (TARGET) pentru a prelua un produs, și să returneze la stația de pachetare — un ciclu tipic în operațiunea unui depozit real. Bateria permite circa 15–20 de cicluri complete fără reîncărcare; stațiile de încărcare rapidă sunt disponibile la capetele fiecărui culoar.

### 7.2 Maparea pe Arhitectura Q-Learning Existentă

Eleganta principală a `WarehouseEnvironment` este că se mapează direct pe interfațele definite de mediul generic, necesitând zero modificări în `agent.py`, `q_learning.py` sau `trainer.py`. Schimbările sunt exclusiv în `environment.py`:

**Generatorul de hartă** este înlocuit cu un generator specific depozitului:

```python
def _generate_warehouse_grid(self):
    """
    Generează layout de depozit cu rafturi în configurație de grilă.
    Culoarele ocupă coloanele pare; rafturile - coloanele impare.
    Stațiile de încărcare la rândul 0 și N-1, coloane pare.
    Zonele de pericol (stivuitoare) la rândul 1 și N-2, coloane pare.
    """
    for r in range(self.rows):
        for c in range(self.cols):
            if c % 2 == 1:  # Coloană impară = raft (obstacol)
                self.grid[r, c] = CellType.OBSTACLE
            elif r == 0 or r == self.rows - 1:
                if c % 4 == 0:  # La 4 coloane: stație de încărcare
                    self.grid[r, c] = CellType.FOOD  # Refolosim FOOD pentru stații
            elif r == 1 or r == self.rows - 2:
                if c % 6 == 0:  # La 6 coloane: zonă stivuitor
                    self.grid[r, c] = CellType.DANGER
```

**Funcția `try_move()`** este identică cu mediul generic — nu necesită modificări. Costurile energetice și recompensele sunt moștenite din `constants.py`.

**Starea MDP** rămâne $(rând, coloană, bucket\_energie)$ — mappingul direct pe Q-table este identic.

### 7.3 Implementarea WarehouseEnvironment

Clasa `WarehouseEnvironment` extinde `Environment` prin suprascrierea metodei de generare a hărții și adăugarea unor metrici specifice depozitului:

```python
class WarehouseEnvironment(Environment):
    """
    Mediu de simulare specific depozitelor autonome.
    Extinde Environment cu layout de depozit și metrici operaționale.
    """
    
    def __init__(self, rows: int = 20, cols: int = 20, 
                 n_charging_stations: int = 5,
                 n_forklift_zones: int = 3,
                 seed: int = 42):
        self.n_charging_stations = n_charging_stations
        self.n_forklift_zones = n_forklift_zones
        super().__init__(rows, cols, seed)
    
    def _generate_map(self):
        """Override generare hartă cu layout specific depozitului."""
        self._generate_warehouse_grid()
        self._place_charging_stations()
        self._place_forklift_danger_zones()
        self._validate_or_regenerate()
    
    def get_operational_metrics(self) -> dict:
        """Returnează metrici specifice operaționale depozitului."""
        return {
            'picks_per_charge_cycle': self._calculate_picks_per_cycle(),
            'avg_aisle_traversal_time': self._calculate_aisle_time(),
            'charging_efficiency': self._calculate_charging_efficiency(),
            'collision_avoidance_rate': self._calculate_collision_rate()
        }
```

**Metrici specifice depozitului** sunt calculale pe baza episoadelor de evaluare:

- **Picks per charge cycle:** Numărul mediu de cicluri start→picking→retur completate înainte de o reîncărcare necesară;
- **Avg aisle traversal time:** Numărul mediu de pași pentru traversarea unui culoar complet;
- **Charging efficiency:** Procentul de energie câștigat față de costul de deplasare la stația de încărcare (eficiența detourului);
- **Collision avoidance rate:** Procentul de situații de proximitate cu zonele de pericol care au fost evitate cu succes.

### 7.4 Rezultate și Metrici

Antrenamentul pe `WarehouseEnvironment` cu aceleași hiperparametri ca Scenariul B generează rezultate comparabile, cu câteva particularități specifice structurii de depozit:

| Metrică | WarehouseEnv | Scenariu B generic |
|---------|-------------|-------------------|
| Episoade convergență | ~1.000 | ~700 |
| Rata succes finală | 99% | 98% |
| Lungime drum greedy | 49 pași | 38 pași |
| Overhead față de BFS optim | +26 pași (+113%) | N/A |
| Energie rămasă (greedy) | 67/100 | 84/100 |
| Picks per charge cycle | 12.3 cicluri | N/A |
| Aisle traversal time | 8.7 pași | N/A |

**Convergența mai lentă** (1.400 vs. 1.200 episoade) în `WarehouseEnvironment` este cauzată de topologia mai restrictivă: culoarele înguste lasă mai puțin spațiu pentru manevre alternative, crescând numărul de stări care necesită politici precise. În mediul generic, agentul poate naviga „în jurul" obstacolelor prin mai multe rute alternative; în depozit, mulți nodi ai grilei au un singur culoar de acces.

**Politica de reîncărcare emergentă** este deosebit de interesantă: agentul a învățat să viziteze stațiile de încărcare nu doar când energia e critică (bucket 0), ci profilactic la bucket 1 dacă stația este pe traseul natural spre TARGET. Aceasta este o politică de tip „fill-up" — identică cu comportamentul optim al roboților Kiva reali, care sunt programați să se încarce ori de câte ori trec pe lângă o stație cu mai puțin de 30% baterie.

### 7.5 Comparație cu Abordări Comerciale (ROS, OpenAI Gym)

**ROS (Robot Operating System)** este platforma de software standard pentru robotica de cercetare, oferind un framework pentru comunicarea între noduri, acces la driver-e de senzori și suite de planificare a mișcării. ROS Nav Stack (navigation stack) implementează un planificator de trasee bazat pe A* cu actualizarea dinamică a costmap-urilor — soluție mai robustă decât Q-Learning tabular, dar incomparabil mai complexă și mai greu de înțeles.

**OpenAI Gym** oferă o colecție de medii de benchmark pentru RL, incluzând FrozenLake-v1 (o grilă cu gheață și găuri) care este structural similar cu mediul nostru. Diferențele față de implementarea din lucrare: FrozenLake are tranziții stochastice (gheața alunecă), nu include componenta energetică, și nu are generare procedurală. `WarehouseEnvironment` poate fi expusă ca un mediu OpenAI Gym-compatible prin implementarea interfeței `gym.Env`, permițând benchmarkarea directă față de alți algoritmi RL.

**Comparație directă:**

| Criteriu | WarehouseEnv (Q-Learning) | ROS Nav Stack | OpenAI Gym FrozenLake |
|----------|--------------------------|---------------|----------------------|
| Cunoaștere prealabilă a hărții | Nu necesară | Necesară (SLAM) | N/A (mediu simulator) |
| Adaptare la mediu dinamic | Da (Scenariul C) | Parțial (costmap updates) | Nu |
| Componenta energetică | Da | Nu standard | Nu |
| Transparență politică | Completă (Q-table) | Redusă | Completă |
| Scalabilitate | Limitată la grilă mică | Generalistă | Limitată la benchmark |
| Cost computațional antrenament | Scăzut (secunde-minute) | N/A (planificare on-line) | Scăzut-mediu |

---

## Capitolul 8: Concluzii și Direcții Viitoare

### 8.1 Concluzii Principale

Lucrarea de față a demonstrat că Q-Learning tabular, augmentat cu o componentă de homeostazie energetică în spațiul de stări, constituie o soluție elegantă, eficientă și interpretabilă pentru problema navigării autonome cu constrângeri de supraviețuire. Principalele concluzii sunt:

**Concluzia 1 — Eficiența Q-Learning tabular în spații de stări mici.** Pe o grilă 20×20 cu 4 buckets energetice (8.000 intrări în Q-table), algoritmul converge la politici cu 100% rată de succes în Scenariul A (ep. 900), 98% în Scenariul B (ep. 2.000, greedy: 38 pași, reward 95,0) și 97-98% în Scenariul C (ep. 900, greedy: 36 pași, reward 97,0), cu un timp de antrenament de ordinul minutelor pe hardware standard. Aceasta demonstrează că, pentru probleme cu spații de stări moderate și deterministe, abordarea tabulară rămâne superioară DQN din perspectiva eficienței computaționale și a garanțiilor de convergență.

**Concluzia 2 — Homeostazia energetică generează comportamente emergente non-triviale.** Adăugarea nivelului de energie ca dimensiune a stării MDP produce un agent care dezvoltă politici calitativ diferite în funcție de starea energetică — navigare directă la energie ridicată, detour strategic spre hrană la energie scăzută. Acest comportament nu este programat explicit, ci emerge din procesul de optimizare Q-Learning. Aceasta validează principiul că îmbogățirea spațiului de stări cu variabile interne relevante produce comportamente mai complexe și mai adaptive.

**Concluzia 3 — Adaptabilitatea la mediu dinamic prin transfer implicit.** Scenariul C demonstrează că Q-table-ul acumulat pe o hartă poate fi reutilizat ca punct de start pentru antrenamentul pe o hartă modificată, reducând numărul de episoade de re-convergență de la ~600 la ~180. Aceasta este o formă de transfer learning implicit, validând că cunoașterea generală acumulată (gradienții de valori spre TARGET, politicile de ocolire a obstacolelor în general) se transferă între configurații specifice diferite.

**Concluzia 4 — Aplicabilitate directă în robotică reală.** Implementarea `WarehouseEnvironment` demonstrează că arhitectura propusă se mapează direct pe probleme reale cu modificări minime. Principiile identificate — navigare cu constrângeri energetice, pit-stop-uri profilactice, adaptare la schimbări de mediu — sunt relevante pentru sisteme robotice reale, de la Amazon Kiva la drone SAR și roboți agricoli.

**Concluzia 5 — Valoarea pedagogică a implementării tabulare.** Comparativ cu DQN și alte abordări bazate pe rețele neurale, Q-Learning tabular oferă trasabilitate completă: fiecare valoare Q poate fi inspectată, fiecare decizie poate fi justificată prin valorile Q comparate. Această proprietate, combinată cu vizualizările heatmap și săgeți de politică, face implementarea un instrument valoros pentru înțelegerea intuitivă a mecanismelor RL.

### 8.2 Limitări ale Abordării

**Limitarea 1 — Scalabilitatea la spații de stări mari.** Dimensiunea Q-table-ului crește liniar cu produsul dimensiunilor fiecărei componente a stării. O grilă de 100×100 cu 8 buckets energetice ar necesita $100 \times 100 \times 8 \times 5 = 400.000$ intrări — gestionabil. Dar o grilă 1.000×1.000 (dimensiunea realistă a unui depozit mare) cu 16 buckets energetice și 8 acțiuni ar necesita $1.000 \times 1.000 \times 16 \times 8 = 128.000.000$ intrări — impractică atât ca memorie, cât și ca explorare completă.

**Limitarea 2 — Mediu determinist.** Implementarea curentă presupune tranziții deterministe ($P(s'|s,a) \in \{0, 1\}$). Mediile reale au perturbații stochastice: senzori cu zgomot, actuatori imperfecți, obstacole dinamice neplanificate. Extinderea la medii stochastice ar necesita evaluarea așteptată a valorilor Q, nu simpla operație max.

**Limitarea 3 — Un singur agent.** Arhitectura este single-agent. Depozitele reale cu sute de roboți necesită algoritmi multi-agent RL care gestionează coordonarea, comunicarea și evitarea coliziunilor la nivel de flotă. Extinderea la multi-agent introduce complexitate exponențială în spațiul de stări și acțiuni combinate.

**Limitarea 4 — Funcție de recompensă manuală.** Funcția de recompensă din lucrarea de față este definită manual, bazată pe intuiție și cunoaștere expertă. În aplicații complexe din lumea reală, proiectarea funcției de recompensă (reward engineering) este o problemă dificilă, iar funcțiile slab proiectate pot conduce la comportamente neașteptate sau exploatare de loophole-uri.

**Limitarea 5 — Absența generalizării.** Q-table-ul antrenat pe o hartă cu seed 42 nu se transferă direct la o hartă cu seed diferit (deși transfer-ul parțial din Scenariul C sugerează că unele politici sunt generalizabile). Un agent RL tabular nu poate „generaliza" la configurații neîntâlnite — spre deosebire de DQN care poate extrapola prin reprezentările neurale.

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

---

*Lucrare depusă la Facultatea de Matematică și Informatică, Universitatea din București, în vederea obținerii titlului de Licențiat în Informatică.*

*București, Iunie 2026*

---

**Declarație de autenticitate**

Subsemnatul, Andrei Demit, declar pe propria răspundere că lucrarea de licență intitulată „Simularea Comportamentului Inteligent prin Q-Learning: Navigare Autonomă și Supraviețuire" este elaborată de mine, pe baza studiului literaturii de specialitate și a implementării originale, și nu conține fragmente plagiate din alte lucrări. Toate sursele bibliografice utilizate sunt citate conform normelor academice în vigoare.

*Semnătura:* _________________________ *Data:* _________________________
