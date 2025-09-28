# Leaf Catcher

## Overview
Leaf Catcher is a fun and interactive game built using Python's Tkinter library. The objective of the game is to catch falling leaves using a basket. Players can move the basket left and right to collect as many leaves as possible while avoiding obstacles.

## Features
- Catch falling leaves to score points.
- Simple and intuitive controls.
- Colorful graphics and engaging sound effects.
- Scoring system to track player performance.

## Project Structure
```
leaf-catcher
├── src
│   ├── app.py
│   ├── controllers
│   │   ├── __init__.py
│   │   └── game_controller.py
│   ├── models
│   │   ├── __init__.py
│   │   └── game_state.py
│   ├── views
│   │   ├── __init__.py
│   │   └── game_view.py
│   └── utils
│       ├── __init__.py
│       └── constants.py
├── assets
│   ├── images
│   ├── sounds
│   └── fonts
├── tests
│   └── test_app.py
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/leaf-catcher.git
   ```
2. Navigate to the project directory:
   ```
   cd leaf-catcher
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To start the game, run the following command:
```
python src/app.py
```

## Gameplay
- Use the left and right arrow keys to move the basket.
- Catch the falling leaves to increase your score.
- Avoid missing leaves to maintain your score.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.