"""Flask application — serves the Tetris frontend, exposes engine API, and hosts WebSocket multiplayer."""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from rooms import RoomManager

app = Flask(__name__)
app.config["SECRET_KEY"] = "tetris-secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

manager = RoomManager()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    return jsonify(
        {
            "grid": [[0] * 10 for _ in range(20)],
            "score": 0,
            "level": 1,
            "lines_cleared": 0,
            "current_piece": None,
            "next_piece": None,
            "game_over": False,
        }
    )


# ── WebSocket event handlers ──────────────────────────────────────────


@socketio.on("create_room")
def handle_create_room(data=None):
    data = data or {}
    player_name = data.get("name", "")
    room = manager.create_room(request.sid, player_name)
    join_room(room.room_id)
    emit("room_created", {"room_id": room.room_id, "room": room.to_dict()})
    emit(
        "player_joined",
        {"room": room.to_dict(), "player": room.get_player(request.sid).to_dict()},
        room=room.room_id,
    )


@socketio.on("join_room")
def handle_join_room(data):
    room_id = data.get("room_id", "")
    player_name = data.get("name", "")
    room, error = manager.join_room(room_id, request.sid, player_name)
    if error:
        emit(error, {"room_id": room_id})
        return
    join_room(room.room_id)
    emit(
        "player_joined",
        {"room": room.to_dict(), "player": room.get_player(request.sid).to_dict()},
        room=room.room_id,
        include_self=True,
    )


@socketio.on("start_game")
def handle_start_game(data=None):
    room, error = manager.start_game(request.sid)
    if error:
        emit(error, {})
        return
    emit("game_started", {"room": room.to_dict()}, room=room.room_id)


@socketio.on("game_state_update")
def handle_game_state_update(data):
    room = manager.get_room_for_sid(request.sid)
    if room is None:
        return
    player = room.get_player(request.sid)
    if player is None:
        return
    player.score = data.get("score", 0)
    player.lines_cleared = data.get("lines_cleared", 0)
    emit(
        "opponent_state",
        {
            "sid": request.sid,
            "grid": data.get("grid"),
            "score": player.score,
            "lines_cleared": player.lines_cleared,
            "game_over": data.get("game_over", False),
        },
        room=room.room_id,
        include_self=False,
    )


@socketio.on("lines_cleared_event")
def handle_lines_cleared(data):
    lines = data.get("lines", 0)
    if lines < 2:
        return
    room = manager.get_room_for_sid(request.sid)
    if room is None:
        return
    garbage = RoomManager.garbage_for_lines(lines)
    if garbage <= 0:
        return
    for p in room.players:
        if p.sid != request.sid and not p.game_over:
            emit(
                "garbage_lines",
                {"lines": garbage, "from_sid": request.sid},
                to=p.sid,
            )


@socketio.on("player_game_over")
def handle_player_game_over(data=None):
    room = manager.get_room_for_sid(request.sid)
    if room is None:
        return
    player = room.get_player(request.sid)
    if player:
        player.game_over = True
    winner, rankings = manager.check_game_over(room)
    if winner is not None:
        emit("you_win", {"rankings": rankings}, to=winner.sid)
        for p in room.players:
            if p.sid != winner.sid:
                emit("game_over", {"rankings": rankings}, to=p.sid)
    elif rankings is not None:
        for p in room.players:
            emit("game_over", {"rankings": rankings}, to=p.sid)


@socketio.on("disconnect")
def handle_disconnect():
    room = manager.leave_room(request.sid)
    if room is None:
        return
    leave_room(room.room_id)
    emit(
        "player_disconnected",
        {"sid": request.sid, "room": room.to_dict()},
        room=room.room_id,
    )


if __name__ == "__main__":
    socketio.run(app, debug=True, port=5000)
