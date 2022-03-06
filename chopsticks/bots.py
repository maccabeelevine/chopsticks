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
        starting_state: State, prior_state: State|None, optimizing_player_id: int) -> int:
        return cast(int, None)

class AttackBot(RecurseBot):
    """ Bot that always hits if it will erase an opponent's hand within x moves. """

    def exit_test(self, scenario: Scenario, additional_rounds: int, current_round: int, 
        starting_state: State, prior_state: State|None, optimizing_player_id: int) -> int:

        if not scenario.player_id == optimizing_player_id:
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
        starting_state: State, prior_state: State|None, optimizing_player_id: int) -> int:

        prior_state = prior_state if prior_state else starting_state 
        before_alive_hands = prior_state.player(optimizing_player_id).get_alive_hands()
        after_alive_hands = scenario.player(optimizing_player_id).get_alive_hands()
        if len(after_alive_hands) < len(before_alive_hands):
            BotUtil.print_r(f"... rejecting due to hands {scenario.player(optimizing_player_id).hands()}", current_round)
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
        starting_state: State, prior_state: State|None, optimizing_player_id: int) -> int:

        # try attack test first.  if it doesn't succeed, use defend test.
        attack_result = self.attack_bot.exit_test(scenario, additional_rounds, current_round, 
            starting_state, prior_state, optimizing_player_id)
        if attack_result:
            return attack_result
        else:
            return self.defend_bot.exit_test(scenario, additional_rounds, current_round, 
            starting_state, prior_state, optimizing_player_id)