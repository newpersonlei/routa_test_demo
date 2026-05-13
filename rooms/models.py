"""Room and Player data models for multiplayer Tetris."""

import uuid
from dataclasses import dataclass, field


@dataclass
class Player:
    sid: str
    name: str = ""
    game_over: bool = False
    score: int = 0
    lines_cleared: int = 0

    def to_dict(self):
        return {
            "sid": self.sid,
            "name": self.name,
            "game_over": self.game_over,
            "score": self.score,
            "lines_cleared": self.lines_cleared,
        }


@dataclass
class Room:
    room_id: str = field(default_factory=lambda: uuid.uuid4().hex[:6].upper())
    players: list = field(default_factory=list)
    game_started: bool = False
    max_players: int = 4
    host_sid: str = ""

    @property
    def player_count(self):
        return len(self.players)

    @property
    def is_full(self):
        return self.player_count >= self.max_players

    @property
    def is_ready(self):
        return self.player_count >= 2

    @property
    def alive_players(self):
        return [p for p in self.players if not p.game_over]

    def add_player(self, player):
        if self.is_full:
            return False
        if not self.players:
            self.host_sid = player.sid
        self.players.append(player)
        return True

    def remove_player(self, sid):
        self.players = [p for p in self.players if p.sid != sid]
        if self.host_sid == sid and self.players:
            self.host_sid = self.players[0].sid

    def get_player(self, sid):
        for p in self.players:
            if p.sid == sid:
                return p
        return None

    def to_dict(self):
        return {
            "room_id": self.room_id,
            "players": [p.to_dict() for p in self.players],
            "game_started": self.game_started,
            "host_sid": self.host_sid,
            "max_players": self.max_players,
        }
