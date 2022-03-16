from __future__ import annotations

import random
from abc import abstractmethod

from chopsticks.player import Player
from chopsticks.move import Split
from chopsticks.bot_util import BotUtil
from chopsticks.state import Scenario
from chopsticks.move import Hit
from chopsticks.rule import *

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

class AttackNowBot(Bot):
    """ Bot that always hits if it will erase an opponent's hand right now. """

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

class RecurseBot(Bot):
    """ Abstract class that recurses to get the next move """

    def __init__(self, id: int, num_hands: int, num_fingers: int, rounds: int):
        super().__init__(id, num_hands, num_fingers)
        self.rounds = rounds

    def get_next_move(self, g: Game, state: State):
        results = BotUtil.simulate(g=g, state=state, current_player_id=self.id, starting_state=state, 
            starting_move=None, prior_move=None, optimizing_player_id=self.id, additional_rounds=self.rounds, 
            current_round=1, exit_test=self.exit_test)

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

    @abstractmethod
    def exit_test(self, scenario: Scenario, additional_rounds: int, current_round: int, 
        starting_state: State, prior_state: State|None, optimizing_player_id: int, g: Game) -> int:
        return cast(int, None)

class AttackBot(RecurseBot):
    """ Bot that always hits if it will erase an opponent's hand within x moves. """

    def exit_test(self, scenario: Scenario, additional_rounds: int, current_round: int, 
        starting_state: State, prior_state: State|None, optimizing_player_id: int, g: Game) -> int:

        if not scenario.get_current_player().id == optimizing_player_id:
            return 0

        if isinstance(scenario.move, Split):
            return 0

        prior_state = prior_state if prior_state else starting_state 

        # determine opponent's starting number of alive hands
        before_opponent = BotUtil.get_opponent(prior_state.players(), cast(Hit, scenario.move))
        before_alive_hands = len(before_opponent.get_alive_hands())

        # determine opponent's resulting number of alive hands
        after_opponent = BotUtil.get_opponent(scenario.players(), cast(Hit, scenario.move))
        after_alive_hands = len(after_opponent.get_alive_hands())

        # see if they lost a hand
        if after_alive_hands < before_alive_hands:
            BotUtil.print_r("... Found strategy move", current_round)
            return 1
        else:
            return 0

class DefendBot(RecurseBot):
    """ Bot that always skips a move that could let the opponent erase one of it's hands within x moves. """

    def exit_test(self, scenario: Scenario, additional_rounds: int, current_round: int, 
        starting_state: State, prior_state: State|None, optimizing_player_id: int, g: Game) -> int:

        prior_state = prior_state if prior_state else starting_state 
        before_alive_hands = prior_state.player(optimizing_player_id).get_alive_hands()
        after_alive_hands = scenario.player(optimizing_player_id).get_alive_hands()
        if len(after_alive_hands) < len(before_alive_hands):
            BotUtil.print_r(f"... rejecting due to hands {scenario.player(optimizing_player_id).hands()}", current_round)
            return -1
        elif BotUtil.is_vulnerable(optimizing_player_id, scenario, g):
            return -1
        else:
            return 0

class AttackDefendBot(RecurseBot):
    """ Bot that combines AttackBot and DefendBot strategies. """

    def __init__(self, id: int, num_hands: int, num_fingers: int, rounds: int):
        super().__init__(id=id, num_hands=num_hands, num_fingers=num_fingers, rounds=rounds)
        self.attack_bot = AttackBot(id=id, num_hands=num_hands, num_fingers=num_fingers, rounds=rounds)
        self.defend_bot = DefendBot(id=id, num_hands=num_hands, num_fingers=num_fingers, rounds=rounds)

    def exit_test(self, scenario: Scenario, additional_rounds: int, current_round: int, 
        starting_state: State, prior_state: State|None, optimizing_player_id: int, g: Game) -> int:

        # prioritize defend over attack
        defend_result = self.defend_bot.exit_test(scenario, additional_rounds, current_round, 
            starting_state, prior_state, optimizing_player_id, g)
        if defend_result:
            return defend_result
        else:
            return self.attack_bot.exit_test(scenario, additional_rounds, current_round, 
            starting_state, prior_state, optimizing_player_id, g)


class RulesBot(Bot):
    """ Bot that follows a set of rules. """

    def __init__(self, id: int, num_hands: int, num_fingers: int):
        super().__init__(id, num_hands, num_fingers)

        self.next_low_score = -100
        self.next_high_score = 100
        self.rules: list[Rule] = []

    def get_next_move(self, g: Game, state: State):
        legal_moves = BotUtil.get_legal_moves(g, state, self.id)
        good_moves: dict[Move, int] = {}
        bad_moves: dict[Move, int] = {}
        neutral_moves: list[Move] = []
        for move in legal_moves:
            scenario = Scenario(g, state, self.id, move)
            print(f"testing move {move} resulting in scenario {scenario}")
            found_matching_rule = False
            for rule in self.rules:
                print(f"... on rule {rule}")
                score: int = rule.test(g, move, scenario, state, self.id)
                if score > 0:
                    good_moves[move] = score
                    found_matching_rule = True
                    BotUtil.print_t(f"Found good score {score} on rule {rule}")
                    break
                elif score < 0:
                    bad_moves[move] = score
                    found_matching_rule = True
                    BotUtil.print_t(f"Found bad score {score} on rule {rule}")
                    break
                else:
                    # rule doesn't match this move
                    pass
            if not found_matching_rule:
                neutral_moves.append(move)
                print(f"... No match, neutral score")
        if len(good_moves):
            print(f"returning good move with highest score from {good_moves}")
            return self.get_highest_score(good_moves)
        elif len(neutral_moves):
            print(f"returning neutral move from {neutral_moves}")
            return random.choice(neutral_moves)
        else:
            print(f"returning bad move with highest score from {bad_moves}")
            return self.get_highest_score(bad_moves)

    def get_highest_score(self, moves: dict[Move, int]) -> Move:
        highest_score = None
        highest_score_move = None
        for move in moves.keys():
            score = moves[move]
            if not highest_score or score > highest_score:
                highest_score = score
                highest_score_move = move
        return cast(Move, highest_score_move)

    def get_next_low_score(self):
        score = self.next_low_score
        self.next_low_score += 1
        return score

    def get_next_high_score(self):
        score = self.next_high_score
        self.next_high_score -= 1
        return score

class ThetaBot(RulesBot):

    def __init__(self, id: int, num_hands: int, num_fingers: int):
        super().__init__(id, num_hands, num_fingers)

        self.rules.append(HitIfItEndsTheGame(self.get_next_high_score()))
        self.rules.append(DontLeaveOneHandAndVulnerable(self.get_next_low_score()))
        self.rules.append(DontSplitIfThenAHandIsVulnerable(self.get_next_low_score()))
        self.rules.append(DontLeaveAnyHandVulnerable(self.get_next_low_score()))
        self.rules.append(DontSplitToVulnerableAndOne(self.get_next_low_score()))
        self.rules.append(If2DontHitToVulnerable(self.get_next_low_score()))
        self.rules.append(IfOneHandHasZeroHitsAreBad(self.get_next_low_score()))
