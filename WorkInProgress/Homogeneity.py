#coding=utf-8

import csv
from tulip import *
import numpy as np

class Homogeneity(object):
	"""docstring for Homogeneity"""
	def __init__(self, one_mode_graph, edge_attributes_property_name):
		super(Homogeneity, self).__init__()
		self.one_mode_graph = one_mode_graph
		self.type = self.one_mode_graph.getStringProperty(edge_attributes_property_name)

	def countMatrix(self):
		edge_types = set()
		for e in self.one_mode_graph.getEdges():
			for t in self.type[e].split(';'):
				edge_types.add(t)
		edge_types = list(edge_types)
		print edge_types

		m = np.matrix([[0.0 for t in edge_types] for tt in edge_types])

		for e in self.one_mode_graph.getEdges():
			e_types = set(self.type[e].split(';'))
			for t in e_types:
				i = edge_types.index(t)
				for tt in e_types:
					j = edge_types.index(tt)
					m[i,j] += 1.0

		with open('coOccurrence_matrices_ssgraph.csv', 'w') as fout:
			fout.write(';'.join(edge_types))
			fout.write('\n')
			for i in range(len(edge_types)):
				row = []
				for j in range(len(edge_types)):
					row.append(str(m[i,j]))
				print(row)
				fout.write(';'.join(row) + '\n')

def main(graph):
	h = Homogeneity(graph, 'edge_type_attributes')
	h.countMatrix()

