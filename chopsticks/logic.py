class Logic:

    def hit(self, attack_player_id, defend_player_id, recieving_hand, giving_hand):
        """hits a player's hand with the current player's hand"""
        
        if attack_player_id == defend_player_id and giving_hand == recieving_hand:
            return False
        
        is_valid_move = self.players[defend_player_id].hands[recieving_hand].add_fingers("h",self.players[attack_player_id].hands[giving_hand].alive_fingers)
        
        return is_valid_move

    
    def split(self, player_id, hand_1, hand_2, amount_1, amount_2):
        """Splits the fingers between two hands"""

        
        if hand_1 >self.num_hands - 1:
            print('Select a hand')
            return False
        if hand_2 >self.num_hands - 1:
            print('Select a hand')
            return False
        
        hand_1_fingers = self.players[player_id].hands[hand_1].alive_fingers
        hand_2_fingers = self.players[player_id].hands[hand_2].alive_fingers
        
       
        if hand_1_fingers + hand_2_fingers == 1:
            print('Cannot split.')
            return False
        if hand_1_fingers == 1 and hand_2_fingers == 1:
            print('Must have more than one finger to split.')
            return False
        if hand_1_fingers == amount_2 and hand_2_fingers == amount_1:
            print('This is the same hand set as before.')
            return False
        if amount_1 == 0:
            print('Cannot destroy hand this way.')
            return False
        if amount_2 == 0:
            print('Cannot destroy hand this way.')
            return False
        if hand_1_fingers + hand_2_fingers != amount_1 + amount_2:
            print('Must equal same amount of fingers.')
            return False
        if amount_1 >= self.num_fingers:
            print('Too many fingers on one hand.')
            return False
        if amount_2 >= self.num_fingers:
            print('Too many fingers on one hand.')
            return False
        if amount_1 <=0:
            print('Cannot have a negative')
            return False
        if amount_2 <=0:
            print('Cannot have a negative')
            return False
        if hand_1 == -1:
            print('Select a hand.')
            return False
        if hand_2 == -1:
            print('Select a hand.')
            return False
        if player_id >= self.num_players:
            print('Select someone who is playing.')
            return False
        if player_id < 0:
            print('Select somone who is playing')
            return False
        else: 
            self.players[player_id].hands[hand_1].alive_fingers = amount_1
            self.players[player_id].hands[hand_2].alive_fingers = amount_2
            return True


    
    
    def check_if_game_over(self):
        """Check if the game is over"""
        alive_count = 0
        for player in self.players:
            if player.is_alive == True:
                alive_count += 1
            if alive_count > 1:
                return False
        return True
    