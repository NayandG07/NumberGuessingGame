# Number Guessing Game

A feature-rich number guessing game built with Python and Tkinter, offering multiple game modes, themes, and player progression.

## Features

### Game Modes
- **Classic Mode**: Standard number guessing game with 7 attempts
- **Sudden Death**: One attempt to guess correctly
- **Survival Mode**: Score accumulates across rounds
- **Time Attack**: Guess under time pressure with a 60-second limit

### Player Features
- Customizable player profiles with avatars
- Achievement system
- High score tracking
- Player statistics tracking
- Multiple difficulty levels

### Game Features
- Dynamic hints system
- Progress tracking
- Timer functionality
- Sound effects and music
- Multiple themes (Light/Dark mode)
- Responsive UI

## Requirements

- Python 3.x
- Tkinter (usually comes with Python)
- Required Python packages:
  - random
  - time
  - json
  - datetime
  - os
  - sys
  - traceback

## Installation

1. Clone or download this repository
2. Ensure you have Python 3.x installed
3. Run the game:
   ```bash
   python Final_fixed_game.py
   ```

## How to Play

1. Launch the game
2. Choose your game mode
3. Select difficulty level
4. Try to guess the secret number within the given attempts
5. Use hints if needed
6. Track your progress and achievements

## Game Structure

The game creates two main directories:
- `data/`: Stores game data, high scores, and player profiles
- `avatars/`: Stores player avatar images

## Features in Detail

### Achievements
- First Win
- Winning Streak (3 games in a row)
- Perfect Game (win with first guess)
- Speed Demon (win under 30 seconds)
- Master Guesser (play 10 games)

### Statistics Tracking
- Accuracy
- Average guess time
- Total guesses
- Correct guesses
- Games played
- Total score
- Best time

### UI Features
- Progress bar
- Status indicators
- Theme customization
- Responsive layout
- Achievement notifications

## Contributing

Feel free to fork this repository and submit pull requests for any improvements.

## License

This project is open source and available under the MIT License. 