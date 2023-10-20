from tulip import *
from mmg_ring import merge_operator, contract_operator

class MMG_player(object):
	"""
	This class implements a reduction algorithm first published in:
	
	Bruno Pinaud, Maud Bénichou, Guy Melançon.
	Extraction d'un réseau social criminel par transformation d'un graphe d'enquête multivarié.
	Conférence Extraction et Gestion des Connaissances (EGC) 2023, Revue RNTI-039. pp.151-162.
	Référence HAL hal-03929950.

	The algorithm computes a social network out of a multivariate multigraph, by iteratively
	merging multiple edges and contracting simple paths connecting entitites of a given type.
	By default, the type the multivariate graph is reduced to is PERSON, hence producing a social network
	between individuals connected through multiple artefact.

	This work was motivated by the need to consider a social network of actors
	starting from a series of observation collected along a criminal investigations.
	Links in the multivariate graph typically connect people to phones or app logins, to vehicle
	and physical location.

	This piece of code is written as to make it usable within the Graph Visualization Framework Tulip,
	alongisde the graph. The historicize method then helps mapping edges of the social network back
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
		sub = self.original_multivariate_graph.inducedSubGraph(self.original_multivariate_graph['viewSelection'])
		sub.setName(f'Expand edge {history_edge_ids}')
		
	def find_edge(self, edge_id):
		edge_ids = self.original_multivariate_graph.getStringProperty('id')
		for e in self.original_multivariate_graph.getEdges():
			if edge_ids[e] == edge_id:
				return e
		return None

	def reload_weights(self, weight_file):
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
		for e in self.result_graph.getEdges():
			self.weight[e] = self._recompute_weight_(self.compute_history[e])
				
def main(graph):
	player = MMG_player(graph, 'PERSON', 'weight')
	player.historicize()

