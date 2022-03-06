"""
Created on 6 Sep 2019

Authors: Luca Bianchi 
         Tom MacArthur
"""

from __future__ import annotations
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING, cast
if TYPE_CHECKING:
    from chopsticks.core import Game
    from chopsticks.move import Move
    from chopsticks.state import State


class Hand:
    """
    Class representing the hand of a player
    """
    def __init__(self, num_fingers: int):
        self.total_fingers = num_fingers
        self.alive_fingers = 1
        
    def remove_fingers(self, num_fingers: int):
        """Removes fingers from the hands"""
        if self.alive_fingers - num_fingers >= 0:
            self.alive_fingers = self.alive_fingers - num_fingers
            return True
    
    def add_fingers(self, num_fingers: int):
        """
        Adds alive fingers to the hand
        
        Parameters
        ----------
        num_fingers: int
            Number of fingers to add
        """
        self.alive_fingers = (self.alive_fingers + num_fingers) % self.total_fingers
        return True

    def is_alive(self):
        return self.alive_fingers

    def __repr__(self):
        return f"{self.alive_fingers}"

class Player(ABC):

    """Abstract class for players in the game"""
    def __init__(self, id: int, num_hands: int, num_fingers: int):
        self.id = id
        self._hands = [Hand(num_fingers) for _ in range(num_hands)]
    
    def hand(self, hand_id: int):
        return self._hands[hand_id - 1]

    def hands(self):
        return self._hands

    @abstractmethod
    def get_next_move(self, g: Game, state: State) -> Move:
        """Gets the next move"""
        pass

    def get_alive_hands(self):
        alive_hands: list[Hand] = []
        for hand in self._hands:
            if hand.is_alive():
                alive_hands.append(hand)
        return alive_hands

    def get_alive_fingers(self):
        alive_fingers = 0
        for hand in self._hands:
            alive_fingers += hand.alive_fingers
        return alive_fingers

    def is_alive(self):
        """Checks if the player is alive"""
        return self.get_alive_fingers()

class Human(Player):
    """Class for human players"""
    def get_next_move(self, g: Game, state: State) -> Move:
        """Gets the next move from the player"""
        #TODO Check if move is valid
        is_error = True
        move: Move|str|None = None
        while is_error:
            move = g.ui.get_user_input(self.id) 
            if move != "error" and move != "help":
                is_error = False         
        return cast(Move, move)

    def __repr__(self):
        return f"Human({self.id})"
