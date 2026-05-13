/**
 * multiplayer.js — WebSocket 多人房间与对战同步
 * 处理房间创建/加入、对手状态渲染、垃圾行攻击
 */

import { ROWS, COLS, CELL, PIECE_COLORS, drawGrid, drawActivePiece, drawGameOver } from './renderer.js';

let socket = null;
let myRoomId = null;
let mySid = null;
let opponents = {};
let onGarbageLines = null;
let onGameOver = null;
let onGameStarted = null;

const GARBAGE_COLOR = '#888888';

function connect() {
  if (socket && socket.connected) return;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  socket = io();

  socket.on('connect', () => {
    mySid = socket.id;
    console.log('Connected:', mySid);
  });

  socket.on('room_created', (data) => {
    myRoomId = data.room_id;
    updateRoomUI(data.room);
    setStatus(`房间已创建: ${myRoomId}`);
  });

  socket.on('player_joined', (data) => {
    updateRoomUI(data.room);
    setStatus(`玩家加入 (${data.room.players.length}/${data.room.max_players})`);
  });

  socket.on('player_disconnected', (data) => {
    delete opponents[data.sid];
    removeOpponentCanvas(data.sid);
    updateRoomUI(data.room);
    setStatus('有玩家断开连接');
  });

  socket.on('opponent_state', (data) => {
    opponents[data.sid] = data;
    renderOpponent(data.sid, data.grid);
  });

  socket.on('garbage_lines', (data) => {
    if (onGarbageLines) {
      onGarbageLines(data.lines);
    }
  });

  socket.on('game_started', (data) => {
    if (onGameStarted) onGameStarted();
    setStatus('游戏开始！');
    hideRoomPanel();
  });

  socket.on('you_win', (data) => {
    if (onGameOver) onGameOver(true, data.rankings);
  });

  socket.on('game_over', (data) => {
    if (onGameOver) onGameOver(false, data.rankings);
  });

  socket.on('room_full', () => {
    setStatus('房间已满！');
  });

  socket.on('room_not_found', () => {
    setStatus('房间不存在！');
  });

  socket.on('game_already_started', () => {
    setStatus('游戏已经开始！');
  });

  socket.on('not_enough_players', () => {
    setStatus('至少需要 2 名玩家！');
  });

  socket.on('not_host', () => {
    setStatus('只有房主可以开始游戏！');
  });

  socket.on('already_started', () => {
    setStatus('游戏已经开始了！');
  });
}

function createRoom(name) {
  connect();
  socket.emit('create_room', { name });
}

function joinRoom(roomId, name) {
  connect();
  socket.emit('join_room', { room_id: roomId, name });
}

function startGame() {
  if (!socket || !myRoomId) return;
  socket.emit('start_game');
}

function sendStateUpdate(state) {
  if (!socket || !myRoomId) return;
  socket.emit('game_state_update', {
    grid: state.grid,
    score: state.score,
    lines_cleared: state.lines_cleared,
    game_over: state.game_over,
  });
}

function sendLinesCleared(lines) {
  if (!socket || !myRoomId) return;
  socket.emit('lines_cleared_event', { lines });
}

function sendGameOver() {
  if (!socket || !myRoomId) return;
  socket.emit('player_game_over');
}

function setGarbageHandler(fn) {
  onGarbageLines = fn;
}

function setGameOverHandler(fn) {
  onGameOver = fn;
}

function setGameStartedHandler(fn) {
  onGameStarted = fn;
}

// ── Opponent rendering ─────────────────────────────────────────────

function getOrCreateOpponentCanvas(sid) {
  let container = document.getElementById('opponents-container');
  let wrapper = document.getElementById(`opponent-${sid}`);
  if (!wrapper) {
    wrapper = document.createElement('div');
    wrapper.id = `opponent-${sid}`;
    wrapper.className = 'opponent-wrapper';
    const label = document.createElement('div');
    label.className = 'opponent-label';
    label.textContent = `对手`;
    const canvas = document.createElement('canvas');
    canvas.width = COLS * CELL;
    canvas.height = ROWS * CELL;
    canvas.className = 'opponent-canvas';
    wrapper.appendChild(label);
    wrapper.appendChild(canvas);
    container.appendChild(wrapper);
  }
  return wrapper.querySelector('canvas');
}

function renderOpponent(sid, grid) {
  const canvas = getOrCreateOpponentCanvas(sid);
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  for (let r = 0; r < ROWS; r++) {
    for (let c = 0; c < COLS; c++) {
      const x = c * CELL;
      const y = r * CELL;
      if (grid[r] && grid[r][c]) {
        const val = grid[r][c];
        const color = PIECE_COLORS[val] || GARBAGE_COLOR;
        ctx.fillStyle = color;
        ctx.fillRect(x + 1, y + 1, CELL - 2, CELL - 2);
      } else {
        ctx.fillStyle = '#0f0f23';
        ctx.fillRect(x, y, CELL, CELL);
        ctx.strokeStyle = '#1a1a2e';
        ctx.lineWidth = 0.5;
        ctx.strokeRect(x, y, CELL, CELL);
      }
    }
  }
}

function removeOpponentCanvas(sid) {
  const wrapper = document.getElementById(`opponent-${sid}`);
  if (wrapper) wrapper.remove();
}

// ── UI helpers ──────────────────────────────────────────────────────

function updateRoomUI(room) {
  const roomInfo = document.getElementById('room-info');
  if (roomInfo) {
    const playerList = room.players.map(p => p.name || p.sid.substring(0, 6)).join(', ');
    roomInfo.textContent = `房间: ${room.room_id} | 玩家: ${playerList}`;
  }
  const startBtn = document.getElementById('start-btn');
  if (startBtn && room) {
    startBtn.style.display = room.host_sid === mySid ? 'inline-block' : 'none';
  }
}

function setStatus(msg) {
  const el = document.getElementById('multiplayer-status');
  if (el) el.textContent = msg;
}

function hideRoomPanel() {
  const panel = document.getElementById('room-panel');
  if (panel) panel.style.display = 'none';
}

export {
  connect,
  createRoom,
  joinRoom,
  startGame,
  sendStateUpdate,
  sendLinesCleared,
  sendGameOver,
  setGarbageHandler,
  setGameOverHandler,
  setGameStartedHandler,
};
