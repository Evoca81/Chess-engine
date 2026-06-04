# Chess

A chess game built with Python and Pygame, featuring a minimax AI opponent.

## Features

- Full chess rule implementation: castling, en passant, pawn promotion (auto-queen)
- Draw detection: threefold repetition and 50-move rule
- Checkmate and stalemate detection
- Move highlighting for selected pieces
- Animated piece movement
- Undo moves with `Z` and reset the board with `R`
- AI opponent using minimax search (depth 2) with material evaluation

## Requirements

- Python 3
- Pygame

## How to Run

```
pip install pygame
python ChessMain.py
```

## Controls

| Key / Action | Effect |
|---|---|
| Click | Select and move pieces |
| `Z` | Undo last move |
| `R` | Reset the board |

## Configuration

In `ChessMain.py`, set the player flags to control who plays each side:

```python
playerOne = True   # True = human plays White, False = AI plays White
PlayerTwo = False   # True = human plays Black, False = AI plays Black
```

## Project Structure

| File | Description |
|---|---|
| `ChessMain.py` | Game loop, rendering, and input handling |
| `ChessEngine.py` | Board state, move generation, and rule enforcement |
| `ChessAI.py` | AI move selection (random fallback + minimax) |
| `Pictures/` | Piece sprite images |
