'''
Created on 6 Sep 2019

Authors: Luca Bianchi 
         Tom MacArthur

Description: Core functionality module for the Chopsticks game. Contains the game class
'''
from __future__ import annotations
from chopsticks.bots import RandomBot, AttackNowBot, AttackBot, DefendBot, AttackDefendBot, ThetaBot
from chopsticks.user_interface import CommandLine
from chopsticks.state import State
import chopsticks.logic as logic
from chopsticks.player import Human, Player
from chopsticks.move import Move
import random
from typing import cast

STALEMATE_COUNT = 3

STARTING_HANDS: list[list[int]]|None = None
# Example:
# STARTING_HANDS: list[list[int]]|None = [
#     [1, 1], [0, 3]
# ]

class Game:
    """
    Class for running one instance of a game

    Parameters
    ----------
    num_hands: int
        Number of hands that each player has
    num_fingers: int
        Number of fingers that each hand has
    player_types: List[str]
        Array of player types.  See build_player().

    """
    def __init__(self, num_hands: int, num_fingers: int, player_types: list[str]):
        if num_hands > 9 or num_fingers > 9:
            # due to State hashing function
            raise Exception("num_hands and num_fingers must be single digits")

        self.num_players = len(player_types)
        self.num_hands = num_hands
        self.num_fingers = num_fingers
        self.game_is_over = False
        self.logic = logic.Logic()
        self.ui  = CommandLine()
        self.prior_states: dict[int, int] = {}
        self.rounds_played = 0
        self.last_move = None
        
        self.state = State(
            [self.build_player(index + 1, player_type, num_hands, num_fingers) 
                for index, player_type in enumerate(player_types)])
        
        if STARTING_HANDS:
            for player_index, player in enumerate(self.state.players()):
                player_starting_hands = STARTING_HANDS[player_index]
                for hand_index, hand in enumerate(player.hands()):
                    hand.alive_fingers = player_starting_hands[hand_index]
        
        print(f"Players: {self.state.players()}" +
              "\nHands per Player: ", self.num_hands, "\nFingers per hand: ", self.num_fingers , "\n")

    def build_player(self, player_id: int, player_type: str, num_hands: int, num_fingers: int):
        match player_type:
            case 'H':
                return Human(player_id, num_hands, num_fingers)
            case 'RB':
                return RandomBot(player_id, num_hands, num_fingers)
            case 'ANB':
                return AttackNowBot(player_id, num_hands, num_fingers)
            case 'AB':
                return AttackBot(player_id, num_hands, num_fingers, 5)
            case 'DB':
                return DefendBot(player_id, num_hands, num_fingers, 2)
            case 'ADB':
                return AttackDefendBot(player_id, num_hands, num_fingers, 10)
            case 'TB':
                return ThetaBot(player_id, num_hands, num_fingers)
            case _:
                raise Exception(f"Unknown player type: {player_type}")
    
    def player(self, player_id: int):
        return self.state.player(player_id)

    def play(self):
        """Game Loop"""
        i = random.randint(1, self.num_players)
        print(f"Starting Player is {self.player(i)}")
        while self.game_is_over == False:
            if self.player(i).is_alive():
                self.state.set_current_player(i)
                self.ui.display_game_state(self.state)
                if self.test_stalemate(self.state):
                    break
                if isinstance(self.player(i), Human):
                    is_valid_move = False
                    while is_valid_move == False:
                        move: Move = self.player(i).get_next_move(self, self.state)
                        is_valid_move = self.logic.do_move(self, self.state, move, i)
                        if is_valid_move == False:
                            print("Not A Valid Move")
                else:
                    move = self.player(i).get_next_move(self, self.state)    
                    print(f"... {self.player(i)} selected move: {move}")
                    is_valid_move = self.logic.do_move(self, self.state, move, i)
                    if not is_valid_move:
                        raise Exception(f"Bot returned invalid move: {move}")
                    
            self.rounds_played += 1
            self.game_is_over = self.logic.check_if_game_over(self.state)
            i+=1
            if(i > self.num_players):
                i=1
        
        if self.logic.check_if_game_over(self.state):
            print(f"Game Over after {self.rounds_played} rounds played.  " \
                f"The winner is {self.logic.get_winning_player(self.state)}!\n\n")
        else:
            print(f"Game Over after {self.rounds_played} rounds played due to stalemate.\n\n")

    def play_async(self, move: Move|None):
        i = self.state.get_current_player().id
        if not self.game_is_over:
            if self.player(i).is_alive():
                self.state.set_current_player(i)
                if self.test_stalemate(self.state):
                    return "stalemate"
                if isinstance(self.player(i), Human):
                    move = cast(Move, move)
                    is_valid_move = self.logic.do_move(self, self.state, move, i)
                    if is_valid_move == False:
                        return "Not A Valid Move"
                else:
                    move = self.player(i).get_next_move(self, self.state)    
                    print(f"... {self.player(i)} selected move: {move}")
                    is_valid_move = self.logic.do_move(self, self.state, move, i)
                    if not is_valid_move:
                        raise Exception(f"Bot returned invalid move: {move}")
                    
            self.rounds_played += 1
            self.game_is_over = self.logic.check_if_game_over(self.state)
            i+=1
            if(i > self.num_players):
                i=1
            self.last_move = move
            self.state.set_current_player(i)
        
        if self.logic.check_if_game_over(self.state):
            return(f"Game Over after {self.rounds_played} rounds played.  " \
                f"The winner is {self.logic.get_winning_player(self.state)}!\n\n")
        else:
            return(f"Game Over after {self.rounds_played} rounds played due to stalemate.\n\n")
    

    def test_stalemate(self, state: State):
        if not state.key() in self.prior_states:
            count = 1
        else:
            count = self.prior_states[state.key()] + 1
        self.prior_states[state.key()] = count
        if count == STALEMATE_COUNT:
            print(f"Found the same state {count} times, declaring a stalemate")
            return True
        if count + 1 == STALEMATE_COUNT:
            print("Warning, one more time at this state will be a stalemate")
        return False


class Tournament:
    """ A series of games with the same players """

    def __init__(self, num_hands: int, num_fingers: int, num_games: int, player_types: list[str]):
        self.num_hands = num_hands
        self.num_fingers = num_fingers
        self.num_games = num_games
        self.player_types = player_types
        self.winners: dict[int, int] = {}
        self.stalemates = 0
        self.total_rounds_played = 0

    def play(self):
        print(f"Starting a {self.num_games}-game tournament.")
        for game_number in range(self.num_games):
            print(f"Starting Game #{game_number + 1} of {self.num_games}.")
            g = Game(self.num_hands, self.num_fingers, self.player_types)
            g.play()
            self.record_win(g.logic.get_winning_player(g.state))
            self.total_rounds_played += g.rounds_played
            print("-----------------------------------------------\n\n")
        self.print_results()

    def record_win(self, player: Player|None):
        if player:
            if player.id not in self.winners:
                self.winners[player.id] = 0
            wins = self.winners[player.id]
            wins += 1
            self.winners[player.id] = wins
        else:
            self.stalemates += 1

    def print_results(self):
        def get_key(pair: tuple[int, int]):
            return pair[0]
        for player_id, wins in sorted(self.winners.items(), key = get_key):
            print(f"Player {player_id} won {wins} games.")
        print(f"{self.stalemates} games ended in stalemate.")
        print("Any other players did not win any games.")
        print(f"Games lasted for an average of {(self.total_rounds_played / self.num_games):.1f} rounds.")


if __name__ == '__main__':
    g = Game(2, 5, ['H', 'H'])
    g.play()
