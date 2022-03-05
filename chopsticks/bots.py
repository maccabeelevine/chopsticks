import random
from abc import ABC, abstractmethod

from chopsticks.player import Player, Move
from chopsticks.bot_util import BotUtil, Scenario

class Bot(Player):
    """Class for bot players"""

    @abstractmethod
    def get_next_move(self,g):
        pass

    def __repr__(self):
        return f"Bot({self.id})"

class RandomBot(Bot):
    """Bot that makes a random legal move"""

    def get_next_move(self, g):
        legal_moves = BotUtil.get_legal_moves(g, self.id)
        # print(f"Legal moves: {legal_moves}")
        move = random.choice(legal_moves)
        return move

    def __repr__(self):
      return f"RandomBot({self.id})"

class AttackBot(Bot):
    """ Bot that always hits if it will erase an opponent's hand. """

    def get_next_move(self, g):
        legal_moves = BotUtil.get_legal_moves(g, self.id)
        for move in legal_moves:
            # ignore splits
            if move[0] == Move.SPLIT:
                continue

            # determine opponent's starting number of alive hands
            before_opponent = BotUtil.get_opponent(g.players, move)
            before_alive_hands = len(before_opponent.get_alive_hands())

            # determine opponent's resulting number of alive hands
            scenario = Scenario(g, self.id, move)
            after_opponent = BotUtil.get_opponent(scenario.players, move)
            after_alive_hands = len(after_opponent.get_alive_hands())

            # see if they lost a hand
            if after_alive_hands < before_alive_hands:
                print("Found strategy move")
                return move
        
        # no strategy-matching move found
        print("No strategy move found, resorting to random.")
        return random.choice(legal_moves)

    def __repr__(self):
      return f"AtttackBot({self.id})"

