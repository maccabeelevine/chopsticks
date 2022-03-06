class Move:
    pass    

class Hit(Move):

    code = 'h'

    def __init__(self, opponent_id: int, my_hand: int, opponent_hand: int):
        self.opponent_id = opponent_id
        self.my_hand = my_hand
        self.opponent_hand = opponent_hand

    def __repr__(self):
        return f"( '{Hit.code}' {self.opponent_id} {self.my_hand} {self.opponent_hand} )"

class Split(Move):

    code = 's'

    def __init__(self, left_hand_id: int, right_hand_id: int, new_left_hand_fingers: int, new_right_hand_fingers: int):
        self.left_hand_id = left_hand_id
        self.right_hand_id = right_hand_id
        self.new_left_hand_fingers = new_left_hand_fingers
        self.new_right_hand_fingers = new_right_hand_fingers

    def __repr__(self):
        return f"( '{Split.code}' {self.left_hand_id} {self.right_hand_id} {self.new_left_hand_fingers} {self.new_right_hand_fingers} )"
