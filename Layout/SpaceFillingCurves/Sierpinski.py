# -*- coding:utf-8 -*-

from tulip import *
from SpaceFilling import *

class Sierpinski(SpaceFilling):
	'''
	embeds nodes in a graph along a Hilbert curve
	'''
	def __init__(self, graph):
		super(Sierpinski, self).__init__(graph)

	def setAxiom(self):
		return list('LF')

	def setAngle(self, angle):
		'''
		with Sierpinski, a + turn is math.pi/3 = 60 degrees
		'''
		return math.pi/3

	def rewrite(self, letter):
		'''
		implements the rewrite rules
		return a list of symbols L, R, F, +, -
		'''
		if letter in ['-', '+', 'F']:
			return letter
		elif letter == 'L':
			return list('RF+LF+R')
		else:
			return list('LF-RF-L')

def main(graph):
	curve = Sierpinski(graph)
	curve.L_expression()
	curve.process_sequence(graph['age'])
	updateVisualization()
