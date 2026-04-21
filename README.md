# Projet_2026_Kamisado
Projet_Kamisado/
│
├── main.py
│
├── server/
│   ├── client.py        # connexion, réception, envoi
│   └── protocol.py      # messages JSON
│
├── game/
│   ├── state.py         # parse l'état JSON
│   └── moves.py         # génère les coups possibles
│
├── ai/
│   ├── heuristics.py    # fonctions d'évaluation
│   └── strategy.py      # compute_move()
│
└── tests/
    ├── test_moves.py
    ├── test_ai.py
    └── test_server.py
