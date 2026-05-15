/**
 * opponent-field.js — 对手场地 Canvas 渲染组件
 *
 * 管理 2-4 个对手的缩略图 Canvas，监听 WebSocket 广播更新场地数据。
 * 处理淘汰状态：灰色滤镜 + 「已淘汰」文字覆盖。
 */

(function () {
  'use strict';

  var COLS = 10;
  var ROWS = 20;
  var CELL_SIZE = 12;

  // 方块颜色映射（索引 → 颜色）
  var BLOCK_COLORS = [
    null,
    '#00f0f0', // I — 青色
    '#f0f000', // O — 黄色
    '#a000f0', // T — 紫色
    '#00f000', // S — 绿色
    '#f00000', // Z — 红色
    '#f0a000', // L — 橙色
    '#0000f0'  // J — 蓝色
  ];

  /**
   * 单个对手场地实例
   * @param {HTMLElement} container - 容器元素
   * @param {string} playerId - 玩家 ID
   * @param {string} playerName - 玩家名称
   */
  function OpponentField(container, playerId, playerName) {
    this.playerId = playerId;
    this.playerName = playerName;
    this.eliminated = false;
    this.board = [];

    // 创建包装器
    this.wrapper = document.createElement('div');
    this.wrapper.className = 'field-thumbnail';
    this.wrapper.dataset.playerId = playerId;

    // 标题
    this.nameLabel = document.createElement('div');
    this.nameLabel.className = 'field-name';
    this.nameLabel.textContent = playerName;
    this.wrapper.appendChild(this.nameLabel);

    // Canvas
    this.canvas = document.createElement('canvas');
    this.canvas.width = COLS * CELL_SIZE;
    this.canvas.height = ROWS * CELL_SIZE;
    this.canvas.className = 'field-canvas';
    this.ctx = this.canvas.getContext('2d');
    this.wrapper.appendChild(this.canvas);

    // 淘汰覆盖层
    this.elimOverlay = document.createElement('div');
    this.elimOverlay.className = 'field-eliminated-overlay';
    this.elimOverlay.innerHTML = '<span>已淘汰</span>';
    this.elimOverlay.style.display = 'none';
    this.wrapper.appendChild(this.elimOverlay);

    container.appendChild(this.wrapper);
    this.clearBoard();
  }

  OpponentField.prototype.clearBoard = function () {
    this.board = [];
    for (var r = 0; r < ROWS; r++) {
      this.board[r] = [];
      for (var c = 0; c < COLS; c++) {
        this.board[r][c] = 0;
      }
    }
    this.render();
  };

  OpponentField.prototype.updateBoard = function (boardData) {
    if (this.eliminated) return;
    this.board = boardData;
    this.render();
  };

  OpponentField.prototype.render = function () {
    var ctx = this.ctx;
    var w = this.canvas.width;
    var h = this.canvas.height;

    ctx.clearRect(0, 0, w, h);

    // 背景
    ctx.fillStyle = '#111';
    ctx.fillRect(0, 0, w, h);

    // 网格线
    ctx.strokeStyle = '#222';
    ctx.lineWidth = 0.5;
    for (var r = 0; r <= ROWS; r++) {
      ctx.beginPath();
      ctx.moveTo(0, r * CELL_SIZE);
      ctx.lineTo(w, r * CELL_SIZE);
      ctx.stroke();
    }
    for (var c = 0; c <= COLS; c++) {
      ctx.beginPath();
      ctx.moveTo(c * CELL_SIZE, 0);
      ctx.lineTo(c * CELL_SIZE, h);
      ctx.stroke();
    }

    // 方块
    for (var row = 0; row < ROWS; row++) {
      for (var col = 0; col < COLS; col++) {
        var val = this.board[row] && this.board[row][col];
        if (val) {
          ctx.fillStyle = BLOCK_COLORS[val] || '#888';
          ctx.fillRect(
            col * CELL_SIZE + 1,
            row * CELL_SIZE + 1,
            CELL_SIZE - 2,
            CELL_SIZE - 2
          );
        }
      }
    }
  };

  OpponentField.prototype.setEliminated = function () {
    this.eliminated = true;
    this.wrapper.classList.add('field-eliminated');
    this.elimOverlay.style.display = 'flex';
  };

  OpponentField.prototype.destroy = function () {
    if (this.wrapper.parentNode) {
      this.wrapper.parentNode.removeChild(this.wrapper);
    }
  };

  /**
   * OpponentFieldManager — 管理所有对手场地实例
   * @param {HTMLElement} container - 对手场地的父容器
   */
  function OpponentFieldManager(container) {
    this.container = container;
    this.fields = {}; // playerId → OpponentField
  }

  OpponentFieldManager.prototype.addPlayer = function (playerId, playerName) {
    if (this.fields[playerId]) return;
    this.fields[playerId] = new OpponentField(this.container, playerId, playerName);
  };

  OpponentFieldManager.prototype.removePlayer = function (playerId) {
    if (!this.fields[playerId]) return;
    this.fields[playerId].destroy();
    delete this.fields[playerId];
  };

  OpponentFieldManager.prototype.updatePlayerBoard = function (playerId, boardData) {
    var field = this.fields[playerId];
    if (field) {
      field.updateBoard(boardData);
    }
  };

  OpponentFieldManager.prototype.eliminatePlayer = function (playerId) {
    var field = this.fields[playerId];
    if (field) {
      field.setEliminated();
    }
  };

  OpponentFieldManager.prototype.clearAll = function () {
    var self = this;
    Object.keys(this.fields).forEach(function (pid) {
      self.fields[pid].destroy();
    });
    this.fields = {};
  };

  OpponentFieldManager.prototype.getPlayerCount = function () {
    return Object.keys(this.fields).length;
  };

  // 导出到全局
  window.OpponentFieldManager = OpponentFieldManager;
})();
