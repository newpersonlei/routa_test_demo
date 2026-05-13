/**
 * renderer.js — Canvas 渲染模块
 * 负责网格绘制、方块着色、Ghost piece 投影、Game Over 遮罩
 */

const COLS = 10;
const ROWS = 20;
const CELL = 30;

const PIECE_COLORS = {
  I: '#00f0f0',
  O: '#f0f000',
  T: '#a000f0',
  S: '#00f000',
  Z: '#f00000',
  J: '#0000f0',
  L: '#f0a000',
};

const GRID_LINE_COLOR = '#1a1a2e';
const LOCKED_ALPHA = 1.0;
const ACTIVE_ALPHA = 0.85;
const GHOST_ALPHA = 0.25;

function cellSize() {
  return CELL;
}

function drawGrid(ctx, grid) {
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const x = c * CELL;
      const y = r * CELL;
      if (grid[r] && grid[r][c]) {
        const color = grid[r][c];
        ctx.globalAlpha = LOCKED_ALPHA;
        drawCell(ctx, x, y, color);
      } else {
        ctx.globalAlpha = 1;
        ctx.fillStyle = '#0f0f23';
        ctx.fillRect(x, y, CELL, CELL);
        ctx.strokeStyle = GRID_LINE_COLOR;
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, CELL, CELL);
      }
    }
  }
  ctx.globalAlpha = 1;
}

function drawActivePiece(ctx, piece) {
  if (!piece || !piece.shape) return;
  const { shape, x, y, type } = piece;
  const color = PIECE_COLORS[type] || '#ffffff';

  for (let r = 0; r < shape.length; r++) {
    for (let c = 0; c < shape[r].length; c++) {
      if (shape[r][c]) {
        const px = (x + c) * CELL;
        const py = (y + r) * CELL;
        ctx.globalAlpha = ACTIVE_ALPHA;
        drawCell(ctx, px, py, color);
      }
    }
  }
  ctx.globalAlpha = 1;
}

function drawGhostPiece(ctx, piece, grid) {
  if (!piece || !piece.shape) return;
  const ghostY = computeGhostY(piece, grid);
  if (ghostY === piece.y) return;

  const { shape, x, type } = piece;
  const color = PIECE_COLORS[type] || '#ffffff';

  for (let r = 0; r < shape.length; r++) {
    for (let c = 0; c < shape[r].length; c++) {
      if (shape[r][c]) {
        const px = (x + c) * CELL;
        const py = (ghostY + r) * CELL;
        ctx.globalAlpha = GHOST_ALPHA;
        drawCell(ctx, px, py, color);
      }
    }
  }
  ctx.globalAlpha = 1;
}

function computeGhostY(piece, grid) {
  let ghostY = piece.y;
  while (!collides(piece.shape, piece.x, ghostY + 1, grid)) {
    ghostY++;
  }
  return ghostY;
}

function collides(shape, offsetX, offsetY, grid) {
  for (let r = 0; r < shape.length; r++) {
    for (let c = 0; c < shape[r].length; c++) {
      if (shape[r][c]) {
        const nx = offsetX + c;
        const ny = offsetY + r;
        if (nx < 0 || nx >= COLS || ny >= ROWS) return true;
        if (ny >= 0 && grid[ny] && grid[ny][nx]) return true;
      }
    }
  }
  return false;
}

function drawCell(ctx, x, y, color) {
  ctx.fillStyle = color;
  ctx.fillRect(x + 1, y + 1, CELL - 2, CELL - 2);

  // highlight
  ctx.fillStyle = 'rgba(255,255,255,0.18)';
  ctx.fillRect(x + 1, y + 1, CELL - 2, 4);
  ctx.fillRect(x + 1, y + 1, 4, CELL - 2);

  // shadow
  ctx.fillStyle = 'rgba(0,0,0,0.25)';
  ctx.fillRect(x + CELL - 4, y + 1, 3, CELL - 2);
  ctx.fillRect(x + 1, y + CELL - 4, CELL - 2, 3);
}

function drawNextPiece(ctx, piece) {
  const canvas = ctx.canvas;
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#0f0f23';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  if (!piece || !piece.shape) return;
  const color = PIECE_COLORS[piece.type] || '#ffffff';
  const rows = piece.shape.length;
  const cols = piece.shape[0].length;
  const offsetX = Math.floor((canvas.width - cols * CELL) / 2);
  const offsetY = Math.floor((canvas.height - rows * CELL) / 2);

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      if (piece.shape[r][c]) {
        drawCell(ctx, offsetX + c * CELL, offsetY + r * CELL, color);
      }
    }
  }
}

function drawGameOver(ctx) {
  const canvas = ctx.canvas;
  const w = canvas.width;
  const h = canvas.height;

  ctx.globalAlpha = 0.7;
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, w, h);
  ctx.globalAlpha = 1;

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 36px "Segoe UI", Arial, sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('Game Over', w / 2, h / 2 - 30);

  // restart button area — actual button is HTML overlay
  ctx.fillStyle = '#e94560';
  const bw = 160;
  const bh = 44;
  const bx = (w - bw) / 2;
  const by = h / 2 + 10;
  ctx.beginPath();
  ctx.roundRect(bx, by, bw, bh, 8);
  ctx.fill();

  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 18px "Segoe UI", Arial, sans-serif';
  ctx.fillText('重新开始', w / 2, by + bh / 2);
}

export {
  COLS,
  ROWS,
  CELL,
  PIECE_COLORS,
  cellSize,
  drawGrid,
  drawActivePiece,
  drawGhostPiece,
  drawNextPiece,
  drawGameOver,
  computeGhostY,
  collides,
};
