# Snake Game with Human and Q-Learning AI Modes

This project contains a complete grid-based Snake game in two versions:

- A browser website built with HTML, CSS, and JavaScript
- A Python desktop version built with pygame and numpy

## Files

- `index.html` - website entry point
- `style.css` - website layout and button styling
- `app.js` - browser Snake game and Q-learning logic
- `main.py` - menu, mode selection, and program entry point
- `game.py` - snake game logic, rendering, collision detection, scoring
- `agent.py` - Q-learning agent, Q-table, epsilon-greedy policy, save/load

## Run the Website

Open `index.html` in your browser.

The website includes:

- Human Mode button
- AI Mode button
- Restart button
- Speed slider
- On-screen direction buttons
- Score, best score, episode, epsilon, and Q-state display

The browser AI saves its Q-table in `localStorage`.

## Run the Python Version

Install the required packages:


```bash
pip install pygame numpy
```

Start the game:

```bash
python main.py
```

If `python` is not available on your PATH on Windows, try:

```bash
py main.py
```

At the menu:

- Press `1` for Human Mode
- Press `2` for AI Mode
- Press `Esc` to quit

## Human Mode

Use the arrow keys to control the snake. The game ends when the snake hits a wall or itself.

## AI Mode

The snake plays automatically using Q-learning.

The console prints:

- Episode number
- Current score
- Best score
- Current epsilon value

The Q-table is saved to `q_table.pkl` during training and loaded automatically on the next run.

You can adjust AI training settings in `main.py`:

- `EPISODES`
- `AI_SPEED`
- `HUMAN_SPEED`
