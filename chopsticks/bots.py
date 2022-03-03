import random
from abc import ABC, abstractmethod

from chopsticks.player import Player
from chopsticks.bot_util import BotUtil

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
        print(f"Legal moves: {legal_moves}")
        move = random.choice(legal_moves)
        print(f"Selected move: {move}")
        return move

    def __repr__(self):
      return f"RandomBot({self.id})"
