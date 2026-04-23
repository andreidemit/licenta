"""
Constante globale pentru simularea Q-Learning.
"""

# --- Dimensiuni Grid ---
GRID_ROWS = 20
GRID_COLS = 20

# --- Dimensiuni Fereastră ---
CELL_SIZE = 32          # pixeli per celulă
SIDEBAR_WIDTH = 250     # lățime panel lateral
WINDOW_WIDTH = GRID_COLS * CELL_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = GRID_ROWS * CELL_SIZE
FPS = 60

# --- Energie ---
ENERGY_MAX = 100
ENERGY_COST_NORMAL = 1    # cost per pas pe teren normal
ENERGY_COST_MUD = 3       # cost per pas pe teren dificil
ENERGY_GAIN_FOOD = 20     # energie câștigată la colectare hrană
ENERGY_STAY_COST = 0      # cost pentru acțiunea STAY

# Praguri discretizare energie (procente din E_max)
ENERGY_THRESHOLDS = [0.25, 0.50, 0.75]  # → 4 nivele: 0=critic, 1=scăzut, 2=mediu, 3=înalt

# --- Recompense ---
REWARD_STEP = -1          # penalizare existențială per pas
REWARD_FOOD = 15          # recompensă colectare hrană
REWARD_COLLISION = -5     # penalizare lovire obstacol/perete
REWARD_TARGET = 100       # recompensă ajungere la țintă
REWARD_DEATH = -100       # penalizare moarte (energie 0 sau capcană)
REWARD_MUD = -2           # penalizare adițională teren dificil

# --- Hiperparametri Q-Learning ---
ALPHA = 0.1               # rata de învățare
GAMMA = 0.95              # factor de discount
EPSILON_START = 1.0       # explorare inițială (100%)
EPSILON_MIN = 0.01        # explorare minimă
EPSILON_DECAY = 0.995     # factor de decădere epsilon per episod

# --- Antrenament ---
MAX_STEPS_PER_EPISODE = 500   # limită pași per episod (anti-loop)
DEFAULT_EPISODES = 2000       # număr default de episoade de antrenament

# --- Generare Procedurală ---
OBSTACLE_DENSITY = 0.15       # 15% din celule = obstacole
MUD_DENSITY = 0.08            # 8% din celule = zone dificile
FOOD_DENSITY = 0.05           # 5% din celule = resurse
DANGER_DENSITY = 0.03         # 3% din celule = pericole
MIN_MANHATTAN_DISTANCE = 10   # distanța minimă Manhattan între start și țintă

# --- Culori (RGB) ---
COLOR_EMPTY = (144, 238, 144)      # verde deschis - iarbă
COLOR_OBSTACLE = (100, 100, 100)   # gri - zid
COLOR_MUD = (139, 119, 101)        # maro - noroi
COLOR_FOOD = (255, 215, 0)         # galben-auriu - hrană
COLOR_DANGER = (220, 20, 60)       # roșu - pericol
COLOR_TARGET = (0, 191, 255)       # albastru deschis - țintă
COLOR_AGENT = (255, 255, 255)      # alb - agent
COLOR_START = (50, 205, 50)        # verde intens - start

COLOR_BACKGROUND = (30, 30, 30)    # fundal sidebar
COLOR_GRID_LINE = (60, 60, 60)     # linii grid
COLOR_TEXT = (220, 220, 220)       # text sidebar
COLOR_ENERGY_BAR = (50, 205, 50)   # bară energie (verde)
COLOR_ENERGY_LOW = (255, 69, 0)    # bară energie scăzută (roșu)

# --- Scenariul C — Mediu Dinamic ---
SCENARIO_C_SWITCH_EPISODE = 500          # după câte episoade se relocă obstacolele
SCENARIO_C_OBSTACLE_RELOCATE_FRACTION = 0.3  # fracțiunea de obstacole mutate
ALPHA_SENSITIVITY_VALUES = [0.05, 0.1, 0.2]  # valori alpha pentru analiza de sensibilitate

# --- Acțiuni ---
ACTIONS = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT",
    4: "STAY",
}
NUM_ACTIONS = len(ACTIONS)

# Direcții de mișcare corespunzătoare acțiunilor (dy, dx)
# UP = rând-1, DOWN = rând+1, LEFT = col-1, RIGHT = col+1, STAY = 0,0
ACTION_DELTAS = {
    0: (-1, 0),   # UP
    1: (1, 0),    # DOWN
    2: (0, -1),   # LEFT
    3: (0, 1),    # RIGHT
    4: (0, 0),    # STAY
}
