/**
 * game.js — 主游戏脚本
 * Canvas 渲染循环、键盘事件监听、状态同步（含客户端 mock 引擎）
 */

import {
  COLS, ROWS, CELL, PIECE_COLORS,
  drawGrid, drawActivePiece, drawGhostPiece,
  drawNextPiece, drawGameOver, computeGhostY, collides,
} from './renderer.js';

// ── Tetromino definitions ───────────────────────────────────────────

const SHAPES = {
  I: [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
  O: [[1,1],[1,1]],
  T: [[0,1,0],[1,1,1],[0,0,0]],
  S: [[0,1,1],[1,1,0],[0,0,0]],
  Z: [[1,1,0],[0,1,1],[0,0,0]],
  J: [[1,0,0],[1,1,1],[0,0,0]],
  L: [[0,0,1],[1,1,1],[0,0,0]],
};

const PIECE_TYPES = Object.keys(SHAPES);

// ── Mock engine state ───────────────────────────────────────────────

let grid = [];
let currentPiece = null;
let nextPiece = null;
let score = 0;
let level = 1;
let linesCleared = 0;
let gameOver = false;

function createGrid() {
  const g = [];
  for (let r = 0; r < ROWS; r++) {
    g.push(new Array(COLS).fill(0));
  }
  return g;
}

function randomType() {
  return PIECE_TYPES[Math.floor(Math.random() * PIECE_TYPES.length)];
}

function makePiece(type) {
  const shape = SHAPES[type].map(row => [...row]);
  return {
    type,
    shape,
    x: Math.floor((COLS - shape[0].length) / 2),
    y: 0,
  };
}

function rotateMatrix(matrix) {
  const n = matrix.length;
  const result = [];
  for (let c = 0; c < n; c++) {
    const row = [];
    for (let r = n - 1; r >= 0; r--) {
      row.push(matrix[r][c]);
    }
    result.push(row);
  }
  return result;
}

function lockPiece() {
  const { shape, x, y, type } = currentPiece;
  const color = PIECE_COLORS[type];
  for (let r = 0; r < shape.length; r++) {
    for (let c = 0; c < shape[r].length; c++) {
      if (shape[r][c]) {
        const ny = y + r;
        const nx = x + c;
        if (ny >= 0 && ny < ROWS && nx >= 0 && nx < COLS) {
          grid[ny][nx] = color;
        }
      }
    }
  }
  clearLines();
}

function clearLines() {
  let cleared = 0;
  for (let r = ROWS - 1; r >= 0; r--) {
    if (grid[r].every(cell => cell !== 0)) {
      grid.splice(r, 1);
      grid.unshift(new Array(COLS).fill(0));
      cleared++;
      r++; // re-check this row
    }
  }
  if (cleared > 0) {
    const points = [0, 100, 300, 500, 800];
    score += (points[cleared] || 800) * level;
    linesCleared += cleared;
    level = Math.floor(linesCleared / 10) + 1;
  }
}

function spawnPiece() {
  currentPiece = nextPiece || makePiece(randomType());
  nextPiece = makePiece(randomType());
  if (collides(currentPiece.shape, currentPiece.x, currentPiece.y, grid)) {
    gameOver = true;
  }
}

// ── Engine actions ──────────────────────────────────────────────────

function engineMoveLeft() {
  if (gameOver || !currentPiece) return;
  if (!collides(currentPiece.shape, currentPiece.x - 1, currentPiece.y, grid)) {
    currentPiece.x--;
  }
}

function engineMoveRight() {
  if (gameOver || !currentPiece) return;
  if (!collides(currentPiece.shape, currentPiece.x + 1, currentPiece.y, grid)) {
    currentPiece.x++;
  }
}

function engineRotate() {
  if (gameOver || !currentPiece) return;
  const rotated = rotateMatrix(currentPiece.shape);
  // Try basic rotation, then wall kicks
  const kicks = [0, -1, 1, -2, 2];
  for (const kick of kicks) {
    if (!collides(rotated, currentPiece.x + kick, currentPiece.y, grid)) {
      currentPiece.shape = rotated;
      currentPiece.x += kick;
      return;
    }
  }
}

function engineSoftDrop() {
  if (gameOver || !currentPiece) return;
  if (!collides(currentPiece.shape, currentPiece.x, currentPiece.y + 1, grid)) {
    currentPiece.y++;
    score += 1;
  }
}

function engineHardDrop() {
  if (gameOver || !currentPiece) return;
  const ghostY = computeGhostY(currentPiece, grid);
  score += (ghostY - currentPiece.y) * 2;
  currentPiece.y = ghostY;
  lockPiece();
  spawnPiece();
}

function engineTick() {
  if (gameOver || !currentPiece) return;
  if (!collides(currentPiece.shape, currentPiece.x, currentPiece.y + 1, grid)) {
    currentPiece.y++;
  } else {
    lockPiece();
    spawnPiece();
  }
}

function engineReset() {
  grid = createGrid();
  score = 0;
  level = 1;
  linesCleared = 0;
  gameOver = false;
  currentPiece = null;
  nextPiece = null;
  spawnPiece();
}

function getEngineState() {
  return { grid, score, level, lines_cleared: linesCleared, current_piece: currentPiece, next_piece: nextPiece, game_over: gameOver };
}

// ── Canvas setup ────────────────────────────────────────────────────

const gameCanvas = document.getElementById('game-canvas');
const gameCtx = gameCanvas.getContext('2d');
const nextCanvas = document.getElementById('next-canvas');
const nextCtx = nextCanvas.getContext('2d');

const scoreEl = document.getElementById('score-value');
const levelEl = document.getElementById('level-value');
const linesEl = document.getElementById('lines-value');

const gameOverOverlay = document.getElementById('game-over-overlay');
const restartBtn = document.getElementById('restart-btn');

// ── Render loop ─────────────────────────────────────────────────────

function render() {
  const state = getEngineState();
  gameCtx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
  drawGrid(gameCtx, state.grid);
  drawGhostPiece(gameCtx, state.current_piece, state.grid);
  drawActivePiece(gameCtx, state.current_piece);
  drawNextPiece(nextCtx, state.next_piece);

  scoreEl.textContent = state.score;
  levelEl.textContent = state.level;
  linesEl.textContent = state.lines_cleared;

  if (state.game_over) {
    drawGameOver(gameCtx);
    gameOverOverlay.classList.remove('hidden');
  } else {
    gameOverOverlay.classList.add('hidden');
  }
}

// ── Keyboard input ──────────────────────────────────────────────────

const keysDown = new Set();
let lastActionTime = 0;
const DAS_DELAY = 170;
const DAS_REPEAT = 50;

document.addEventListener('keydown', (e) => {
  if (gameOver && e.code !== 'Space') return;

  const now = performance.now();
  const actionKeys = ['ArrowLeft', 'ArrowRight', 'ArrowDown'];

  if (actionKeys.includes(e.code)) {
    e.preventDefault();
    if (!keysDown.has(e.code)) {
      keysDown.add(e.code);
      handleKey(e.code);
      lastActionTime = now;
    }
  } else if (e.code === 'ArrowUp') {
    e.preventDefault();
    engineRotate();
  } else if (e.code === 'Space') {
    e.preventDefault();
    if (gameOver) {
      engineReset();
    } else {
      engineHardDrop();
    }
  }
});

document.addEventListener('keyup', (e) => {
  keysDown.delete(e.code);
});

function handleKey(code) {
  switch (code) {
    case 'ArrowLeft': engineMoveLeft(); break;
    case 'ArrowRight': engineMoveRight(); break;
    case 'ArrowDown': engineSoftDrop(); break;
  }
}

function processDAS() {
  const now = performance.now();
  for (const code of keysDown) {
    if (now - lastActionTime >= DAS_REPEAT) {
      handleKey(code);
      lastActionTime = now;
    }
  }
}

// ── Game loop ───────────────────────────────────────────────────────

let lastTick = 0;

function tickInterval() {
  return Math.max(100, 800 - (level - 1) * 70);
}

function gameLoop(timestamp) {
  if (!gameOver) {
    if (timestamp - lastTick >= tickInterval()) {
      engineTick();
      lastTick = timestamp;
    }
    processDAS();
  }
  render();
  requestAnimationFrame(gameLoop);
}

// ── Restart button ──────────────────────────────────────────────────

restartBtn.addEventListener('click', () => {
  engineReset();
});

// ── Init ────────────────────────────────────────────────────────────

engineReset();
requestAnimationFrame(gameLoop);
