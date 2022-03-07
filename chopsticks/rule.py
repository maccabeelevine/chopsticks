from __future__ import annotations
from abc import abstractmethod

from typing import TYPE_CHECKING
from chopsticks.move import Move, Split
from chopsticks.state import Scenario, State
from chopsticks.bot_util import BotUtil
if TYPE_CHECKING:
    from chopsticks.core import Game

class Rule:

    def __init__(self, weight: int, name: str):
        self.weight = weight
        self.name = f"\"{name}\""

    def __repr__(self):
        return self.name

    @abstractmethod
    def test(self, g: Game, move: Move, state: State, current_player_id: int) -> int:
        return 0

class DontSplitIfResultHandIsVulnerable(Rule):
    """ Don't split because value of each hand after splitting is vulnerable to being zeroed by one of opponent's hands. """

    def __init__(self, weight: int):
        super().__init__(weight, "Don't split if one of the hands will then be vulnerable.")

    def test(self, g: Game, move: Move, state: State, current_player_id: int):

        if not isinstance(move, Split):
            print("... not a split")
            return 0

        scenario = Scenario(g, state, current_player_id, move)
        opponents = BotUtil.get_opponents(scenario.players(), current_player_id)
        for opponent in opponents:
            if BotUtil.has_vulnerable_hand(g, opponent, scenario.player(current_player_id)):
                print(f"... found vulnerable hand, returning weight {self.weight}")
                return self.weight
        print(f"no vulnerable hand")
        return 0
