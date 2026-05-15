/**
 * game-result.js — 结算面板组件
 *
 * 监听 game_over 事件，弹出结算面板显示所有玩家排名。
 * 提供「返回大厅」按钮跳转回大厅页面。
 */

(function () {
  'use strict';

  var panelElement = null;

  /**
   * 创建结算面板 DOM 并插入页面
   */
  function ensurePanel() {
    if (panelElement) return panelElement;

    panelElement = document.createElement('div');
    panelElement.className = 'result-panel-overlay';
    panelElement.id = 'result-panel';
    panelElement.style.display = 'none';

    var panel = document.createElement('div');
    panel.className = 'result-panel';

    var title = document.createElement('h2');
    title.className = 'result-title';
    title.textContent = '游戏结束';
    panel.appendChild(title);

    var rankList = document.createElement('div');
    rankList.className = 'result-rank-list';
    rankList.id = 'result-rank-list';
    panel.appendChild(rankList);

    var btnBack = document.createElement('button');
    btnBack.className = 'btn btn-primary result-btn-back';
    btnBack.textContent = '返回大厅';
    btnBack.addEventListener('click', function () {
      location.href = '/lobby';
    });
    panel.appendChild(btnBack);

    panelElement.appendChild(panel);
    document.body.appendChild(panelElement);

    return panelElement;
  }

  /**
   * 显示结算面板
   * @param {Array} rankings - 排名数据 [{playerId, playerName, rank, score}]
   */
  function showResult(rankings) {
    ensurePanel();

    var rankList = document.getElementById('result-rank-list');
    rankList.innerHTML = '';

    var sorted = (rankings || []).slice().sort(function (a, b) {
      return (a.rank || 999) - (b.rank || 999);
    });

    sorted.forEach(function (entry) {
      var item = document.createElement('div');
      item.className = 'result-rank-item';

      var rankBadge = document.createElement('span');
      rankBadge.className = 'result-rank-badge rank-' + entry.rank;
      rankBadge.textContent = '#' + entry.rank;

      var nameEl = document.createElement('span');
      nameEl.className = 'result-player-name';
      nameEl.textContent = entry.playerName || entry.playerId || '???';

      var scoreEl = document.createElement('span');
      scoreEl.className = 'result-score';
      scoreEl.textContent = entry.score != null ? entry.score + ' 分' : '';

      item.appendChild(rankBadge);
      item.appendChild(nameEl);
      item.appendChild(scoreEl);
      rankList.appendChild(item);
    });

    panelElement.style.display = 'flex';
  }

  /**
   * 隐藏结算面板
   */
  function hideResult() {
    if (panelElement) {
      panelElement.style.display = 'none';
    }
  }

  /**
   * 绑定 WebSocket 事件
   * @param {WebSocket|object} ws
   */
  function bindWebSocket(ws) {
    if (!ws) return;
    ws.addEventListener('message', function (event) {
      var msg;
      try {
        msg = JSON.parse(event.data);
      } catch (e) { return; }

      if (msg.type === 'game_over') {
        showResult(msg.rankings || []);
      }
    });
  }

  // 导出
  window.GameResult = {
    showResult: showResult,
    hideResult: hideResult,
    bindWebSocket: bindWebSocket
  };
})();
