# Plan: Simulare Q-Learning — Navigare Autonomă (Licență)

## TL;DR
Implementare incrementală a unei simulări Q-Learning în Python/Pygame pentru navigare și supraviețuire autonomă, cu GUI interactiv, export CSV și grafice de convergență. Fiecare pas produce un livrabil testabil. Paralel, un plan de redactare a capitolelor lucrării de licență sincronizat cu progresul implementării.

**Tehnologii:** Python 3.11+, Pygame, NumPy, Matplotlib, CSV (standard lib)
**Grid default:** 20×20 | **Structură:** Modulară | **Deadline:** Iunie 2026

---

## FAZA I — Fundația (Pași 1–3)

### Pas 1: Scheletul proiectului + Mediul static ✅
**Livrabil:** Grid 20×20 randat în Pygame cu celule colorate (vid, obstacol). Agentul apare pe hartă.

- Creează structura de fișiere:
  ```
  licenta/
  ├── src/
  │   ├── __init__.py
  │   ├── environment.py    # Grid, generare, tipuri celule
  │   ├── agent.py           # Clasa Agent (poziție, energie)
  │   ├── constants.py       # Dimensiuni, culori, recompense
  │   ├── renderer.py        # Pygame rendering
  │   └── main.py            # Entry point
  ├── tests/
  │   └── test_environment.py
  ├── data/                  # CSV exports, Q-tables salvate
  ├── readme.md
  └── requirements.txt
  ```
- Environment: matrice NxM, tipuri celule (enum), plasare start + țintă
- Renderer: Pygame window, grid drawing, culori per tip celulă
- **Test:** Rulează `main.py` → vezi grid colorat cu agent și țintă

### Pas 2: Generare procedurală + Validare topologică ✅
**Livrabil:** Hărți generate aleatoriu cu seed, validate prin BFS (drum garantat Start→Țintă).

- Generator cu seed numeric, densitate obstacole ρ configurabilă
- Plasare aleatorie agent + țintă cu distanță minimă Manhattan
- BFS/Flood Fill pentru validare drum existent
- Adaugă zone dificile (Mud) și resurse (Food) pe hartă
- **Test:** Generează 100 hărți cu seed-uri diferite → 100% au drum valid. Unit tests pentru BFS.

### Pas 3: Mișcarea agentului (manual) + Sistemul de energie ✅
**Livrabil:** Agentul se mișcă cu tastele săgeți, energia scade, se poate colecta hrană.

- Implementare acțiuni: UP, DOWN, LEFT, RIGHT, STAY
- Coliziuni cu pereți și obstacole
- Sistem energie: E_max, consum per pas, consum dublu pe mud, +20 la hrană
- Afișare energie ca bară laterală în GUI
- Condiții terminale: E≤0 (moarte), ajunge la țintă (victorie)
- **Test:** Joacă manual, verifică că energia scade corect, coliziunile funcționează, resursa dispare la colectare

---

## FAZA II — Q-Learning Core (Pași 4–6)

### Pas 4: Implementare Q-Learning basic ✅
**Livrabil:** Agentul învață singur să navigheze pe o hartă mică (10×10) fără obstacole.

- Q-Table: dict sau numpy array, cheia = (x, y, E_discret), 5 acțiuni
- Epsilon-Greedy: explorare vs exploatare
- Ecuația Bellman: Q(S,A) ← Q(S,A) + α[R + γ·max Q(S',a') - Q(S,A)]
- Hiperparametri în constants.py: α=0.1, γ=0.95, ε_start=1.0, ε_min=0.01, ε_decay=0.995
- Bucla de antrenament: multiple episoade, fără rendering (fast mode)
- **Test:** Pe hartă 10×10 goală → agentul converge la drum optim în <500 episoade. Verifică Q-values crescătoare spre țintă.

### Pas 5: Sistem de recompense complet + Antrenament 20×20
**Livrabil:** Agentul se antrenează pe grile 20×20 cu obstacole, energie limitată, resurse.

- Reward shaping complet: -1/pas, +15 hrană, -5 coliziune, +100 țintă, -100 moarte
- Discretizare energie (4 nivele) integrată în stare
- Max steps per episod (anti-loop infinit)
- Antrenament pe Scenariul A (navigare pură, energie infinită) → convergență
- **Test:** Scenariul A converge: rolling average reward crește monoton pe ultimele 200 episoade

### Pas 6: Vizualizare Q-Values + Săgeți de politică
**Livrabil:** GUI arată Q-value heatmap și săgeți de direcție per celulă.

- Heatmap: colorare celulă după max Q-value (roșu = pericol, verde = bun)
- Săgeți: argmax Q(s, a) per celulă → direcția preferată
- Toggle între vizualizări (hartă normală / heatmap / politică)
- Replay: rulează un episod cu politica învățată, vizualizat pas cu pas
- **Test:** După antrenament, săgețile indică drumul logic spre țintă, ocolind obstacole

---

## FAZA III — Scenarii + Analytics (Pași 7–9)

### Pas 7: Scenariul B — Dilema Supraviețuitorului
**Livrabil:** Agentul învață să facă detour pentru hrană când energia e insuficientă.

- Configurare scenariu: energie limitată strict, hrană plasată lateral
- Drumul direct imposibil fără reîncărcare
- Antrenament + validare convergență
- Comparare politică cu/fără E_discret în stare (ablation study)
- **Test:** Agentul supraviețuiește >80% din episoade post-antrenament, face pit-stop la resurse

### Pas 8: Export CSV + Grafice de convergență (Matplotlib)
**Livrabil:** Fișiere CSV cu metrici per episod + grafice rolling average reward.

