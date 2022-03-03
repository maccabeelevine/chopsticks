'''
Created on 6 Sep 2019

Authors: Luca Bianchi 
         Tom MacArthur

Description: Core functionality module for the Chopsticks game. Contains the game class
'''
from chopsticks.bots import RandomBot
from chopsticks.player import Human
from chopsticks.user_interface import CommandLine
import chopsticks.logic as logic


class Game:
    """
    Class for running one instance of a game

    Parameters
    ----------
    num_hands: int
        Number of hands that each player has
    num_fingers: int
        Number of fingers that each hand has
    player_types: str[]
        Array of player types.  See build_player().

    """
    def __init__(self, num_hands, num_fingers, player_types):
        self.num_players = len(player_types)
        self.num_hands = num_hands
        self.num_fingers = num_fingers
        self.game_is_over = False
        self.logic = logic.Logic()
        self.ui  = CommandLine()
        
        self.players = \
            [self.build_player(player_type, num_hands, num_fingers) for player_type in player_types]
        
        print(f"Players: {self.players}" +
              "\nHands per Player: ", self.num_hands, "\nFingers per hand: ", self.num_fingers , "\n")

    def build_player(self, player_type, num_hands, num_fingers):
        match player_type:
            case 'H':
                return Human(num_hands, num_fingers)
            case 'RB':
                return RandomBot(num_hands, num_fingers)
            case _:
                raise Exception(f"Unknown player type: {player_type}")
    
    def play(self):
        """Game Loop"""
        i = 0
        while self.game_is_over == False:
            if self.players[i].is_alive():
                self.ui.display_game_state(self)
                if isinstance(self.players[i], Human):
                    is_valid_move = False
                    while is_valid_move == False:
                        move = self.players[i].get_next_move(self)
                        is_valid_move = self.logic.do_move(self, move, i)
                        if is_valid_move == False:
                            print("Not A Valid Move")
                else:
                    move = self.players[i].get_next_move(self)
                    is_valid_move = self.logic.do_move(self, move, i)
                    if not is_valid_move:
                        raise Exception(f"Bot returned invalid move: {move}")
                    
            self.game_is_over = self.logic.check_if_game_over(self)
            i+=1
            if(i >= self.num_players):
                i=0
        print("Game Over")
    
if __name__ == '__main__':
    g = Game(2,0,2,5)
    g.play()

        
        
        
        
        
        
        
        
        
