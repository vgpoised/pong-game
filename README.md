# pong-game

A classic Pong game built in Python where you play against the computer.
The first player to score **7 goals** wins!

## Requirements

- Python 3.6+
- [pygame](https://www.pygame.org/) 2.x

Install the dependency with:

```bash
pip install pygame
```

## How to Play

```bash
python pong.py
```

| Key | Action |
|-----|--------|
| ↑ / W | Move paddle up |
| ↓ / S | Move paddle down |
| ESC | Quit the game |
| SPACE | Restart after a win screen |

## Rules

- You control the **cyan** paddle on the left.
- The **computer** controls the red paddle on the right.
- Score a point each time the ball passes your opponent's paddle.
- The first side to reach **7 points** wins the match.
- After the win screen appears, press **SPACE** to play again or **ESC** to quit.
