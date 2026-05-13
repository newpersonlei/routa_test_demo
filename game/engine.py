import random

from game.pieces import SHAPES, PIECE_NAMES, WALL_KICKS, get_cells, get_shape

GRID_WIDTH = 10
GRID_HEIGHT = 20

SCORE_TABLE = {
    1: 100,
    2: 300,
    3: 500,
    4: 800,
}


class TetrisEngine:
    def __init__(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.current_piece = None
        self.next_piece = None
        self._select_next()
        self._spawn_current()

    def _random_name(self):
        return random.choice(PIECE_NAMES)

    def _select_next(self):
        self.next_piece = {
            "name": self._random_name(),
            "rotation": 0,
        }

    def _spawn_current(self):
        name = self.next_piece["name"]
        shape = get_shape(name, 0)
        col = (GRID_WIDTH - len(shape[0])) // 2
        self.current_piece = {
            "name": name,
            "rotation": 0,
            "row": 0,
            "col": col,
        }
        if not self._is_valid_position(self.current_piece):
            self.game_over = True
        self._select_next()

    def _is_valid_position(self, piece):
        name = piece["name"]
        shape = get_shape(name, piece["rotation"])
        cells = get_cells(shape, piece["row"], piece["col"])
        for r, c in cells:
            if r < 0 or r >= GRID_HEIGHT or c < 0 or c >= GRID_WIDTH:
                return False
            if self.grid[r][c]:
                return False
        return True

    def move_left(self):
        if self.game_over or self.current_piece is None:
            return False
        new_piece = dict(self.current_piece)
        new_piece["col"] -= 1
        if self._is_valid_position(new_piece):
            self.current_piece = new_piece
            return True
        return False

    def move_right(self):
        if self.game_over or self.current_piece is None:
            return False
        new_piece = dict(self.current_piece)
        new_piece["col"] += 1
        if self._is_valid_position(new_piece):
            self.current_piece = new_piece
            return True
        return False

    def soft_drop(self):
        if self.game_over or self.current_piece is None:
            return False
        new_piece = dict(self.current_piece)
        new_piece["row"] += 1
        if self._is_valid_position(new_piece):
            self.current_piece = new_piece
            return True
        self._lock_piece()
        return False

    def hard_drop(self):
        if self.game_over or self.current_piece is None:
            return 0
        drop_distance = 0
        while True:
            new_piece = dict(self.current_piece)
            new_piece["row"] += 1
            if self._is_valid_position(new_piece):
                self.current_piece = new_piece
                drop_distance += 1
            else:
                break
        self._lock_piece()
        return drop_distance

    def rotate_cw(self):
        return self._try_rotate(1)

    def rotate_ccw(self):
        return self._try_rotate(-1)

    def _try_rotate(self, direction):
        if self.game_over or self.current_piece is None:
            return False
        name = self.current_piece["name"]
        if name == "O":
            return False
        old_rotation = self.current_piece["rotation"]
        new_rotation = (old_rotation + direction) % 4
        kick_key = (old_rotation, new_rotation)
        kicks = WALL_KICKS.get(name, {}).get(kick_key, [(0, 0)])
        for drow, dcol in kicks:
            new_piece = {
                "name": name,
                "rotation": new_rotation,
                "row": self.current_piece["row"] + drow,
                "col": self.current_piece["col"] + dcol,
            }
            if self._is_valid_position(new_piece):
                self.current_piece = new_piece
                return True
        return False

    def _lock_piece(self):
        name = self.current_piece["name"]
        shape = get_shape(name, self.current_piece["rotation"])
        cells = get_cells(shape, self.current_piece["row"], self.current_piece["col"])
        for r, c in cells:
            if 0 <= r < GRID_HEIGHT and 0 <= c < GRID_WIDTH:
                self.grid[r][c] = name
        cleared, points = self._clear_lines()
        self.score += points
        self.lines_cleared += cleared
        self.current_piece = None
        self._spawn_current()

    def _clear_lines(self):
        full_rows = []
        for r in range(GRID_HEIGHT):
            if all(self.grid[r][c] for c in range(GRID_WIDTH)):
                full_rows.append(r)
        if not full_rows:
            return 0, 0
        for r in reversed(full_rows):
            del self.grid[r]
            self.grid.insert(0, [0] * GRID_WIDTH)
        count = len(full_rows)
        points = SCORE_TABLE.get(count, 0)
        return count, points

    def get_state(self):
        state = {
            "grid": [row[:] for row in self.grid],
            "score": self.score,
            "lines_cleared": self.lines_cleared,
            "current_piece": dict(self.current_piece) if self.current_piece else None,
            "next_piece": dict(self.next_piece) if self.next_piece else None,
            "game_over": self.game_over,
        }
        return state

    def reset(self):
        self.grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.lines_cleared = 0
        self.game_over = False
        self.current_piece = None
        self.next_piece = None
        self._select_next()
        self._spawn_current()
