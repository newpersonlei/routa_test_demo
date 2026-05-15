"""Tests for multiplayer room management, WebSocket events, and engine garbage lines."""

import pytest
from rooms.models import Player, Room
from rooms.manager import RoomManager
from game.engine import TetrisEngine


# ── Room model tests ─────────────────────────────────────────────────


class TestPlayer:
    def test_to_dict(self):
        p = Player(sid="abc123", name="Alice")
        d = p.to_dict()
        assert d["sid"] == "abc123"
        assert d["name"] == "Alice"
        assert d["game_over"] is False

    def test_default_name(self):
        p = Player(sid="xyz")
        assert p.sid == "xyz"
        assert p.name == ""


class TestRoom:
    def test_add_player(self):
        room = Room()
        p = Player(sid="s1", name="A")
        assert room.add_player(p) is True
        assert room.player_count == 1

    def test_first_player_becomes_host(self):
        room = Room()
        p = Player(sid="s1")
        room.add_player(p)
        assert room.host_sid == "s1"

    def test_room_full(self):
        room = Room(max_players=2)
        room.add_player(Player(sid="s1"))
        room.add_player(Player(sid="s2"))
        assert room.is_full is True
        assert room.add_player(Player(sid="s3")) is False

    def test_max_4_players(self):
        room = Room()
        for i in range(4):
            assert room.add_player(Player(sid=f"s{i}")) is True
        assert room.is_full is True
        assert room.add_player(Player(sid="s5")) is False

    def test_remove_player(self):
        room = Room()
        room.add_player(Player(sid="s1"))
        room.add_player(Player(sid="s2"))
        room.remove_player("s1")
        assert room.player_count == 1
        assert room.host_sid == "s2"

    def test_get_player(self):
        room = Room()
        room.add_player(Player(sid="s1", name="A"))
        p = room.get_player("s1")
        assert p is not None
        assert p.name == "A"
        assert room.get_player("s99") is None

    def test_is_ready(self):
        room = Room()
        assert room.is_ready is False
        room.add_player(Player(sid="s1"))
        assert room.is_ready is False
        room.add_player(Player(sid="s2"))
        assert room.is_ready is True

    def test_alive_players(self):
        room = Room()
        p1 = Player(sid="s1")
        p2 = Player(sid="s2", game_over=True)
        p3 = Player(sid="s3")
        room.players = [p1, p2, p3]
        alive = room.alive_players
        assert len(alive) == 2
        assert p2 not in alive

    def test_to_dict(self):
        room = Room(room_id="ABC123")
        room.add_player(Player(sid="s1", name="Alice"))
        d = room.to_dict()
        assert d["room_id"] == "ABC123"
        assert len(d["players"]) == 1
        assert d["game_started"] is False


# ── RoomManager tests ────────────────────────────────────────────────


