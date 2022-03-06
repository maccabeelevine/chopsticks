from __future__ import annotations
from chopsticks.move import Move, Hit, Split

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from chopsticks.core import Game
    from chopsticks.state import State
    from chopsticks.player import Player


class BotUtil:

    @staticmethod
    def get_legal_moves(g: Game, state: State, player_id: int) -> list[Move]:
        """ Get all legal moves available right now """
        legal_moves: list[Move] = cast(list[Move], BotUtil._get_legal_hit_moves(g, state, player_id))
        legal_moves.extend(BotUtil._get_legal_split_moves(g, state, player_id))
        return legal_moves

    @staticmethod
    def _get_legal_hit_moves(g: Game, state: State, player_id: int) -> list[Hit]:
        """ Generate list of legal hit moves based on game state """
        legal_hit_moves: list[Hit] = []

        # iterate through other players
        for opponent_id in range(1, g.num_players + 1):
            if not opponent_id == player_id:

                # iterate through any of my hands that are alive
                for my_hand in range(1, g.num_hands + 1):
                    if state.player(player_id).hand(my_hand).is_alive():

                        # iterate through opponent hands that are alive
                        for opponent_hand in range(1, g.num_hands + 1):
                            if g.player(opponent_id).hand(opponent_hand).is_alive():
                                move = Hit(opponent_id, my_hand, opponent_hand)
                                legal_hit_moves.append(move)

        return legal_hit_moves

    @staticmethod
    def _get_legal_split_moves(g: Game, state: State, player_id: int) -> list[Split]:
        """ Generate list of legal split moves, based on current game state """
        player = state.player(player_id)
        player_alive_fingers = player.get_alive_fingers()
        legal_split_moves: list[Split] = []
        # TODO remove hard-coded assumption about two hands, already in logic.py
        max_hand_fingers = min(player_alive_fingers, g.num_fingers - 1)
        for left_fingers in range(0, max_hand_fingers + 1):

            # if this move would actually change the game state
            if not left_fingers == player.hand(1).alive_fingers \
                    and not left_fingers == player.hand(2).alive_fingers:

                right_fingers = player_alive_fingers - left_fingers
                if not right_fingers > max_hand_fingers:
                    move = Split(1, 2, left_fingers, right_fingers)
                    legal_split_moves.append(move)

        return legal_split_moves

    @staticmethod
    def get_opponent(players: list[Player], hit: Hit) -> Player:
        player: Player
        for player in players:
            if player.id == hit.opponent_id:
                return player
        raise Exception("Could not find opponent")

