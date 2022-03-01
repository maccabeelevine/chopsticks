'''
Created on 6 Sep 2019

@author: Tom
'''

import core
import sys


def main():
    g = core.Game(
        int(sys.argv[1]), 
        int(sys.argv[2]), 
        int(sys.argv[3]), 
        int(sys.argv[4]))
    g.play()


if __name__ == '__main__':
    main()