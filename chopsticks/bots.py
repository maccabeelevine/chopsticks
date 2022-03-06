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

    def __repr__(self):
        return f"Bot({self.id})"

class RandomBot(Bot):
    """Bot that makes a random legal move"""

    def get_next_move(self, g: Game, state: State) -> Move:
        legal_moves: list[Move] = BotUtil.get_legal_moves(g, state, self.id)
        # print(f"... Legal moves: {legal_moves}")
        move = random.choice(legal_moves)
        return move

    def __repr__(self):
      return f"RandomBot({self.id})"

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

    def __repr__(self):
      return f"AtttackBot({self.id})"

