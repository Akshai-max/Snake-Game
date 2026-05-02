const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");

const scoreEl = document.getElementById("score");
const bestScoreEl = document.getElementById("bestScore");
const episodeEl = document.getElementById("episode");
const modeLabelEl = document.getElementById("modeLabel");
const messageEl = document.getElementById("message");
const speedRange = document.getElementById("speedRange");
const speedText = document.getElementById("speedText");
const epsilonEl = document.getElementById("epsilon");
const statesEl = document.getElementById("states");
const logEl = document.getElementById("log");

const humanBtn = document.getElementById("humanBtn");
const aiBtn = document.getElementById("aiBtn");
const restartBtn = document.getElementById("restartBtn");
const saveBtn = document.getElementById("saveBtn");
const clearBtn = document.getElementById("clearBtn");

const block = 20;
const cols = canvas.width / block;
const rows = canvas.height / block;
const directions = ["RIGHT", "DOWN", "LEFT", "UP"];

let snake;
let food;
let direction;
let nextDirection;
let score;
let bestScore = Number(localStorage.getItem("snake_best_score") || 0);
let episode = 0;
let mode = "menu";
let timer = null;
let frameCount = 0;

let qTable = loadQTable();
let epsilon = 1;
const epsilonMin = 0.02;
const epsilonDecay = 0.995;
const alpha = 0.1;
const gamma = 0.9;

function resetGame() {
  const x = Math.floor(cols / 2) * block;
  const y = Math.floor(rows / 2) * block;
  direction = "RIGHT";
  nextDirection = "RIGHT";
  snake = [
    { x, y },
    { x: x - block, y },
    { x: x - 2 * block, y },
  ];
  score = 0;
  frameCount = 0;
  placeFood();
  updateStats();
  draw();
}

function placeFood() {
  do {
    food = {
      x: Math.floor(Math.random() * cols) * block,
      y: Math.floor(Math.random() * rows) * block,
    };
  } while (snake.some((part) => samePoint(part, food)));
}

function samePoint(a, b) {
  return a.x === b.x && a.y === b.y;
}

function startHuman() {
  mode = "human";
  episode = 0;
  resetGame();
  setActiveButton(humanBtn);
  modeLabelEl.textContent = "Human Mode";
  messageEl.textContent = "Use arrow keys or the on-screen direction buttons.";
  startLoop();
}

function startAi() {
  mode = "ai";
  episode = 1;
  resetGame();
  setActiveButton(aiBtn);
  modeLabelEl.textContent = "AI Mode";
  messageEl.textContent = "Q-learning is running automatically.";
  startLoop();
}

function startLoop() {
  stopLoop();
  timer = setInterval(tick, 1000 / Number(speedRange.value));
}

function stopLoop() {
  if (timer) {
    clearInterval(timer);
    timer = null;
  }
}

function tick() {
  if (mode === "human") {
    stepHuman();
  } else if (mode === "ai") {
    stepAi();
  }
}

function stepHuman() {
  direction = nextDirection;
  const result = moveSnake();
  if (result.done) {
    stopLoop();
    messageEl.textContent = `Game over. Final score: ${score}. Press Restart or choose a mode.`;
  }
  updateStats();
  draw();
}

function stepAi() {
  const state = getState();
  const action = getAction(state);
  turn(action);
  const result = moveSnake();
  const nextState = getState();
  trainStep(state, action, result.reward, nextState, result.done);

  if (result.done) {
    bestScore = Math.max(bestScore, score);
    localStorage.setItem("snake_best_score", String(bestScore));
    addLog(`Episode ${episode} | Score ${score} | Best ${bestScore} | Epsilon ${epsilon.toFixed(3)}`);
    console.log(`Episode: ${episode} | Score: ${score} | Best: ${bestScore} | Epsilon: ${epsilon.toFixed(3)}`);
    epsilon = Math.max(epsilonMin, epsilon * epsilonDecay);
    episode += 1;
    resetGame();
  }

  updateStats();
  draw();
}

function moveSnake() {
  frameCount += 1;
  const head = { ...snake[0] };

  if (direction === "RIGHT") head.x += block;
  if (direction === "LEFT") head.x -= block;
  if (direction === "DOWN") head.y += block;
  if (direction === "UP") head.y -= block;

  snake.unshift(head);

  let reward = -0.1;
  let done = false;

  if (isCollision(head) || frameCount > 100 * snake.length) {
    done = true;
    reward = -10;
    return { reward, done };
  }

  if (samePoint(head, food)) {
    score += 1;
    bestScore = Math.max(bestScore, score);
    localStorage.setItem("snake_best_score", String(bestScore));
    reward = 10;
    placeFood();
  } else {
    snake.pop();
  }

  return { reward, done };
}

function isCollision(point) {
  if (point.x < 0 || point.x >= canvas.width || point.y < 0 || point.y >= canvas.height) {
    return true;
  }
  return snake.slice(1).some((part) => samePoint(part, point));
}

function setDirection(newDirection) {
  if (mode !== "human") return;
  if (newDirection === "LEFT" && direction !== "RIGHT") nextDirection = "LEFT";
  if (newDirection === "RIGHT" && direction !== "LEFT") nextDirection = "RIGHT";
  if (newDirection === "UP" && direction !== "DOWN") nextDirection = "UP";
  if (newDirection === "DOWN" && direction !== "UP") nextDirection = "DOWN";
}

