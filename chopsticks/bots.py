from __future__ import annotations

import random
from abc import abstractmethod

from chopsticks.player import Player
from chopsticks.move import Split
from chopsticks.bot_util import BotUtil
from chopsticks.state import Scenario
from chopsticks.move import Hit

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from chopsticks.core import Game
    from chopsticks.state import State
    from chopsticks.move import Move

class Bot(Player):
    """Class for bot players"""

    @abstractmethod
    def get_next_move(self, g: Game, state: State) -> Move:
        return cast(Move, None)

class RandomBot(Bot):
    """Bot that makes a random legal move"""

    def get_next_move(self, g: Game, state: State) -> Move:
        legal_moves: list[Move] = BotUtil.get_legal_moves(g, state, self.id)
        # print(f"... Legal moves: {legal_moves}")
        move = random.choice(legal_moves)
        return move

class AttackBot(Bot):
    """ Bot that always hits if it will erase an opponent's hand. """

    def get_next_move(self, g: Game, state: State):
        legal_moves = BotUtil.get_legal_moves(g, state, self.id)
        for move in legal_moves:
            # ignore splits
            if isinstance(move, Split):
                continue

            # determine opponent's starting number of alive hands
            before_opponent = BotUtil.get_opponent(state.players(), cast(Hit, move))
            before_alive_hands = len(before_opponent.get_alive_hands())

            # determine opponent's resulting number of alive hands
            scenario = Scenario(g, state, self.id, move)
            after_opponent = BotUtil.get_opponent(scenario.players(), cast(Hit, move))
            after_alive_hands = len(after_opponent.get_alive_hands())

            # see if they lost a hand
            if after_alive_hands < before_alive_hands:
                print("... Found strategy move")
                return move
        
        # no strategy-matching move found
        print("... No strategy move found, resorting to random.")
        return random.choice(legal_moves)

class DefendBot(Bot):
    """ Bot that always skips a move that could let the opponent erase one of it's hands. """

    def get_next_move(self, g: Game, state: State):
        results = BotUtil.simulate(g=g, state=state, current_player_id=self.id, starting_state=state, 
            starting_move=None, prior_move=None, optimizing_player_id=self.id, additional_rounds=2, current_round=1,
            exit_test=DefendBot._exit_test)

        if results:
            if results.success:
                print("... Found strategy move")
                return results.success
            elif results.neutral_moves:
                print("... Only neutral moves found, choosing one of them.")
                return random.choice(results.neutral_moves)

        print("... No safe moves found, resorting to random.")
        legal_moves = BotUtil.get_legal_moves(g, state, self.id)
        return random.choice(legal_moves)

    @staticmethod
    def _exit_test(scenario: Scenario, additional_rounds: int, current_round: int, 
        starting_state: State, optimizing_player_id: int) -> int:

        before_alive_hands = starting_state.player(optimizing_player_id).get_alive_hands()
        after_alive_hands = scenario.player(optimizing_player_id).get_alive_hands()
        if len(after_alive_hands) < len(before_alive_hands):
            BotUtil.print_r(f"... rejecting due to hands {scenario.player(optimizing_player_id).hands()}", current_round)
            return -1
        else:
            return 0
