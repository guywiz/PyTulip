# -*- coding:utf-8 -*-

from tulip import *
from SpaceFilling import *

class Peano(SpaceFilling):
    '''
    embeds nodes in a graph along a Hilbert curve
    '''
    def __init__(self, graph):
        super(Peano, self).__init__(graph)

    def setAxiom(self):
        return ['L']

    def rewrite(self, letter):
        '''
        implements the rewrite rules
        return a list of symbols L, R, F, +, -
        '''
        if letter in ['-', '+', 'F']:
            return letter
        elif letter == 'L':
            return list('LFRFL-F-RFLFR+F+LFRFL')
        else:
            return list('RFLFR+F+LFRFL-F-RFLFR')

def main(graph):
    curve = Peano(graph)
    n = curve.iteration_order()
    curve.process_sequence(graph["Contraceptive method used"])
    updateVisualization()
