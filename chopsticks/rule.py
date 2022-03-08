from __future__ import annotations
from abc import abstractmethod
import re

from typing import TYPE_CHECKING
from chopsticks.move import Hit, Move, Split
from chopsticks.state import Scenario, State
from chopsticks.bot_util import BotUtil
if TYPE_CHECKING:
    from chopsticks.core import Game

class Rule:

    def __init__(self, weight: int, name: str|None = None):
        self.weight = weight
        if name:
            self.name = f"\"{name}\""
        else:
            self.name = self._from_camel_case(self.__class__.__name__)

    def _from_camel_case(self, name: str):
        return re.sub("([A-Z])", " \\1", name).strip()

    def __repr__(self):
        return self.name

    @abstractmethod
    def test(self, g: Game, move: Move, state: State, current_player_id: int) -> int:
        return 0

class DontSplitIfThenAHandIsVulnerable(Rule):
    """ Don't split because value of each hand after splitting is vulnerable to being zeroed by one of opponent's hands. """

    def test(self, g: Game, move: Move, state: State, current_player_id: int):
        if not isinstance(move, Split):
            return 0

        scenario = Scenario(g, state, current_player_id, move)
        opponents = BotUtil.get_opponents(scenario.players(), current_player_id)
        for opponent in opponents:
            if BotUtil.has_vulnerable_hand(g, opponent, scenario.player(current_player_id)):
                return self.weight
        return 0

class HitIfItEndsTheGame(Rule):
    """ Hit if it ends the game"""

    def test(self, g: Game, move: Move, state: State, current_player_id: int):
        if not isinstance(move, Hit):
            return 0

        scenario = Scenario(g, state, current_player_id, move)
        opponent = BotUtil.get_opponent(scenario.players(), move)
        if not opponent.get_alive_fingers:
            return self.weight
        else:
            return 0

class DontLeaveOneHandAndVulnerable(Rule):
    """ Don't leave me with one hand, and it's vulnerable """

    def test(self, g: Game, move: Move, state: State, current_player_id: int):
        scenario = Scenario(g, state, current_player_id, move)
        current_player = scenario.player(current_player_id)

        if len(current_player.get_alive_hands()) > 1:
            return 0

        opponents = BotUtil.get_opponents(scenario.players(), current_player_id)
        for opponent in opponents:
            if BotUtil.has_vulnerable_hand(g, opponent, scenario.player(current_player_id)):
                return self.weight
        return 0
