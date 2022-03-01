'''
Created on 6 Sep 2019

@author: Tom
'''

import core
import sys


def main():
    g = core.Game(
        int(sys.argv[1]), # Hands per Player
        int(sys.argv[2]), # Fingers per Hand
        sys.argv[3:]) # Array of Player Codes: [H]uman, [R]andom bot
    g.play()


if __name__ == '__main__':
    main()