# -*- coding:utf-8 -*-

from tulip import *
import math

class SpaceFilling(object):
	'''
	embeds nodes in a graph along a Space Filling curve

	N.B.
	the alphabet used MUST BE {L, R, +, -, F}
	this implementation works for curves using pi/2 or -pi/2
	'''
	def __init__(self, graph):
		super(SpaceFilling, self).__init__()
		self.graph = graph
		self.direction_vector = tlp.Vec3f(1, 0, 0)
		self.current_coord = tlp.Coord(0,0,0)
		self.sequence = self.setAxiom()
		self.angle = self.setAngle(math.pi/2)

	def setAxiom(self):
		'''
		sets the axiom for a specific L-system
		must be overidden by subclasses
		'''
		return ['L']

	def setAngle(self, angle):
		'''
		defines the angle for + turns
		a - sign then corresponds to a -angle turn
		angle should be given as a fraction of pi (or 2pi)

		N.B. the only example requiring this is the Sierpinski
		curve for which a turn is math.pi/3 = 60 degrees,
		otherwise all curve use the default math.pi/2 value
		'''
		return angle

	def rewrite(self, letter):
		'''
		implements the rewrite rules
		return a list of symbols L, R, F, +, -

		must be overidden by subclasses
		'''
		return [letter]

	def iteration_order(self):
		'''
		computes the order up to which the sequence must be
		rewritten in order to have enough points on the curve
		to fit all nodes in the graph

		makes the assumption that the number of L, R symbols in all rules
		is the same		'''
		n = 0
		p = 1
		nb_LR = len(filter(lambda x: x=='L' or x=='R', self.rewrite('L')))
		while self.graph.numberOfNodes() > p:
			n += 1
			p *= nb_LR
		return n

	def flatten(self, nested_list):
		return [x for sublist in nested_list for x in sublist]

	def L_expression(self):
		'''
		applies the rewrite rule to self.sequence
		maps rewrite rules on each letter
		concatenates the result into a single list
		'''
		for i in range(self.iteration_order()):
			self.sequence = self.flatten(map(self.rewrite, self.sequence))

	def rotate_dir_vector(self, direction):
		'''
		applies a rotation to self.direction_vector
		where direction is an angle
		uses the usual 2D rotation matrix
		NB: Vec3f implements dotProduct
		'''
		if direction == '+':
			angle = self.angle
		else: # direction == '-'
			angle = -self.angle
		return tlp.Vec3f(tlp.Vec3f(math.cos(angle), -math.sin(angle), 0).dotProduct(self.direction_vector), \
						 tlp.Vec3f(math.sin(angle), math.cos(angle), 0).dotProduct(self.direction_vector), \
						 0)

	def process_sequence(self, sort_property):
		'''
		uses the sequence and maps nodes to coordonates in the 2D plane
		each letter in the sequence correspond to either
		- mapping coordinates to a node (L, R)
		- going forward (F) according to the directional vector
		- rotating the directional vector (+, -)
		'''
		nodes = sorted(self.graph.getNodes(), key=lambda x: sort_property[x])
		nb_processed_nodes = 0
		i = 0
		while nb_processed_nodes < self.graph.numberOfNodes():
			if self.sequence[i] in ['L', 'R']:
				self.graph['viewLayout'][nodes[nb_processed_nodes]] = self.current_coord
				nb_processed_nodes += 1
			elif self.sequence[i] in ['-', '+']:
				self.direction_vector = self.rotate_dir_vector(self.sequence[i])
			else: # self.sequence[i] == 'F'
				self.current_coord += self.direction_vector
			i += 1
