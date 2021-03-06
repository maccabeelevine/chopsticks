from __future__ import annotations
from chopsticks.move import Move, Hit, Split

from typing import TYPE_CHECKING, cast, Callable
import random
from state import Scenario
if TYPE_CHECKING:
    from chopsticks.core import Game
    from chopsticks.state import State
    from chopsticks.player import Player, Hand


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
                my_hand_unique: set[int] = set()
                for my_hand in range(1, g.num_hands + 1):
                    if state.player(player_id).hand(my_hand).is_alive():
                        my_alive_fingers = state.player(player_id).hand(my_hand).alive_fingers
                        if my_alive_fingers in my_hand_unique:
                            # skip hand with duplicate number of fingers
                            continue
                        else:
                            my_hand_unique.add(my_alive_fingers)

                        # iterate through opponent hands that are alive
                        opponent_hand_unique: set[int] = set()
                        for opponent_hand in range(1, g.num_hands + 1):
                            if g.player(opponent_id).hand(opponent_hand).is_alive():
                                opponent_alive_fingers = state.player(opponent_id).hand(opponent_hand).alive_fingers
                                if opponent_alive_fingers in opponent_hand_unique:
                                    # skip opponent hand with duplicate number of fingers
                                    continue
                                else:
                                    opponent_hand_unique.add(opponent_alive_fingers)

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

                    # eliminate duplicate half of the legal splits
                    if not left_fingers < right_fingers:
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

    @staticmethod
    def simulate(g: Game, state: State, current_player_id: int, starting_state: State, 
        starting_move: Move|None,
        prior_move: Move|None, optimizing_player_id: int, additional_rounds: int, current_round: int,
        exit_test: Callable[[Scenario, int, int, State, State, int, Game], int]) -> SimulationResults|None:
        
        if not additional_rounds:
            BotUtil.print_r("no additional rounds on this tree", current_round)
            return None

        is_my_turn = current_player_id == optimizing_player_id
        legal_moves = BotUtil.get_legal_moves(g, state, current_player_id)
        results = BotUtil.SimulationResults()
        moves_to_recurse: dict[Move, Scenario] = {}
        for move in legal_moves:
            scenario = Scenario(g, state, current_player_id, move)
            BotUtil.print_r(f"consider move {move} leading to scenario {scenario}", current_round)
            test_result = exit_test(scenario, additional_rounds - 1, current_round, starting_state, 
                state, optimizing_player_id, g)

            # for a good test result
            if test_result > 0:
                if is_my_turn:
                    BotUtil.print_r("good result for me", current_round)
                    return results.record_success(starting_move if starting_move else move)
                else:
                    BotUtil.print_r("ignore good result for me on opponent's turn", current_round)
                    continue

            # for a bad test result
            elif test_result < 0:
                if is_my_turn:
                    BotUtil.print_r("ignore bad result for me on my turn", current_round)
                    continue
                else:
                    BotUtil.print_r("bad result for me on opponent's turn, kill tree", current_round)
                    return results.record_failure()

            # for a neutral test result, recurse
            else:
                BotUtil.print_r(f"found neutral move, so recurse later if needed", current_round)
                moves_to_recurse[move] = scenario
                results.add_naive_neutral_move(move)
                continue

        # did a breadth-first search at this level and did not return, 
        # so now recurse on the saved neutral moves in random order
        BotUtil.print_r(f"recurse on stored neutral moves", current_round)
        shuffled_moves = random.sample(moves_to_recurse.keys(), len(moves_to_recurse))
        for move in shuffled_moves:
            next_player_id = 1 if current_player_id == g.num_players else current_player_id + 1
            scenario = moves_to_recurse[move]
            BotUtil.print_r(f"recurse on move {move} leading to scenario {scenario}", current_round)
            recursion_results = BotUtil.simulate(g, scenario, next_player_id, starting_state, 
                starting_move if starting_move else move,
                move, optimizing_player_id, additional_rounds - 1, current_round + 1, exit_test)

            if recursion_results:
                if recursion_results.success:
                    BotUtil.print_r(f"returning recursive success {recursion_results.success}", current_round)
                    return recursion_results
                elif recursion_results.failure:
                    if is_my_turn:
                        continue
                    else:
                        BotUtil.print_r(f"returning recursive failure", current_round)
                        return recursion_results
                else:
                    BotUtil.print_r(f"recursion returned with only neutral moves, so add neutral move", current_round)
                    results.add_neutral_move(move)
                    continue

            else:
                BotUtil.print_r(f"returned from recursion with no results, so adding neutral move {move}", current_round)
                results.add_neutral_move(move)
                continue

        # considered all recursion moves and still no definitive move
        if is_my_turn:
            BotUtil.print_r(f"considered all moves, nothing found, returning neutral moves: {results.neutral_moves}", current_round)
            return results
        else:
            BotUtil.print_r("considered all opponent moves, nothing bad found", current_round)
            return None


    @staticmethod
    def print_r(message: str, depth: int):
        print("..." * depth + " " + message)

    @staticmethod
    def print_t(message: str):
        BotUtil.print_r(message, 2)

    class SimulationResults:

        def __init__(self):
            self.success = None
            self.neutral_moves: list[Move] = []
            self.naive_neutral_moves: list[Move] = []
            self.failure = False

        def record_success(self, success: Move) -> BotUtil.SimulationResults:
            self.success = success
            return self

        def record_failure(self):
            self.failure = True
            return self

        def add_neutral_move(self, neutral_move: Move):
            self.neutral_moves.append(neutral_move)

        # a "naive" neutral move appears neutral at the current depth, without recursion
        def add_naive_neutral_move(self, naive_neutral_move: Move):
            self.naive_neutral_moves.append(naive_neutral_move)

    @staticmethod
    def is_vulnerable(current_player_id: int, scenario: Scenario, g: Game):
        opponents = BotUtil.get_opponents(scenario.players(), current_player_id)
        for opponent in opponents:
            if BotUtil.has_vulnerable_hand(g, opponent, scenario.player(current_player_id)):
                return True
        return False

    @staticmethod
    def get_opponents(players: list[Player], player_id: int) -> list[Player]:
        opponents: list[Player] = []
        for player in players:
            if not player.id == player_id:
                opponents.append(player)
        return opponents

    @staticmethod
    def has_vulnerable_hand(g: Game, player_1: Player, player_2: Player):
        for player_1_hand in player_1.hands():
            for player_2_hand in player_2.hands():
                if player_1_hand.alive_fingers + player_2_hand.alive_fingers == g.num_fingers:
                    return True
        return False

    @staticmethod
    def is_vulnerable_hand(hand: Hand, current_player_id: int, scenario: Scenario, g: Game):
        opponents = BotUtil.get_opponents(scenario.players(), current_player_id)
        for opponent in opponents:
            for opponent_hand in opponent.hands():
                if hand.alive_fingers + opponent_hand.alive_fingers == g.num_fingers:
                    return True
        return False
