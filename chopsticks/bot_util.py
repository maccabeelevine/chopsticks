from chopsticks.player import Move
import copy

class BotUtil:

    def get_legal_moves(g, player_id):
        """ Get all legal moves available right now """
        legal_moves = BotUtil._get_legal_hit_moves(g, player_id)
        legal_moves.extend(BotUtil._get_legal_split_moves(g, player_id))
        return legal_moves

    def _get_legal_hit_moves(g, player_id):
        """ Generate list of legal hit moves based on game state """
        legal_hit_moves = []

        # iterate through other players
        for opponent_id in range(1, g.num_players + 1):
            if not opponent_id == player_id:

                # iterate through any of my hands that are alive
                for my_hand in range(1, g.num_hands + 1):
                    if g.players[player_id - 1].hands[my_hand - 1].is_alive():

                        # iterate through opponent hands that are alive
                        for opponent_hand in range(1, g.num_hands + 1):
                            if g.players[opponent_id - 1].hands[opponent_hand - 1].is_alive():
                                move = (Move.HIT, opponent_id, my_hand, opponent_hand)
                                legal_hit_moves.append(move)

        return legal_hit_moves

    def _get_legal_split_moves(g, player_id):
        """ Generate list of legal split moves, based on current game state """
        player = g.players[player_id - 1]
        player_alive_fingers = player.get_alive_fingers()
        legal_split_moves = []
        # TODO remove hard-coded assumption about two hands, already in logic.py
        max_hand_fingers = min(player_alive_fingers, g.num_fingers - 1)
        for left_fingers in range(0, max_hand_fingers + 1):

            # if this move would actually change the game state
            if not left_fingers == player.hands[0].alive_fingers \
                    and not left_fingers == player.hands[1].alive_fingers:

                right_fingers = player_alive_fingers - left_fingers
                if not right_fingers > max_hand_fingers:
                    move = (Move.SPLIT, 1, 2, left_fingers, right_fingers)
                    legal_split_moves.append(move)

        return legal_split_moves

    def get_opponent(players, move):
        if move[0] == Move.SPLIT:
            return None
        
        opponent_player_id = move[1]
        return players[opponent_player_id - 1]


class Scenario():

    def __init__(self, g, player_id, move):
        self._initPlayers(g)
        self._initOpponents(player_id)
        g.logic.do_move(g, self.players, move, player_id-1)

    def _initPlayers(self, g):
        self.players = copy.deepcopy(g.players)

    def _initOpponents(self, player_id):
        self.opponents = []
        for player in self.players:
            if not player.id == player_id:
                self.opponents.append(player)