function turn(action) {
  const index = directions.indexOf(direction);
  if (action === 1) direction = directions[(index + 3) % 4];
  if (action === 2) direction = directions[(index + 1) % 4];
}

function getState() {
  const head = snake[0];
  const pointL = { x: head.x - block, y: head.y };
  const pointR = { x: head.x + block, y: head.y };
  const pointU = { x: head.x, y: head.y - block };
  const pointD = { x: head.x, y: head.y + block };

  const dirL = direction === "LEFT";
  const dirR = direction === "RIGHT";
  const dirU = direction === "UP";
  const dirD = direction === "DOWN";

  const dangerStraight =
    (dirR && isCollision(pointR)) ||
    (dirL && isCollision(pointL)) ||
    (dirU && isCollision(pointU)) ||
    (dirD && isCollision(pointD));

  const dangerLeft =
    (dirU && isCollision(pointL)) ||
    (dirD && isCollision(pointR)) ||
    (dirL && isCollision(pointD)) ||
    (dirR && isCollision(pointU));

  const dangerRight =
    (dirD && isCollision(pointL)) ||
    (dirU && isCollision(pointR)) ||
    (dirR && isCollision(pointD)) ||
    (dirL && isCollision(pointU));

  return [
    dangerStraight,
    dangerLeft,
    dangerRight,
    dirL,
    dirR,
    dirU,
    dirD,
    food.x < head.x,
    food.x > head.x,
    food.y < head.y,
    food.y > head.y,
  ].map((value) => (value ? 1 : 0)).join("");
}

function getQValues(state) {
  if (!qTable[state]) qTable[state] = [0, 0, 0];
  return qTable[state];
}

function getAction(state) {
  if (Math.random() < epsilon) {
    return Math.floor(Math.random() * 3);
  }
  const values = getQValues(state);
  return values.indexOf(Math.max(...values));
}

function trainStep(state, action, reward, nextState, done) {
  const values = getQValues(state);
  const currentQ = values[action];
  const futureQ = done ? 0 : Math.max(...getQValues(nextState));
  const target = reward + gamma * futureQ;
  values[action] = currentQ + alpha * (target - currentQ);
}

function draw() {
  ctx.fillStyle = "#0f1117";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "#171d26";
  ctx.lineWidth = 1;
  for (let x = 0; x <= canvas.width; x += block) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }
  for (let y = 0; y <= canvas.height; y += block) {
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(canvas.width, y);
    ctx.stroke();
  }

  snake.forEach((part, index) => {
    ctx.fillStyle = index === 0 ? "#47df7a" : "#32c766";
    ctx.fillRect(part.x + 1, part.y + 1, block - 2, block - 2);
    ctx.strokeStyle = "#178d43";
    ctx.strokeRect(part.x + 1, part.y + 1, block - 2, block - 2);
  });

  ctx.fillStyle = "#f05252";
  ctx.fillRect(food.x + 2, food.y + 2, block - 4, block - 4);
}

function updateStats() {
  scoreEl.textContent = score;
  bestScoreEl.textContent = bestScore;
  episodeEl.textContent = episode;
  epsilonEl.textContent = epsilon.toFixed(3);
  statesEl.textContent = Object.keys(qTable).length;
}

function setActiveButton(button) {
  [humanBtn, aiBtn].forEach((item) => item.classList.remove("active"));
  button.classList.add("active");
}

function addLog(text) {
  const row = document.createElement("div");
  row.textContent = text;
  logEl.prepend(row);
  while (logEl.children.length > 40) {
    logEl.lastChild.remove();
  }
}

function saveQTable() {
  localStorage.setItem("snake_q_table", JSON.stringify(qTable));
  messageEl.textContent = "Q-table saved in this browser.";
}

function loadQTable() {
  try {
    return JSON.parse(localStorage.getItem("snake_q_table")) || {};
  } catch {
    return {};
  }
}

function clearQTable() {
  qTable = {};
  epsilon = 1;
  localStorage.removeItem("snake_q_table");
  messageEl.textContent = "Q-table cleared.";
  updateStats();
}

humanBtn.addEventListener("click", startHuman);
aiBtn.addEventListener("click", startAi);
restartBtn.addEventListener("click", () => {
  if (mode === "ai") startAi();
  else startHuman();
});
saveBtn.addEventListener("click", saveQTable);
clearBtn.addEventListener("click", clearQTable);

speedRange.addEventListener("input", () => {
  speedText.textContent = `${speedRange.value} FPS`;
  if (timer) startLoop();
});

document.getElementById("upBtn").addEventListener("click", () => setDirection("UP"));
document.getElementById("leftBtn").addEventListener("click", () => setDirection("LEFT"));
document.getElementById("downBtn").addEventListener("click", () => setDirection("DOWN"));
document.getElementById("rightBtn").addEventListener("click", () => setDirection("RIGHT"));

window.addEventListener("keydown", (event) => {
  if (["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"].includes(event.key)) {
    event.preventDefault();
  }
  if (event.key === "ArrowUp") setDirection("UP");
  if (event.key === "ArrowDown") setDirection("DOWN");
  if (event.key === "ArrowLeft") setDirection("LEFT");
  if (event.key === "ArrowRight") setDirection("RIGHT");
});

resetGame();
draw();
updateStats();
