from tulip import *
from mmg_ring import *

class MMG_player(object):
	"""
	This piece of code is written as to make it usable within
	the Graph Visualization Framework Tulip, alongside the graph.
	It is assumed the script is applied to a pair of graphs obtained
	from the reduction algorithm.
	
	The historicize method then helps mapping edges of the social network back
	into the multivariate graph.
	"""
	def __init__(self, graph, projected_type, weight_property_name):
		super(MMG_player, self).__init__()
		self.graph = graph
		self.item_id = self.graph.getStringProperty('id')
		self.types = self.graph.getStringProperty('type')
		self.history = self.graph.getStringProperty('history')
		self.compute_history = self.graph.getStringProperty('compute_history')
		self.projected_type = projected_type
		self.weight = self.graph.getDoubleProperty(weight_property_name)
		self.result_graph = graph.getSubGraph(f'Projected graph {self.projected_type}')
		self.original_multivariate_graph = graph.getSubGraph('Original multivariate graph')
		self.ring = MMG_ring()

	def reset_ring_atomic_values(self):
		edges_values = {}
		for e in self.original_multivariate_graph.getEdges():
			edges_values[self.item_id[e]] = self.weight[e]
		self.ring.set_atomic_values(edges_values)

	def historicize(self):
		# we assume an edge has been selected in the social network
		selected_edges = []
		for e in self.result_graph.getEdges():
			if self.result_graph['viewSelection'][e]:
				selected_edges.append(e)
		print(f'HISTORIZATION EDGES {selected_edges}')
		self.original_multivariate_graph['viewSelection'].setAllNodeValue(False)
		self.original_multivariate_graph['viewSelection'].setAllEdgeValue(False)
		for selected_edge in selected_edges:
			history_edge_ids = self.history[selected_edge].split(';')
			print(f'HISTORY {history_edge_ids}')
			for id in history_edge_ids:
				e = self.find_edge(id)
				self.original_multivariate_graph['viewSelection'][e] = True
				self.original_multivariate_graph['viewSelection'][self.original_multivariate_graph.source(e)] = True
				self.original_multivariate_graph['viewSelection'][self.original_multivariate_graph.target(e)] = True
		sub = self.original_multivariate_graph.addSubGraph(self.original_multivariate_graph['viewSelection'])
		sub.setName(f'Expand edge {history_edge_ids}')
		sub['viewSelection'].setAllNodeValue(False)
		sub['viewSelection'].setAllEdgeValue(False)
		
	def find_edge(self, edge_id):
		edge_ids = self.original_multivariate_graph.getStringProperty('id')
		for e in self.original_multivariate_graph.getEdges():
			if edge_ids[e] == edge_id:
				return e
		return None

	def report_type_weights(self):
		weight_dict = {}
		for e in self.original_multivariate_graph.getEdges():
			weight_dict[self.types[e]] = self.weight[e]
		return sorted(weight_dict.items(), key=lambda x: -x[1])


	def reload_weights(self, weight_dict):
		'''
		This method allows to reset weights assigned to primary edge types
		(edges that are part of the original multivariate multigraph).
		New weights are read from key-value pairs (type - float).
		Types that do not appear in the dict keep their already assigned weights.
		'''
		types_new_weight = weight_dict.keys()
		for e in self.original_multivariate_graph.getEdges():
			if self.types[e] in types_new_weight:
				self.weight[e] = weight_dict[self.types[e]]

	def recompute_weights(self):
		for e in self.result_graph.getEdges():
			new_value = self.ring.eval(self.compute_history[e])
			self.weight[e] = new_value

	def reload_weights_from_file(self, weight_file):
		'''
		This method allows to reset weights assigned to primary edge types
		(edges that are part of the original multivariate multigraph)
		from a csv file.
		The file must follow a very simple structure, listing on each line
		an edge type and a value, separated by a semi-colon ';',
		with headers begin 'type' and 'value'.
		Types that do not appear in the csv file keep their already assigned weights.
		'''
		with open(weight_file, 'r') as fweights:
			weight_reader = csv.DictReader(fweights, delimiter=';')
			weight_dict = {}
			for row in weight_reader:
				weight_dict[row['type']] = float(row['value'])
			for e in self.original_multivariate_graph.getEdges():
				self.weight[e] = weight_dict[self.types[e]]
				
def main(graph):
	'''
	The script must be run from the superGraph holding the two
	graphs: social network as well as the original multigraph.
	'''
	player = MMG_player(graph, 'PERSON', 'weight')
	player.historicize()

	


