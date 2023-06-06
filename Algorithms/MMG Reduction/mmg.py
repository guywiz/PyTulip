import os
from pathlib import Path
import argparse
from mmg_parser import *
from mmg_reduction import *

class MMG(object):
	"""
	This class encapsulates the overall phases needed to process
	data stored in separate csv files.
	"""
	def __init__(self):
		super(MMG, self).__init__()
		parser = argparse.ArgumentParser(description='Process csv files into a multivariate mutigraph and social network.')
		parser.add_argument('--nodes', type=str, required=True, help='Name of csv file listing nodes of a multivariate multigraph.')
		parser.add_argument('--edges', type=str, required=True, help='Name of csv file listing edges of a multivariate multigraph.')
		parser.add_argument('--projected_type', type=str, help='Value of node type to reduce the multivariate multigraph to. Default value is PERSON')
		parser.add_argument('--output', type=str, required=True, help='File to which resulting graph should be stored.')
		args = parser.parse_args()
		self.node_file = args.nodes
		self.edge_file = args.edges
		self.output_file = args.output
		if args.projected_type:
			self.projected_type = args.projected_type
		else:
			self.projected_type = 'PERSON'
		try:
			self.node_file = self.file_exists(self.node_file)
			print(f'Using file {self.node_file} to process nodes')
		except FileNotFoundError:
			print(f"Cannot resolve filename {self.node_file} to any existing file in local directory {os.path.abspath('')}")
		try:
			self.edge_file = self.file_exists(self.edge_file)
			print(f'Using file {self.edge_file} to process edges')
		except FileNotFoundError:
			print(f"Cannot resolve filename {self.edge_file} to any existing file in local directory {os.path.abspath('')}")
		try:
			fout = open(self.output_file, 'w')
			fout.close()
		except FileNotFoundError:
			print(f"Unable to create output file {self.output_file}.")

	def file_exists(self, filename):
		path = Path(filename)
		absolute_path = Path(os.path.abspath('')) / path
		if path.is_file():
			return filename
		elif absolute_path.is_file():
			return str(absolute_path)
		else:
			raise FileNotFoundError(f'Could not find file {filename}')

	def parse_and_reduce(self):
		parser = MMG_parser(self.node_file, self.edge_file)
		G = parser.get_multivariate_multigraph()
		print(f'Number of nodes {G.numberOfNodes()} - Number of edges {G.numberOfEdges()}')

		reductor = MMG_reduction(G)
		reductor.set_projected_type(self.projected_type)
		reductor.set_weight_property()

		reductor.run_algorithm()
		reductor.save_graph(self.output_file)
			
if __name__ == "__main__":
	mmg = MMG()
	mmg.parse_and_reduce()


