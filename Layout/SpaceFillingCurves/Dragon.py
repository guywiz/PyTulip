# -*- coding:utf-8 -*-

from tulip import *
from SpaceFilling import *

class Dragon(SpaceFilling):
    '''
    embeds nodes in a graph along a Hilbert curve
    '''
    def __init__(self, graph):
        super(Dragon, self).__init__(graph)

    def setAxiom(self):
        return ['F', 'L']

    def rewrite(self, letter):
        '''
        implements the rewrite rules
        return a list of symbols L, R, F, +, -
        '''
        if letter in ['-', '+', 'F']:
            return letter
        elif letter == 'L':
            return list('L+RF+')
        else:
            return list('-FL-R')

def main(graph):
    curve = Dragon(graph)
    curve.L_expression()
    curve.process_sequence(graph['id'])
    updateVisualization()
