from tulip import *
import csv

class MMG_parser(object):
	"""
	This class encapsulates the overall phases needed to process
	data stored in separate csv files.
	"""
	def __init__(self, node_file, edge_file):
		super(MMG_parser, self).__init__()
		self.node_file = node_file
		self.edge_file = edge_file

		self.graph = tlp.newGraph()
		self.ids = self.graph.getStringProperty('id')
		self.types = self.graph.getStringProperty('type')
		self.labels = self.graph.getStringProperty('viewLabel')
		self.shapes = self.graph.getIntegerProperty('viewShape')
		self.icons = self.graph.getStringProperty('viewIcon')
		self.weights = self.graph.getDoubleProperty('weight')

	def _create_node_(self, node_info):
		node = self.graph.addNode()
		self.ids[node] = node_info['id']
		self.types[node] = node_info['type']
		try:
			self.labels[node] = node_info['label']
		except KeyError:
			self.labels[node] = node_info['id']
		self.shapes[node] = tlp.NodeShape.Icon
		try:
			self.icons[node] = node_info['icon']
		except KeyError:
			pass
		self.ids[node] = node_info['id']
		return node

	def _create_edge_(self, edge_info):
		try:
			source = self._get_node_(edge_info['source'])
		except KeyError as e:
			print(edge_info)
			raise e
		target = self._get_node_(edge_info['target'])
		try:
			edge = self.graph.addEdge(source, target)
		except TypeError as e:
			print(edge_info)
			raise e
		self.ids[edge] = edge_info['id']
		self.types[edge] = edge_info['type']
		try:
			self.labels[edge] = edge_info['label']
		except KeyError:
			pass
		try:
			self.weights[edge] = float(edge_info['weight'])
		except KeyError:
			self.weights[edge] = 1
		return edge

	def _get_node_(self, node_id):
		try:
			i = self.id_list.index(node_id)
			return self.node_list[i]
		except ValueError:
			print(f'id {node_id} not in')
			return None

	def _parse_nodes_(self):
		'''
		Parses a ;-separated csv file describing nodes of the multivariate multigraph.
		'''
		with open(self.node_file, 'r', encoding='utf-8-sig') as fnode:
			node_reader = csv.DictReader(fnode, delimiter=';')
			for row in node_reader:
				self._create_node_(row)
		self.id_list = [self.ids[n] for n in self.graph.getNodes()]
		self.node_list = [n for n in self.graph.getNodes()]

	def _parse_edges_(self):
		'''
		Parses a ;-separated csv file describing edges of the multivariate multigraph.
		'''
		with open(self.edge_file, 'r', encoding='utf-8-sig') as fedge:
			node_reader = csv.DictReader(fedge, delimiter=';')
			for row in node_reader:
				self._create_edge_(row)

	def get_multivariate_multigraph(self):
		self._parse_nodes_()
		self._parse_edges_()
		return self.graph