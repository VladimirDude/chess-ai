# Custom Chess Engine

A high-performance chess engine developed from scratch..

---

## Technical Stack & Systems Used

* **Language:** Python 3.10+
* **Board Representation & Move Generation:** `python-chess` library managing legal move validation, FEN parsing, and board state transitions.
* **Search Algorithm:** Minimax search tree paired with Alpha-Beta pruning to eliminate redundant branches.
* **Evaluation Framework:** 
  * Tapered Phase Interpolation for smooth shifting between Opening/Middlegame and Endgame piece values.
  * Custom Piece-Square Tables (PSTs) for positional bonuses across all piece types.
* **Benchmarking & Testing Suite:** Custom multi-threaded Python gauntlet script utilizing concurrent execution to pit the engine directly against scaled Stockfish instances.

---

## Performance & Benchmarks

Automated gauntlet testing against Stockfish instances with concurrency enabled:

| Target Opponent | Sample Size | Record (W-D-L) | Win Rate | Estimated Elo |
| :--- | :---: | :---: | :---: | :---: |
| **Stockfish @ 1400** | 12 games | 11-1-0 | 95.8% | ~1945 |
| **Stockfish @ 1600** | 21 games | 13-2-6 | 66.7% | ~1776 |

---
