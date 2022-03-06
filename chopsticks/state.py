from __future__ import annotations
import copy
from chopsticks.logic import Logic
from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from chopsticks.player import Player
    from chopsticks.move import Move
    from chopsticks.core import Game


class State:

    def __init__(self, players: list[Player]):
        self._players = players

    def player(self, player_id: int):
        return self._players[player_id - 1]

    def players(self) -> list[Player]:
        return self._players

    def __repr__(self):
        return str([player.hands() for player in self.players()])


class Scenario(State):

    def __init__(self, g: Game, starting_state: State, player_id: int, move: Move):
        self._initPlayers(starting_state)
        self._initOpponents(player_id)
        self.move = move
        self.player_id = player_id
        Logic.do_move(g, self, move, player_id)

    def _initPlayers(self, starting_state: State):
        self._players = cast(State, copy.deepcopy(starting_state._players))

    def _initOpponents(self, player_id: int):
        self._opponents: list[Player] = []
        player: Player
        for player in self.players():
            if not player.id == player_id:
                self._opponents.append(player)
