"""
Created on 6 Sep 2019

Authors: Luca Bianchi 
         Tom MacArthur

Description: Object which contains the game logic
"""

from __future__ import annotations
from chopsticks.move import Move, Hit, Split

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from chopsticks.core import Game
    from chopsticks.state import State
    from chopsticks.player import Player

class Logic:
    """
    Class for game logic
    """

    @staticmethod
    def do_move(g: Game, state: State, move: Move, player_id: int) -> bool:
        """ Performs the specified move by the specified player """
        is_valid_move = False
        if isinstance(move, Hit):
            is_valid_move = Logic.hit(g, state, player_id, move)
        elif isinstance(move, Split):
            is_valid_move = Logic.split(g, state, player_id, move)
        return is_valid_move
        
        
    @staticmethod
    def hit(g: Game, state: State, attack_player_id: int, hit: Hit):
        """
        hits a player's hand with the current player's hand and updates the Game object g
        
        Parameters
        ----------
        g: Game object
            reference to the game object
        state: State
            Game state list of players' hands
        attack_player_id: int
            Id of the attacking player

        Returns
        -------
        is_valid_move: bool
            True if the move is valid, otherwise false
        """
        
        #move validation
        if attack_player_id == hit.opponent_id:
            return False
        
        defending_hand = state.player(hit.opponent_id).hand(hit.opponent_hand)
        num_attacking_fingers = state.player(attack_player_id).hand(hit.my_hand).alive_fingers
        
        is_valid_move = defending_hand.add_fingers(num_attacking_fingers)
        
        return is_valid_move

    
    @staticmethod
    def split(g: Game, state: State, player_id: int, split: Split):
        """
        Splits the fingers between two hands and updates the Game object g
        
        Parameters
        ----------
        g: Game object
            reference to the game object
        state: State
            Game state list of players' hands
        player_id: int
            Id of the player
            
        Returns
        -------
        is_valid_move: bool
            True if the move is valid, otherwise false
        """

        
        if split.left_hand_id > g.num_hands:
            print('Select a hand')
            return False
        if split.right_hand_id > g.num_hands:
            print('Select a hand')
            return False
        
        left_hand_fingers = state.player(player_id).hand(split.left_hand_id).alive_fingers
        right_hand_fingers = state.player(player_id).hand(split.right_hand_id).alive_fingers
        
       
        if left_hand_fingers + right_hand_fingers == 1:
            print('Cannot split.')
            return False
        if left_hand_fingers == split.new_right_hand_fingers and right_hand_fingers == split.new_left_hand_fingers:
            print('This is the same hand set as before.')
            return False
        if left_hand_fingers + right_hand_fingers != split.new_left_hand_fingers + split.new_right_hand_fingers:
            print('Must equal same amount of fingers.')
            return False
        if split.new_left_hand_fingers >= g.num_fingers:
            print('Too many fingers on one hand.')
            return False
        if split.new_right_hand_fingers >= g.num_fingers:
            print('Too many fingers on one hand.')
            return False
        if split.new_left_hand_fingers < 0:
            print('Cannot have a negative')
            return False
        if split.new_right_hand_fingers < 0:
            print('Cannot have a negative')
            return False
        state.player(player_id).hand(split.left_hand_id).alive_fingers = split.new_left_hand_fingers
        state.player(player_id).hand(split.right_hand_id).alive_fingers = split.new_right_hand_fingers
        return True


    @staticmethod
    def check_if_game_over(state: State):
        """
        Check if the game is over
        
        Parameter
        ---------
        g: Game object
            reference to the game object

        Returns
        -------
        True if only one player is alive, otherwise false
        """
        alive_count = 0
        for player in state.players():
            if player.is_alive():
                alive_count += 1
        return alive_count < 2

    @staticmethod
    def get_winning_player(state: State) -> Player:
        if not Logic.check_if_game_over(state):
            raise Exception("No winning player yet, the game is still going on.")
        for player in state.players():
            if player.is_alive():
                return player
        raise Exception("Game is over, but none of the players are alive.")
    