class TestRoomManager:
    def test_create_room(self):
        mgr = RoomManager()
        room = mgr.create_room("s1", "Alice")
        assert room.player_count == 1
        assert room.host_sid == "s1"
        assert room.room_id in mgr.rooms

    def test_join_room(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        joined, err = mgr.join_room(room.room_id, "s2", "Bob")
        assert err is None
        assert joined.player_count == 2

    def test_join_full_room(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        for i in range(2, 5):
            mgr.join_room(room.room_id, f"s{i}")
        joined, err = mgr.join_room(room.room_id, "s5")
        assert err == "room_full"
        assert joined is None

    def test_join_nonexistent_room(self):
        mgr = RoomManager()
        joined, err = mgr.join_room("NOPE", "s1")
        assert err == "room_not_found"

    def test_leave_room(self):
        mgr = RoomManager()
        mgr.create_room("s1")
        room = mgr.leave_room("s1")
        assert room is not None
        assert room.player_count == 0

    def test_leave_room_removes_empty(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        rid = room.room_id
        mgr.leave_room("s1")
        assert rid not in mgr.rooms

    def test_leave_room_keeps_others(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        mgr.join_room(room.room_id, "s2")
        mgr.leave_room("s1")
        assert room.player_count == 1
        assert room.host_sid == "s2"

    def test_start_game_host(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        mgr.join_room(room.room_id, "s2")
        result, err = mgr.start_game("s1")
        assert err is None
        assert result.game_started is True

    def test_start_game_not_host(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        mgr.join_room(room.room_id, "s2")
        result, err = mgr.start_game("s2")
        assert err == "not_host"

    def test_start_game_not_enough(self):
        mgr = RoomManager()
        mgr.create_room("s1")
        result, err = mgr.start_game("s1")
        assert err == "not_enough_players"

    def test_check_game_over_winner(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        mgr.join_room(room.room_id, "s2")
        room.players[1].game_over = True
        winner, rankings = mgr.check_game_over(room)
        assert winner is not None
        assert winner.sid == "s1"

    def test_check_game_over_all_dead(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        mgr.join_room(room.room_id, "s2")
        room.players[0].game_over = True
        room.players[1].game_over = True
        winner, rankings = mgr.check_game_over(room)
        assert winner is None
        assert rankings is not None
        assert len(rankings) == 2

    def test_check_game_over_still_playing(self):
        mgr = RoomManager()
        room = mgr.create_room("s1")
        mgr.join_room(room.room_id, "s2")
        winner, rankings = mgr.check_game_over(room)
        assert winner is None
        assert rankings is None

    def test_garbage_for_lines(self):
        assert RoomManager.garbage_for_lines(0) == 0
        assert RoomManager.garbage_for_lines(1) == 0
        assert RoomManager.garbage_for_lines(2) == 1
        assert RoomManager.garbage_for_lines(3) == 2
        assert RoomManager.garbage_for_lines(4) == 4


# ── Engine add_garbage_lines tests ───────────────────────────────────


class TestAddGarbageLines:
    def test_adds_lines_at_bottom(self):
        engine = TetrisEngine()
        initial_top = engine.grid[0][:]
        engine.add_garbage_lines(2)
        assert engine.grid[-1].count(8) == 9
        assert engine.grid[-2].count(8) == 9

    def test_pushes_content_up(self):
        engine = TetrisEngine()
        engine.grid[-1] = [1] * 10
        engine.add_garbage_lines(1)
        assert engine.grid[-1] != [1] * 10
        assert engine.grid[-1].count(8) == 9

    def test_gap_in_garbage(self):
        engine = TetrisEngine()
        engine.add_garbage_lines(1)
        last_row = engine.grid[-1]
        gap_count = sum(1 for c in last_row if c == 0)
        assert gap_count == 1

    def test_game_over_if_piece_collides(self):
        engine = TetrisEngine()
        for r in range(18):
            engine.grid[r] = [1] * 10
        engine.current_piece = {"name": "I", "rotation": 0, "row": 0, "col": 3}
        engine.add_garbage_lines(1)
        assert engine.game_over is True

    def test_no_game_over_if_no_collision(self):
        engine = TetrisEngine()
        assert engine.game_over is False
        engine.add_garbage_lines(1)
        assert engine.game_over is False


# ── WebSocket integration tests (using Flask-SocketIO test client) ───


def _get_room_id(responses):
    for r in responses:
        if r["name"] == "room_created":
            return r["args"][0]["room_id"]
    return None


def _find_event(responses, name):
    for r in responses:
        if r["name"] == name:
            return r
    return None


class TestSocketIOEvents:
    @pytest.fixture(autouse=True)
    def _reset_manager(self):
        from app import manager
        manager.rooms.clear()
        manager.sid_to_room.clear()

    def test_create_room(self):
        from app import app, socketio
        fc = app.test_client()
        c = socketio.test_client(app, flask_test_client=fc)
        c.emit("create_room", {"name": "Alice"})
        responses = c.get_received()
        assert _find_event(responses, "room_created") is not None
        room_id = _get_room_id(responses)
        assert room_id is not None
        assert len(room_id) == 6

    def test_join_room(self):
        from app import app, socketio
        fc1 = app.test_client()
        c1 = socketio.test_client(app, flask_test_client=fc1)
        c1.emit("create_room", {"name": "Alice"})
        responses1 = c1.get_received()
        room_id = _get_room_id(responses1)
        assert room_id is not None

        fc2 = app.test_client()
        c2 = socketio.test_client(app, flask_test_client=fc2)
        c2.emit("join_room", {"room_id": room_id, "name": "Bob"})
        responses2 = c2.get_received()
        assert _find_event(responses2, "player_joined") is not None

    def test_room_full_rejection(self):
        from app import app, socketio
        fc0 = app.test_client()
        c0 = socketio.test_client(app, flask_test_client=fc0)
        c0.emit("create_room", {"name": "P0"})
        responses0 = c0.get_received()
        room_id = _get_room_id(responses0)
        assert room_id is not None

        for i in range(1, 4):
            fc = app.test_client()
            c = socketio.test_client(app, flask_test_client=fc)
            c.emit("join_room", {"room_id": room_id, "name": f"P{i}"})
            c.get_received()

        fc5 = app.test_client()
        c5 = socketio.test_client(app, flask_test_client=fc5)
        c5.emit("join_room", {"room_id": room_id})
        responses5 = c5.get_received()
        assert _find_event(responses5, "room_full") is not None

    def test_start_game(self):
        from app import app, socketio
        fc1 = app.test_client()
        c1 = socketio.test_client(app, flask_test_client=fc1)
        c1.emit("create_room", {"name": "A"})
        rid = _get_room_id(c1.get_received())
        assert rid is not None

        fc2 = app.test_client()
        c2 = socketio.test_client(app, flask_test_client=fc2)
        c2.emit("join_room", {"room_id": rid, "name": "B"})
        c2.get_received()

        c1.emit("start_game")
        responses = c1.get_received()
        assert _find_event(responses, "game_started") is not None

    def test_disconnect_removes_player(self):
        from app import app, socketio
        fc1 = app.test_client()
        c1 = socketio.test_client(app, flask_test_client=fc1)
        c1.emit("create_room", {"name": "A"})
        rid = _get_room_id(c1.get_received())
        assert rid is not None

        fc2 = app.test_client()
        c2 = socketio.test_client(app, flask_test_client=fc2)
        c2.emit("join_room", {"room_id": rid, "name": "B"})
        c2.get_received()

        c2.disconnect()
        responses = c1.get_received()
        assert _find_event(responses, "player_disconnected") is not None
