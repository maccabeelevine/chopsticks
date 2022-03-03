'''
Created on 6 Sep 2019

@author: Tom
'''

import core
import sys


def main():
    hands_per_player = int(sys.argv[1])
    fingers_per_hand = int(sys.argv[2])
    games_to_play = int(sys.argv[3])
    player_codes = sys.argv[4:] # Array of player type codes.  See Game.build_player.

    if games_to_play == 1:
        g = core.Game(hands_per_player, fingers_per_hand, player_codes)
        g.play()
    else:
        t = core.Tournament(hands_per_player, fingers_per_hand, games_to_play, player_codes)
        t.play()


if __name__ == '__main__':
    main()