import type { ExperimentProfileId, SafeNavigationConfig } from './types';

export type ExperimentProfile = {
  id: ExperimentProfileId;
  label: string;
  shortLabel: string;
  description: string;
  assumption: string;
  expectedTakeaway: string;
  favoredAlgorithms: string[];
  protocol: string;
  recommended: Partial<SafeNavigationConfig>;
  monteCarlo: {
    number_of_maps: number;
    episodes_per_map: number;
  };
};

export const experimentProfiles: ExperimentProfile[] = [
  {
    id: 'known_static',
    label: 'Hartă cunoscută, mediu static',
    shortLabel: 'Static',
    description: 'Testează cazul ideal pentru planificare: harta și costurile sunt cunoscute, iar acțiunile sunt deterministe.',
    assumption: 'Agentul are model complet al mediului înainte de decizie.',
    expectedTakeaway: 'A* este alegerea naturală când vrem eficiență pe o hartă cunoscută și statică.',
    favoredAlgorithms: ['astar', 'risk_aware_astar'],
    protocol: 'Evaluare clasică Monte Carlo: fiecare hartă este cunoscută integral agentului în momentul planificării.',
    recommended: {
      scenario: 'medium',
      movement_noise: 0,
      risk_weight: 1,
      training_episodes: 150,
      max_steps: 300,
    },
    monteCarlo: { number_of_maps: 6, episodes_per_map: 2 },
  },
  {
    id: 'high_risk',
    label: 'Risc ridicat',
    shortLabel: 'Risc',
    description: 'Crește penalizarea riscului pentru a arăta de ce drumul cel mai scurt nu este mereu drumul potrivit.',
    assumption: 'Siguranța este mai importantă decât minimizarea strictă a numărului de pași.',
    expectedTakeaway: 'A* conștient de risc devine preferabil când expunerea la pericol contează explicit.',
    favoredAlgorithms: ['risk_aware_astar'],
    protocol: 'Evaluare Monte Carlo cu cost de risc mai mare; tabelul trebuie citit prin succes și expunere, nu doar pași.',
    recommended: {
      scenario: 'hard',
      danger_probability: 0.18,
      movement_noise: 0,
      risk_weight: 3,
      training_episodes: 200,
      max_steps: 380,
    },
    monteCarlo: { number_of_maps: 6, episodes_per_map: 2 },
  },
  {
    id: 'stochastic_execution',
    label: 'Execuție incertă',
    shortLabel: 'Zgomot',
    description: 'Adaugă zgomot de mișcare pentru a testa ce se întâmplă când acțiunea cerută nu este mereu cea executată.',
    assumption: 'Planul poate fi corect, dar actuatorul sau mediul pot devia execuția.',
    expectedTakeaway: 'Robustețea se citește din coliziuni, timeout și risc acumulat, nu doar din lungimea planului.',
    favoredAlgorithms: ['risk_aware_astar', 'feature_q'],
    protocol: 'Evaluare Monte Carlo cu tranziții stocastice; agentul observă rezultatul fiecărui pas, dar nu controlează perfect execuția.',
    recommended: {
      scenario: 'medium',
      movement_noise: 0.2,
      risk_weight: 2,
      training_episodes: 300,
      max_steps: 420,
    },
    monteCarlo: { number_of_maps: 6, episodes_per_map: 3 },
  },
  {
    id: 'same_map_learning',
    label: 'Învățare pe aceeași hartă',
    shortLabel: 'Învățare',
    description: 'Antrenează agenții Q pe aceeași hartă pe care sunt evaluați, ca să fie vizibilă memorarea prin experiență.',
    assumption: 'Agentul poate repeta același mediu de multe ori înainte de rularea demonstrativă.',
    expectedTakeaway: 'Q-learning tabular are sens când mediul se repetă și coordonatele învățate rămân relevante.',
    favoredAlgorithms: ['tabular_q', 'feature_q'],
    protocol: 'Pentru agenții cu învățare: training pe seed-ul hărții evaluate, apoi evaluare greedy pe aceeași hartă.',
    recommended: {
      scenario: 'easy',
      movement_noise: 0,
      risk_weight: 1,
      training_episodes: 900,
      max_steps: 260,
    },
    monteCarlo: { number_of_maps: 3, episodes_per_map: 2 },
  },
  {
    id: 'transfer_learning',
    label: 'Transfer pe hărți noi',
    shortLabel: 'Transfer',
    description: 'Separă hărțile de antrenare de hărțile de evaluare pentru a evidenția generalizarea.',
    assumption: 'Agentul învață tipare într-un set de medii, apoi este testat pe seed-uri nevăzute.',
    expectedTakeaway: 'Q-learning pe trăsături transferă mai natural decât Q-learning tabular, care memorează coordonate absolute.',
    favoredAlgorithms: ['feature_q'],
    protocol: 'Agenții learning se antrenează pe seed-uri dedicate și sunt evaluați pe alte seed-uri; A* rămâne baseline cu hartă cunoscută.',
    recommended: {
      scenario: 'medium',
      movement_noise: 0.05,
      risk_weight: 1.5,
      training_episodes: 700,
      max_steps: 360,
    },
    monteCarlo: { number_of_maps: 6, episodes_per_map: 2 },
  },
  {
    id: 'training_cost',
    label: 'Cost training vs decizie',
    shortLabel: 'Cost',
    description: 'Pune accent pe faptul că planning-ul plătește cost la fiecare hartă, iar learning-ul plătește cost înainte de evaluare.',
    assumption: 'Comparația trebuie să distingă timpul de antrenare de timpul de decizie în episod.',
    expectedTakeaway: 'A* este puternic fără training, iar learning-ul devine interesant când politica este reutilizată.',
    favoredAlgorithms: ['astar', 'risk_aware_astar', 'feature_q'],
    protocol: 'Evaluare Monte Carlo standard, dar dashboard-ul explică separat costul de training și timpul de execuție raportat.',
    recommended: {
      scenario: 'medium',
      movement_noise: 0,
      risk_weight: 1,
      training_episodes: 600,
      max_steps: 320,
    },
    monteCarlo: { number_of_maps: 5, episodes_per_map: 2 },
  },
];

export const algorithmUseCases: Record<string, string> = {
  random: 'Baseline minim: îl folosim doar ca reper pentru dificultatea mediului.',
  rule_based: 'Bun pentru demo-uri simple și reguli locale explicabile, dar fragil la ocoluri lungi.',
  astar: 'Cea mai bună alegere când harta este cunoscută, costurile sunt clare și mediul este static.',
  risk_aware_astar: 'Potrivit când harta este cunoscută, dar siguranța și expunerea la risc sunt obiective explicite.',
  tabular_q: 'Potrivit când agentul repetă aceeași hartă și poate învăța coordonate utile prin multe episoade.',
  feature_q: 'Potrivit când vrem transfer de tipare locale pe hărți noi sau condiții ușor variabile.',
};

export function getExperimentProfile(id: string | undefined) {
  return experimentProfiles.find((profile) => profile.id === id) ?? experimentProfiles[0];
}

export function applyExperimentProfile(config: SafeNavigationConfig, id: ExperimentProfileId): SafeNavigationConfig {
  const profile = getExperimentProfile(id);
  return {
    ...config,
    ...profile.recommended,
    experiment_profile: id,
  };
}
