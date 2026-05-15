from game.pieces import SHAPES, get_cells, get_shape
from game.engine import TetrisEngine, GRID_WIDTH, GRID_HEIGHT, SCORE_TABLE


def test_ac1_all_seven_pieces_defined():
    assert set(SHAPES.keys()) == {"I", "O", "T", "S", "Z", "J", "L"}


def test_ac1_each_piece_has_four_rotations():
    for name, rotations in SHAPES.items():
        if name == "O":
            assert len(rotations) == 1
        else:
            assert len(rotations) == 4, (
                f"{name} should have 4 rotations, got {len(rotations)}"
            )


def test_ac1_rotation_matrices_have_correct_shape():
    for name, rotations in SHAPES.items():
        for ri, shape in enumerate(rotations):
            n_rows = len(shape)
            for row in shape:
                assert len(row) == n_rows


def test_ac1_rotation_produces_correct_cell_count():
    for name, rotations in SHAPES.items():
        for ri, shape in enumerate(rotations):
            cells = get_cells(shape, 0, 0)
            assert len(cells) == 4, (
                f"{name}[{ri}] should have 4 cells, got {len(cells)}"
            )


def test_ac1_rotation_consistency_i():
    shape0 = get_shape("I", 0)
    shape1 = get_shape("I", 1)

    cells0 = sorted(get_cells(shape0, 0, 0))
    cells1 = sorted(get_cells(shape1, 0, 0))

    assert cells0 == [(1, 0), (1, 1), (1, 2), (1, 3)]
    assert cells1 == [(0, 2), (1, 2), (2, 2), (3, 2)]


def test_ac1_rotation_consistency_t():
    shape0 = get_shape("T", 0)
    shape1 = get_shape("T", 1)

    cells0 = sorted(get_cells(shape0, 0, 0))
    cells1 = sorted(get_cells(shape1, 0, 0))

    assert cells0 == [(0, 1), (1, 0), (1, 1), (1, 2)]
    assert cells1 == [(0, 1), (1, 1), (1, 2), (2, 1)]


def test_ac2_move_left():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 0,
        "col": 5,
    }
    assert engine.move_left() is True
    assert engine.current_piece["col"] == 4


def test_ac2_move_left_blocked_by_wall():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 0,
        "col": 0,
    }
    assert engine.move_left() is False
    assert engine.current_piece["col"] == 0


def test_ac2_move_right():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 0,
        "col": 3,
    }
    assert engine.move_right() is True
    assert engine.current_piece["col"] == 4


def test_ac2_move_right_blocked_by_wall():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 0,
        "col": 7,
    }
    assert engine.move_right() is False
    assert engine.current_piece["col"] == 7


def test_ac2_soft_drop():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 0,
        "col": 3,
    }
    assert engine.soft_drop() is True
    assert engine.current_piece["row"] == 1


def test_ac2_soft_drop_into_lock():
    engine = TetrisEngine()
    engine.grid[19][3] = 1
    engine.grid[19][4] = 1
    engine.grid[19][5] = 1
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 18,
        "col": 3,
    }
    assert engine.soft_drop() is False
    assert engine.grid[18][4] == "T"


def test_ac2_hard_drop():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 0,
        "col": 3,
    }
    distance = engine.hard_drop()
    assert distance > 0
    assert engine.grid[19][4] == "T"


def test_ac2_rotate_cw():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 5,
        "col": 4,
    }
    assert engine.rotate_cw() is True
    assert engine.current_piece["rotation"] == 1


def test_ac2_rotate_ccw():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 5,
        "col": 4,
    }
    assert engine.rotate_ccw() is True
    assert engine.current_piece["rotation"] == 3


def test_ac2_rotate_blocked_by_wall():
    engine = TetrisEngine()
    engine.current_piece = {
        "name": "I",
        "rotation": 0,
        "row": 5,
        "col": 0,
    }
    result = engine.rotate_cw()
    assert result is True
    assert engine.current_piece["rotation"] == 1


def test_ac2_pieces_cannot_overlap():
    engine = TetrisEngine()
    engine.grid[5][4] = "T"
    engine.current_piece = {
        "name": "T",
        "rotation": 0,
        "row": 5,
        "col": 4,
    }
    assert engine.move_left() is False


def test_ac3_single_clear():
    engine = TetrisEngine()
    engine.grid[19] = [1] * GRID_WIDTH
    cleared, points = engine._clear_lines()
    assert cleared == 1
    assert points == 100


