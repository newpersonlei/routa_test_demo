/**
 * attack-effects.js — 攻击特效动画模块
 *
 * 监听 garbage_line_attack 事件，触发本方场地边框红色闪烁动画。
 * 动画持续 ≥500ms。连续攻击时重置计时器，重新开始闪烁。
 */

(function () {
  'use strict';

  var FLASH_DURATION = 600; // ms，略高于 500ms 最低要求
  var FLASH_CLASS = 'attack-flash';

  var fieldElement = null;
  var flashTimeout = null;

  /**
   * 初始化攻击特效模块
   * @param {HTMLElement} localField - 本方场地容器元素
   */
  function init(localField) {
    fieldElement = localField;
  }

  /**
   * 触发闪烁动画。
   * 如果当前正在闪烁，重置计时器重新开始。
   */
  function triggerFlash() {
    if (!fieldElement) return;

    // 清除上一次闪烁的定时器（处理连续攻击叠加）
    if (flashTimeout) {
      clearTimeout(flashTimeout);
    }

    fieldElement.classList.add(FLASH_CLASS);

    flashTimeout = setTimeout(function () {
      fieldElement.classList.remove(FLASH_CLASS);
      flashTimeout = null;
    }, FLASH_DURATION);
  }

  /**
   * 绑定 WebSocket 事件，监听 garbage_line_attack
   * @param {WebSocket|object} ws - WebSocket 实例或 Mock 对象
   */
  function bindWebSocket(ws) {
    if (!ws) return;
    ws.addEventListener('message', function (event) {
      var msg;
      try {
        msg = JSON.parse(event.data);
      } catch (e) { return; }

      if (msg.type === 'garbage_line_attack') {
        triggerFlash();
      }
    });
  }

  // 手动触发接口（供 mock 测试使用）
  function flash() {
    triggerFlash();
  }

  // 导出
  window.AttackEffects = {
    init: init,
    bindWebSocket: bindWebSocket,
    flash: flash
  };
})();
