from __future__ import annotations
import copy
from chopsticks.logic import Logic
from typing import TYPE_CHECKING, cast
import json
if TYPE_CHECKING:
    from chopsticks.player import Player
    from chopsticks.move import Move
    from chopsticks.core import Game


class State:

    def __init__(self, players: list[Player]):
        self._players = players
        self.set_current_player(1)

    def player(self, player_id: int):
        return self._players[player_id - 1]

    def players(self) -> list[Player]:
        return self._players

    def get_current_player(self):
        return self.player(self._current_player_id)

    def set_current_player(self, current_player_id: int):
        self._current_player_id = current_player_id

    def __repr__(self):
        return str([player.hands() for player in self.players()])

    def key(self):
        return self.__hash__()

    def __hash__(self):
        hash: int = self._current_player_id
        for player in self.players():
            for hand in player.hands():
                hash = hash * 10
                hash = hash + hand.alive_fingers
        return hash

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)


class Scenario(State):

    def __init__(self, g: Game, starting_state: State, player_id: int, move: Move):
        self.set_current_player(player_id)
        self._initPlayers(starting_state)
        self._initOpponents(player_id)
        self.move = move
        Logic.do_move(g, self, move, player_id)

    def _initPlayers(self, starting_state: State):
        self._players = cast(State, copy.deepcopy(starting_state._players))

    def _initOpponents(self, player_id: int):
        self._opponents: list[Player] = []
        player: Player
        for player in self.players():
            if not player.id == player_id:
                self._opponents.append(player)