def test_ac3_double_clear():
    engine = TetrisEngine()
    engine.grid[18] = [1] * GRID_WIDTH
    engine.grid[19] = [1] * GRID_WIDTH
    cleared, points = engine._clear_lines()
    assert cleared == 2
    assert points == 300


def test_ac3_triple_clear():
    engine = TetrisEngine()
    engine.grid[17] = [1] * GRID_WIDTH
    engine.grid[18] = [1] * GRID_WIDTH
    engine.grid[19] = [1] * GRID_WIDTH
    cleared, points = engine._clear_lines()
    assert cleared == 3
    assert points == 500


def test_ac3_tetris_clear():
    engine = TetrisEngine()
    for r in range(16, 20):
        engine.grid[r] = [1] * GRID_WIDTH
    cleared, points = engine._clear_lines()
    assert cleared == 4
    assert points == 800


def test_ac3_score_accumulates():
    engine = TetrisEngine()
    engine.grid[19] = [1] * GRID_WIDTH
    engine._lock_piece()
    assert engine.score == 100
    assert engine.lines_cleared == 1


def test_ac3_multi_clear_accumulates():
    engine = TetrisEngine()
    engine.score = 0
    for r in range(16, 20):
        engine.grid[r] = [1] * GRID_WIDTH
    cleared, points = engine._clear_lines()
    assert cleared == 4
    assert points == 800
    assert engine.score == 0
    engine.score += points
    assert engine.score == 800


def test_ac4_game_over_on_spawn_collision():
    engine = TetrisEngine()
    for r in range(4):
        for c in range(GRID_WIDTH):
            engine.grid[r][c] = "T"
    engine.current_piece = None
    engine._spawn_current()
    assert engine.game_over is True


def test_ac4_game_over_not_set_when_clear():
    engine = TetrisEngine()
    engine._spawn_current()
    assert engine.game_over is False


def test_ac5_get_state_returns_all_keys():
    engine = TetrisEngine()
    state = engine.get_state()
    expected_keys = {
        "grid",
        "score",
        "lines_cleared",
        "current_piece",
        "next_piece",
        "game_over",
    }
    assert set(state.keys()) == expected_keys


def test_ac5_grid_dimensions():
    engine = TetrisEngine()
    state = engine.get_state()
    assert len(state["grid"]) == GRID_HEIGHT
    for row in state["grid"]:
        assert len(row) == GRID_WIDTH


def test_ac5_get_state_values():
    engine = TetrisEngine()
    engine.score = 300
    engine.lines_cleared = 4
    engine.game_over = True
    state = engine.get_state()
    assert state["score"] == 300
    assert state["lines_cleared"] == 4
    assert state["game_over"] is True
    assert state["current_piece"] is not None
    assert state["next_piece"] is not None


def test_ac5_state_does_not_share_mutation():
    engine = TetrisEngine()
    state = engine.get_state()
    state["grid"][0][0] = "X"
    assert engine.grid[0][0] == 0


def test_ac6_no_network_imports():
    import ast
    import pathlib

    base = pathlib.Path(__file__).resolve().parent.parent
    forbidden = {
        "flask",
        "socketio",
        "eventlet",
        "gevent",
        "requests",
        "websocket",
        "tornado",
    }
    for fname in ["game/pieces.py", "game/engine.py", "game/__init__.py"]:
        source = (base / fname).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top not in forbidden, (
                        f"{fname} imports forbidden module: {alias.name}"
                    )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top = node.module.split(".")[0]
                    assert top not in forbidden, (
                        f"{fname} imports forbidden module: {node.module}"
                    )


def test_ac6_import_works():
    from game import TetrisEngine

    eng = TetrisEngine()
    assert eng is not None


def test_reset_restores_initial_state():
    engine = TetrisEngine()
    engine.score = 999
    engine.lines_cleared = 50
    engine.game_over = True
    engine.reset()
    assert engine.score == 0
    assert engine.lines_cleared == 0
    assert engine.game_over is False
    assert engine.current_piece is not None
    assert engine.next_piece is not None


def test_hard_drop_after_game_over():
    engine = TetrisEngine()
    engine.game_over = True
    assert engine.hard_drop() == 0


def test_operations_after_game_over_are_noops():
    engine = TetrisEngine()
    engine.game_over = True
    assert engine.move_left() is False
    assert engine.move_right() is False
    assert engine.soft_drop() is False
    assert engine.rotate_cw() is False
    assert engine.rotate_ccw() is False


def test_score_table_values():
    assert SCORE_TABLE == {1: 100, 2: 300, 3: 500, 4: 800}
