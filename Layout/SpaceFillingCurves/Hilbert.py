# -*- coding:utf-8 -*-

from tulip import *
from SpaceFilling import *

class Hilbert(SpaceFilling):
    '''
    embeds nodes in a graph along a Hilbert curve
    '''
    def __init__(self, graph):
        super(Hilbert, self).__init__(graph)

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
            return list('-RF+LFL+FR-')
        else:
            return list('+LF-RFR-FL+')

def main(graph):
    hilb = Hilbert(graph)
    hilb.L_expression()
    hilb.process_sequence(graph['age'])
    updateVisualization()
