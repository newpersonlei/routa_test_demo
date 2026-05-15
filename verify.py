"""验证脚本：检查 Tetris 前端实现的 AC 达成情况。"""

import re
import sys


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def check_ac1():
    """AC1: 10×20 网格(30px)，7种方块独立颜色，活动/锁定视觉区分"""
    errors = []

    renderer = read('static/js/renderer.js')
    game = read('static/js/game.js')
    html = read('templates/index.html')

    # Check COLS=10, ROWS=20, CELL=30
    if 'COLS = 10' not in renderer:
        errors.append('COLS != 10 in renderer.js')
    if 'ROWS = 20' not in renderer:
        errors.append('ROWS != 20 in renderer.js')
    if 'CELL = 30' not in renderer:
        errors.append('CELL != 30 in renderer.js')

    # Canvas size = COLS*CELL x ROWS*CELL = 300 x 600
    if 'width="300" height="600"' not in html:
        errors.append('Canvas dimensions not 300x600')

    # 7 piece colors
    piece_colors = re.findall(r"PIECE_COLORS\s*=\s*\{([^}]+)\}", renderer)
    if piece_colors:
        types_found = re.findall(r"(\w)\s*:", piece_colors[0])
        if len(types_found) != 7:
            errors.append(f'Expected 7 piece colors, found {len(types_found)}: {types_found}')
    else:
        errors.append('PIECE_COLORS not found in renderer.js')

    # Active vs locked visual distinction
    if 'ACTIVE_ALPHA' not in renderer or 'LOCKED_ALPHA' not in renderer:
        errors.append('Missing active/locked alpha distinction')

    return errors


def check_ac2():
    """AC2: 键盘绑定——左右移、旋转、软降、硬降"""
    errors = []
    game = read('static/js/game.js')

    key_checks = [
        ('ArrowLeft', 'engineMoveLeft'),
        ('ArrowRight', 'engineMoveRight'),
        ('ArrowUp', 'engineRotate'),
        ('ArrowDown', 'engineSoftDrop'),
        ('Space', 'engineHardDrop'),
    ]

    for key, func in key_checks:
        if key not in game:
            errors.append(f'Missing key binding for {key}')
        if func not in game:
            errors.append(f'Missing function {func}')

    return errors


def check_ac3():
    """AC3: 侧边栏4个信息区——下一个预览(Canvas)、分数、等级、已消行数"""
    errors = []
    html = read('templates/index.html')

    checks = [
        ('next-canvas', 'next piece preview canvas'),
        ('score-value', 'score display'),
        ('level-value', 'level display'),
        ('lines-value', 'lines cleared display'),
    ]

    for elem_id, desc in checks:
        if elem_id not in html:
            errors.append(f'Missing {desc} element (id={elem_id})')

    renderer = read('static/js/renderer.js')
    if 'drawNextPiece' not in renderer:
        errors.append('Missing drawNextPiece in renderer.js')

    return errors


def check_ac4():
    """AC4: Game Over 遮罩 + 重新开始按钮"""
    errors = []
    html = read('templates/index.html')
    renderer = read('static/js/renderer.js')
    game = read('static/js/game.js')

    if 'game-over-overlay' not in html:
        errors.append('Missing game-over-overlay in HTML')
    if 'restart-btn' not in html:
        errors.append('Missing restart-btn in HTML')
    if '重新开始' not in html:
        errors.append('Missing "重新开始" text on restart button')
    if 'drawGameOver' not in renderer:
        errors.append('Missing drawGameOver in renderer.js')
    if 'engineReset' not in game:
        errors.append('Missing engineReset in game.js')

    return errors


def check_ac5():
    """AC5: ≥600px 布局正常，无水平滚动"""
    errors = []
    css = read('static/css/game.css')

    if 'overflow-x: hidden' not in css:
        errors.append('Missing overflow-x: hidden on body')

    # Game board total width = 300 (canvas) + sidebar (~160) + gaps = ~520 < 600
    html = read('templates/index.html')
    canvas_match = re.search(r'width="(\d+)"', html)
    if canvas_match and int(canvas_match.group(1)) > 600:
        errors.append(f'Canvas width {canvas_match.group(1)} exceeds 600px viewport')

    return errors


def main():
    acs = [
        ('AC1', check_ac1),
        ('AC2', check_ac2),
        ('AC3', check_ac3),
        ('AC4', check_ac4),
        ('AC5', check_ac5),
    ]

    all_pass = True
    for name, check_fn in acs:
        errors = check_fn()
        if errors:
            all_pass = False
            print(f'FAIL {name}:')
            for e in errors:
                print(f'  - {e}')
        else:
            print(f'PASS {name}')

    print()
    if all_pass:
        print('All ACs passed.')
    else:
        print('Some ACs failed.')
        sys.exit(1)


if __name__ == '__main__':
    main()
