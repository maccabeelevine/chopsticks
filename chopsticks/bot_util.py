class BotUtil:

    # _possible_moves = None

    def get_legal_moves(g, player_id):
        """ Get all legal moves available right now """
        legal_moves = BotUtil._get_legal_hit_moves(g, player_id)
        legal_moves.extend(BotUtil._get_legal_split_moves(g, player_id))
        return legal_moves

    def _get_legal_hit_moves(g, player_id):
        # TODO filter on actually legal
        return BotUtil._get_possible_hit_moves(g, player_id)

    def _get_possible_hit_moves(g, player_id):
        """ Generate list of possible hit moves based on initial setup, ignoring game state """
        possible_hit_moves = []

        # iterate through other players
        for opponent_id in range(1, g.num_players + 1):
            if not opponent_id == player_id:

                # iterate through my hands
                for my_hand in range(1, g.num_hands + 1):

                    # iterate through opponent hands
                    for opponent_hand in range(1, g.num_hands + 1):
                        move = ("h", opponent_id, my_hand, opponent_hand)
                        possible_hit_moves.append(move)

        return possible_hit_moves

    def _get_legal_split_moves(g, player_id):
        """ Generate list of legal split moves, based on current game state """
        player = g.players[player_id - 1]
        player_alive_fingers = player.get_alive_fingers()
        legal_split_moves = []
        # TODO remove hard-coded assumption about two hands, already in logic.py
        for left_fingers in range(0, player_alive_fingers + 1):

            # if this move would actually change the game state
            if not left_fingers == player.hands[0].alive_fingers \
                    and not left_fingers == player.hands[1].alive_fingers:

                right_fingers = player_alive_fingers - left_fingers
                move = ('s', 1, 2, left_fingers, right_fingers)
                legal_split_moves.append(move)

        return legal_split_moves
