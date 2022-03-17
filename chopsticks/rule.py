from __future__ import annotations
from abc import abstractmethod
import re

from typing import TYPE_CHECKING, cast
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
    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int) -> int:
        return 0

class DontSplitIfThenAHandIsVulnerable(Rule):
    """ Don't split because value of each hand after splitting is vulnerable to being zeroed by one of opponent's hands. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if not isinstance(move, Split):
            return 0

        if BotUtil.is_vulnerable(current_player_id, scenario, g):
            return self.weight
        return 0

class HitIfItEndsTheGame(Rule):
    """ Hit if it ends the game"""

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if not isinstance(move, Hit):
            return 0

        opponent = BotUtil.get_opponent(scenario.players(), move)
        if not opponent.get_alive_fingers():
            return self.weight
        else:
            return 0

class DontLeaveOneHandAndVulnerable(Rule):
    """ Don't leave me with one hand, and it's vulnerable """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        current_player = scenario.player(current_player_id)

        if len(current_player.get_alive_hands()) > 1:
            return 0

        if BotUtil.is_vulnerable(current_player_id, scenario, g):
            return self.weight
        return 0

class DontLeaveAnyHandVulnerable(Rule):
    """ Don't do any move if it leaves a hand vulnerable to being zeroed by one of opponent's hands. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if BotUtil.is_vulnerable(current_player_id, scenario, g):
            return self.weight
        return 0

class DontSplitToVulnerableAndOne(Rule):
    """ Don't split to each hand either having one finger or being being vulnerable. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if not isinstance(move, Split):
            return 0

        hands = scenario.get_current_player().hands()
        for hand in hands:
            if hand.alive_fingers > 1 and not BotUtil.is_vulnerable_hand(hand, current_player_id, scenario, g):
                return 0
        return self.weight

class If2DontHitToVulnerable(Rule):
    """ If my total fingers are two, don't hit in a way that makes a hand vulnerable. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if not prior_state.get_current_player().get_alive_fingers() == 2:
            return 0

        if not isinstance(move, Hit):
            return 0

        if BotUtil.is_vulnerable(current_player_id, scenario, g):
            return self.weight
        return 0

class IfOneHandHasZeroHitsAreBad(Rule):
    """ If one of my hands has zero fingers, then hit moves are bad because I'd still have zero fingers. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if isinstance(move, Split):
            return 0

        if len(prior_state.get_current_player().get_alive_hands()) < g.num_hands:
            return self.weight
        
        return 0

class DontSplitAndLeaveOneHandZero(Rule):
    """ Don't split and leave one hand with zero fingers. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if isinstance(move, Hit):
            return 0

        if len(scenario.get_current_player().get_alive_hands()) < g.num_hands:
            return self.weight

        return 0
        
class DontLeaveFewerTotalFingersThanOpponent(Rule):
    """ Don't leave myself with fewer fingers than any opponent. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        total_fingers = scenario.get_current_player().get_alive_fingers()

        for opponent in BotUtil.get_opponents(scenario.players(), current_player_id):
            if opponent.get_alive_fingers() > total_fingers:
                return self.weight

        return 0

class HitIfItEliminatesAHand(Rule):
    """ Hit an opponent's hand if it eliminates it. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if isinstance(move, Split):
            return 0
        hit = cast(Hit, move)
        opponent_id = hit.opponent_id
        opponent_hand_id = hit.opponent_hand
        if prior_state.player(opponent_id).hand(opponent_hand_id).is_alive() and \
            not scenario.player(opponent_id).hand(opponent_hand_id).is_alive():
            return self.weight
        return 0

class HitIfOpponentHasOneFingerAndIHaveMore(Rule):
    """ Hit if it leaves the opponent with one total finger, and me with more. """

    def test(self, g: Game, move: Move, scenario: Scenario, prior_state: State, current_player_id: int):
        if isinstance(move, Split):
            return 0

        opponent_id = cast(Hit, move).opponent_id
        if scenario.player(opponent_id).get_alive_fingers() == 1 and \
            scenario.get_current_player().get_alive_fingers() > 1:
            return self.weight

        return 0
