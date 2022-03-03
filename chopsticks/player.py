"""
Created on 6 Sep 2019

Authors: Luca Bianchi 
         Tom MacArthur
"""

from abc import ABC, abstractmethod

class Hand:
    """
    Class representing the hand of a player
    """
    def __init__(self, num_fingers):
        self.total_fingers = num_fingers
        self.alive_fingers = 1
        
    def remove_fingers(self, num_fingers):
        """Removes fingers from the hands"""
        if self.alive_fingers - num_fingers >= 0:
            self.alive_fingers = self.alive_fingers - num_fingers
            return True
    
    def add_fingers(self, move_type, num_fingers):
        """
        Adds alive fingers to the hand
        
        Parameters
        ----------
        move_type: string
            Either "h" or "s"
        num_fingers: int
            Number of fingers to add
        """
        if (move_type == "h" and self.alive_fingers == 0) or num_fingers == 0:
            return False

        self.alive_fingers = (self.alive_fingers + num_fingers) % self.total_fingers
        return True

    def is_alive(self):
        return self.alive_fingers

class Player(ABC):

    _next_player = 1

    def get_next_player():
        next = Player._next_player
        Player._next_player += 1
        return next

    """Abstract class for players in the game"""
    def __init__(self, num_hands, num_fingers):
        self.id = Player.get_next_player()
        self.hands = [Hand(num_fingers) for x in range(num_hands)]
    
    @abstractmethod
    def get_next_move(self,g):
        """Gets the next move"""
        pass

    def get_alive_fingers(self):
        alive_fingers = 0
        for hand in self.hands:
            alive_fingers += hand.alive_fingers
        return alive_fingers

    def is_alive(self):
        """Checks if the player is alive"""
        return self.get_alive_fingers()

class Human(Player):
    """Class for human players"""
    def get_next_move(self,g):
        """Gets the next move from the player"""
        #TODO Check if move is valid
        is_error = True
        while is_error:
            move = g.ui.get_user_input(g, self.id) 
            if move != "error" and move != "help":
                is_error = False         
        return move

    def __repr__(self):
        return f"Human({self.id})"
