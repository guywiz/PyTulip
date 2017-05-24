# -*- coding:utf-8 -*-

from tulip import *
from SpaceFilling import *

class Moore(SpaceFilling):
	'''
	embeds nodes in a graph along a Hilbert curve
	'''
	def __init__(self, graph):
		super(Moore, self).__init__(graph)

	def setAxiom(self):
		return list('LFL+F+LFL')

	def rewrite(self, letter):
		'''
		implements the rewrite rules
		return a list of symbols L, R, F, +, -
		'''
		if letter in ['-', '+', 'F']:
			return letter
		elif letter == 'L':
			return list('−RF+LFL+FR−')
		else:
			return list('+LF−RFR−FL+')

def main(graph):
	curve = Moore(graph)
	curve.L_expression()
	curve.process_sequence(graph["Contraceptive method used"])
	updateVisualization()
