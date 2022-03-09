"""
Created on 6 Sep 2019

Authors: Luca Bianchi 
         Tom MacArthur
"""

from __future__ import annotations
from chopsticks.player import Human, Player, Hand
from chopsticks.move import Move, Hit, Split
from chopsticks.state import State
from abc import ABC, abstractmethod

class Ui(ABC):
    """Abstract Class for the user interface"""
    def __init__(self):
        pass

    @abstractmethod
    def display_game_state(self, state: State):
        pass

    @abstractmethod
    def get_user_input(self, player_id: int) -> Move|str|None:
        pass

class Gui(Ui):
    """Graphical user interface"""
    def display_game_state(self, state: State):
        pass

    def get_user_input(self, player_id: int) -> None:
        pass

class CommandLine(Ui):
    """For Printing to the console"""
    def __init__(self):
        pass
    
    def display_game_state(self, state: State):
        """Prints the number of fingers each player has"""
        str_list: list[str] = []
        player: Player
        for player in state.players():
            if isinstance(player, Human):
                str_list.append(f"Human {str(player.id)}: (")
            else:
                str_list.append(f"{player}: (")
            
            hand: Hand
            for hand in player.hands():
                str_list.append(" " + str(hand.alive_fingers) + " ")
                
            str_list.append(")   |   ")
        current_message = f"{state.get_current_player()}'s turn"
        print("\n" + ''.join(str_list) + current_message)
    
    def get_user_input(self, player_id: int) -> Move|str :
        """Gets the user input and returns the appropriate action or an error"""
        ui = input("Human " + str(player_id) + "'s turn: ")
        ui_list = ui.strip().lower().split()
        
        try:
            if ui_list[0] in [Hit.code, 'hit']:
                #Input: Hit, PLayerBeingHit, GivingHand, ReceivingHand
                return Hit(int(ui_list[1]), int(ui_list[2]), int(ui_list[3]))
            elif ui_list[0] in [Split.code,'split']:
                #Input: Split, Hand1, Hand2, Amount1, Amount2
                return Split(int(ui_list[1]), int(ui_list[2]), int(ui_list[3]), int(ui_list[4]))
            elif ui_list[0] == "help":
                return "help"
            else:
                print("Not a Valid Command")
                return "error"
        except:
            print("Not a Valid Command")
            return "error"