- Logger: salvează per episod — ID, steps, total_reward, epsilon, outcome, coverage%
- Export CSV în data/
- Grafice Matplotlib: reward curve, epsilon decay, steps per episode, success rate
- Salvare grafice ca PNG
- **Test:** CSV valid, graficele arată trend ascendent clar pentru scenariile A și B

### Pas 9: Scenariul C — Adaptabilitate + Salvare/Încărcare Q-Table
**Livrabil:** Testare adaptabilitate la schimbări de mediu + persistență Q-Table.

- Salvare Q-Table (pickle sau JSON) după antrenament
- Încărcare Q-Table salvată pentru continuare antrenament
- Scenariul C: antrenament N episoade → modificare hartă → continuare antrenament
- Măsurare "timp de readaptare" (episoade până la re-convergență)
- Variație α pentru testare plasticitate
- **Test:** Agentul se readaptează la noua configurație. Grafic comparativ: α=0.1 vs α=0.3 vs α=0.5

---

## FAZA IV — Polish + Livrare (Pas 10)

### Pas 10: GUI complet + Integrare finală
**Livrabil:** Aplicație completă, polished, cu toate funcționalitățile.

- Panel lateral: butoane Start/Pause/Reset, selector scenariu, slider viteză
- Afișaj metrici live: episod curent, reward, epsilon, energie
- Mod antrenament rapid (fără render) + mod vizualizare (cu render)
- Comutare între scenarii din GUI
- README actualizat cu instrucțiuni de rulare
- **Test:** Demo complet: alege scenariu → antrenare → vizualizare politică → export date

---

## PLAN REDACTARE CAPITOLE LICENȚĂ

Capitolele se scriu **paralel** cu implementarea — nu la final.

| Capitol | Conținut | Se scrie după Pasul | Pagini est. |
|---------|---------|---------------------|-------------|
| **1. Introducere** | Motivație, obiective, structura lucrării | Pas 1 | 3-4 |
| **2. Fundamente Teoretice** | RL, MDP, Q-Learning, epsilon-greedy, Bellman | Pas 4 | 10-12 |
| **3. Tehnologii Utilizate** | Python, Pygame, NumPy, Matplotlib, arhitectura | Pas 3 | 4-5 |
| **4. Modelarea Mediului** | Grid, generare procedurală, ontologie, validare BFS | Pas 2 | 6-8 |
| **5. Modelarea Agentului** | Stare, Q-Table, sistem senzorial, recompense | Pas 5 | 8-10 |
| **6. Implementare** | Arhitectura cod, bucla principală, detalii tehnice | Pas 6 | 10-12 |
| **7. Rezultate Experimentale** | Scenariile A, B, C — grafice, tabele, analiză | Pas 9 | 12-15 |
| **8. Concluzii** | Sumar, limitări, direcții viitoare | Pas 10 | 3-4 |
| **Anexe** | Cod sursă relevant, tabele complete | Pas 10 | 5-10 |

**Total estimat:** 60-80 pagini

### Cronologie recomandată (Martie–Iunie 2026)

| Perioadă | Implementare | Scriere |
|----------|-------------|---------|
| Săpt. 1–2 (Mar 26 – Apr 8) | Pași 1–3 (Fundația) | Cap. 1 (Introducere) |
| Săpt. 3–4 (Apr 9 – Apr 22) | Pași 4–5 (Q-Learning core) | Cap. 2 (Fundamente Teoretice) |
| Săpt. 5–6 (Apr 23 – Mai 6) | Pas 6 (Vizualizare) | Cap. 3 + 4 (Tehnologii + Mediu) |
| Săpt. 7–8 (Mai 7 – Mai 20) | Pași 7–8 (Scenarii + CSV) | Cap. 5 + 6 (Agent + Implementare) |
| Săpt. 9–10 (Mai 21 – Iun 3) | Pași 9–10 (Adaptabilitate + Polish) | Cap. 7 (Rezultate) |
| Săpt. 11–12 (Iun 4 – Iun 17) | Bugfix + demo final | Cap. 8 + Anexe + Revizie finală |

---

## Fișiere relevante
- `src/environment.py` — Grid, generare procedurală, BFS validare, tipuri celule
- `src/agent.py` — Q-Table, epsilon-greedy, Bellman update, stare (x, y, E_discret)
- `src/constants.py` — Hiperparametri (α, γ, ε), dimensiuni, recompense, culori
- `src/renderer.py` — Pygame rendering, heatmap, săgeți politică, panel metrici
- `src/main.py` — Bucla principală, orchestrare antrenament/vizualizare
- `src/logger.py` — Export CSV, metrici per episod
- `src/plotter.py` — Grafice Matplotlib (convergență, epsilon decay)
- `tests/test_environment.py` — Unit tests generare, validare, coliziuni
- `tests/test_agent.py` — Unit tests Q-update, selecție acțiune, energie

## Decizii
- Q-Learning tabular (nu DQN) — conform specificația proiectului
- Grid 20×20 default, configurabil
- Structură modulară din start
- Structură capitole liberă, propusă mai sus
- Deadline: Iunie 2026

## Considerații suplimentare
1. **Persistență Q-Table:** Pickle (simplu, rapid) vs JSON (human-readable, mai mare). Recomand pickle cu opțiune de export JSON pentru debugare.
2. **Testare automată:** pytest pentru unit tests + manual testing pentru GUI. Recomand pytest minimal pentru logica critică (generare hartă, Q-update).
3. **Grafice în lucrare:** Matplotlib exportă PNG/SVG direct. SVG recomandat pentru calitate tipărire.
