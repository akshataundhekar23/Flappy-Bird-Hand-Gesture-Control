# Hand-Controlled Flappy Bird

A fun variation of the classic Flappy Bird game that uses hand gestures for control through your webcam!

## Requirements
- Python 3.7+
- Webcam

## Installation

1. Install the required packages:
```bash
pip install -r requirements.txt
```

## How to Play

1. Run the game:
```bash
python flappy_bird.py
```

2. Game Controls:
   - Raise your index finger above your palm to make the bird flap
   - Alternatively, press SPACE to flap
   - Press 'Q' to quit the game

3. Game Rules:
   - Navigate the bird through the pipes
   - Each successful pipe passage earns you 1 point
   - Don't hit the pipes or the screen boundaries!

## Features
- Real-time hand gesture detection using MediaPipe
- Classic Flappy Bird gameplay mechanics
- Score tracking
- Visual feedback of hand tracking
