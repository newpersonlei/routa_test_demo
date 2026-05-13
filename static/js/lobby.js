/**
 * lobby.js — 房间大厅交互逻辑
 *
 * 负责初始化 WebSocket 连接、绑定创建/加入房间按钮事件。
 * 使用 MockWebSocket 在开发阶段模拟后端响应。
 */

(function () {
  'use strict';

  var ws = null;

  // ---- Mock WebSocket（开发阶段使用，后端就绪后替换为真实 WebSocket）----

  var MockWebSocket = function () {
    this.handlers = {};
    this.readyState = 1; // OPEN
    var self = this;
    setTimeout(function () {
      self._emit('open', {});
    }, 0);
  };

  MockWebSocket.prototype.addEventListener = function (event, handler) {
    if (!this.handlers[event]) this.handlers[event] = [];
    this.handlers[event].push(handler);
  };

  MockWebSocket.prototype.send = function (data) {
    var msg = JSON.parse(data);
    var self = this;
    setTimeout(function () {
      switch (msg.type) {
        case 'create_room':
          self._emit('message', { data: JSON.stringify({
            type: 'room_created',
            roomId: 'ROOM-' + Math.random().toString(36).substr(2, 6).toUpperCase()
          })});
          break;
        case 'join_room':
          if (msg.roomId) {
            self._emit('message', { data: JSON.stringify({
              type: 'room_joined',
              roomId: msg.roomId,
              players: ['Player1', 'You']
            })});
          } else {
            self._emit('message', { data: JSON.stringify({
              type: 'error',
              message: '房间 ID 不能为空'
            })});
          }
          break;
      }
    }, 100);
  };

  MockWebSocket.prototype._emit = function (event, data) {
    var handlers = this.handlers[event] || [];
    handlers.forEach(function (h) { h(data); });
  };

  // ---- 初始化 WebSocket 连接 ----

  function connectWebSocket() {
    var wsUrl = (location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + location.host + '/ws';
    try {
      ws = new WebSocket(wsUrl);
    } catch (e) {
      console.warn('[lobby] WebSocket 连接失败，使用 Mock 模式:', e.message);
      ws = new MockWebSocket();
    }

    ws.addEventListener('message', function (event) {
      var msg = JSON.parse(event.data);
      handleMessage(msg);
    });

    ws.addEventListener('open', function () {
      setStatus('已连接到服务器', 'success');
    });

    ws.addEventListener('error', function () {
      setStatus('连接异常，使用离线模式', 'warning');
      ws = new MockWebSocket();
      ws.addEventListener('message', function (event) {
        handleMessage(JSON.parse(event.data));
      });
    });
  }

  // ---- 消息处理 ----

  function handleMessage(msg) {
    switch (msg.type) {
      case 'room_created':
        setStatus('房间已创建，ID: ' + msg.roomId, 'success');
        setTimeout(function () {
          location.href = '/game?room=' + encodeURIComponent(msg.roomId);
        }, 500);
        break;
      case 'room_joined':
        setStatus('已加入房间 ' + msg.roomId, 'success');
        setTimeout(function () {
          location.href = '/game?room=' + encodeURIComponent(msg.roomId);
        }, 500);
        break;
      case 'error':
        setStatus(msg.message || '操作失败', 'error');
        break;
    }
  }

  function sendWS(type, data) {
    var payload = Object.assign({ type: type }, data || {});
    if (ws && ws.readyState === 1) {
      ws.send(JSON.stringify(payload));
    }
  }

  // ---- UI 辅助 ----

  function setStatus(text, level) {
    var el = document.getElementById('lobby-status');
    if (!el) return;
    el.textContent = text;
    el.className = 'lobby-status lobby-status--' + (level || 'info');
  }

  // ---- 绑定事件 ----

  function bindEvents() {
    var btnCreate = document.getElementById('btn-create-room');
    var btnJoin = document.getElementById('btn-join-room');
    var inputRoomId = document.getElementById('input-room-id');

    if (btnCreate) {
      btnCreate.addEventListener('click', function () {
        setStatus('正在创建房间...', 'info');
        sendWS('create_room');
      });
    }

    if (btnJoin && inputRoomId) {
      btnJoin.addEventListener('click', function () {
        var roomId = inputRoomId.value.trim();
        if (!roomId) {
          setStatus('请输入房间 ID', 'error');
          return;
        }
        setStatus('正在加入房间 ' + roomId + '...', 'info');
        sendWS('join_room', { roomId: roomId });
      });

      inputRoomId.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
          btnJoin.click();
        }
      });
    }
  }

  // ---- 启动 ----

  document.addEventListener('DOMContentLoaded', function () {
    bindEvents();
    connectWebSocket();
  });
})();
