"""Room manager — handles room lifecycle, player management, and game flow."""

from rooms.models import Player, Room


GARBAGE_MAP = {
    2: 1,
    3: 2,
    4: 4,
}


class RoomManager:
    def __init__(self):
        self.rooms: dict[str, Room] = {}
        self.sid_to_room: dict[str, str] = {}

    def create_room(self, sid, player_name=""):
        room = Room()
        player = Player(sid=sid, name=player_name or f"Player_{sid[:4]}")
        room.add_player(player)
        self.rooms[room.room_id] = room
        self.sid_to_room[sid] = room.room_id
        return room

    def join_room(self, room_id, sid, player_name=""):
        room = self.rooms.get(room_id)
        if room is None:
            return None, "room_not_found"
        if room.is_full:
            return None, "room_full"
        if room.game_started:
            return None, "game_already_started"
        player = Player(sid=sid, name=player_name or f"Player_{sid[:4]}")
        room.add_player(player)
        self.sid_to_room[sid] = room_id
        return room, None

    def leave_room(self, sid):
        room_id = self.sid_to_room.pop(sid, None)
        if room_id is None:
            return None
        room = self.rooms.get(room_id)
        if room is None:
            return None
        room.remove_player(sid)
        if room.player_count == 0:
            del self.rooms[room_id]
        return room

    def get_room_for_sid(self, sid):
        room_id = self.sid_to_room.get(sid)
        if room_id is None:
            return None
        return self.rooms.get(room_id)

    def start_game(self, sid):
        room = self.get_room_for_sid(sid)
        if room is None:
            return None, "not_in_room"
        if room.host_sid != sid:
            return None, "not_host"
        if not room.is_ready:
            return None, "not_enough_players"
        if room.game_started:
            return None, "already_started"
        room.game_started = True
        for p in room.players:
            p.game_over = False
            p.score = 0
            p.lines_cleared = 0
        return room, None

    def check_game_over(self, room):
        alive = room.alive_players
        if len(alive) == 1 and room.player_count >= 2:
            winner = alive[0]
            rankings = self._compute_rankings(room)
            return winner, rankings
        if len(alive) == 0:
            rankings = self._compute_rankings(room)
            return None, rankings
        return None, None

    def _compute_rankings(self, room):
        sorted_players = sorted(
            room.players,
            key=lambda p: (not p.game_over, p.lines_cleared),
            reverse=True,
        )
        return [
            {"sid": p.sid, "name": p.name, "lines_cleared": p.lines_cleared, "score": p.score}
            for p in sorted_players
        ]

    @staticmethod
    def garbage_for_lines(lines_cleared):
        return GARBAGE_MAP.get(lines_cleared, 0)
