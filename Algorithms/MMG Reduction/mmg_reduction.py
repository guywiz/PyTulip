from tulip import *
from dfs import *
import time
from mmg_ring import *

class MMG_reduction(object):
	"""
	This class implements a reduction algorithm starting from a multivariate multigraph
	encapsulating data from a criminal investigation, projecting it onto a social network.
	
	This code is companion to a paper submitted to the Journal of Graph Algorithms and Applications.
	An early version of the algorithm was presented at the EGC French Annual Conference in 2023.
	
	Bruno Pinaud, Maud Bénichou, Guy Melançon.
	Extraction d'un réseau social criminel par transformation d'un graphe d'enquête multivarié.
	Conférence Extraction et Gestion des Connaissances (EGC) 2023, Revue RNTI-039. pp.151-162.
	Référence HAL hal-03929950. https://hal.science/hal-03929950/

	Contrarily to the EGC paper, the version published on this repo is undeterministic
	and (heavily) relies on graph rewriting.

	* Erratum. The EGC paper contains a slight mistake concerning the arithmetic operators that can be used
	to compute weights on the social network. The proper requirement is to make sure the operators do
	form a commutative ring over the reals. The mistake has been properly addressed in
	the Journal of Graph Algorithms and Applications version (submitted).

	The algorithm computes a social network out of a multivariate multigraph, by iteratively
	merging multiple edges and contracting simple paths connecting entitites of a given type.
	By default, the type the multivariate graph is reduced to is PERSON, hence producing a social network
	between individuals connected through multiple artefact.

	This work was motivated by the need to consider a social network of actors
	starting from a series of observation collected along a criminal investigations.
	Links in the multivariate graph typically connect people to phones or app logins, to vehicles
	and physical locations.

	Observe that this code also applies to a variety of situations, not only those resulting
	from criminal investigation data. Furthermore, one could use the algorithm to compute
	a social of network not involving actors but any other entity type. For instance, the algorithm
	may be used to compute a social network of vehicles, assuming this is of interest as ot may reveal
	some pattern in the activity of the network, or unveal how a third party took part in these activities.
	"""
	def __init__(self, graph, ring):
		super(MMG_reduction, self).__init__()
		self.graph = graph
		self.item_id = self.graph.getStringProperty('id')
		self.history = self.graph.getStringProperty('history')
		self.compute_history = self.graph.getStringProperty('compute_history')
		self._initial_history_()
		self.ring = ring

	def _initial_history_(self):
		for e in self.graph.getEdges():
			self.history[e] = self.item_id[e]
			self.compute_history[e] = self.item_id[e]

	def set_projected_type(self, projected_type = 'PERSONNE'):
		'''
		Types of nodes and edges are stored in a string property
		whose name can be passed as a parameter. The method also require
		to specify the value of nodes that are being projected onto a social network.
		'''
		self.original_multivariate_graph = self.graph.addCloneSubGraph()
		self.original_multivariate_graph.setName('Original multivariate graph')

		self.result_graph = self.original_multivariate_graph.addCloneSubGraph(
			f'Projected graph {projected_type}',
			addSibling=True,
			addSiblingProperties=True)
		self.item_type = self.result_graph.getStringProperty('type')
		self.projected_type = projected_type

	def set_weight_property(self, weight_property_name = 'weight'):
		'''
		Edges of the original multivarate graph are manually assigned a weight
		(typically read form the file used to build the graph).
		This property will hold weights for all newly created edges
		(derived from merge or contract operations).
		'''
		self.weight = self.graph.getDoubleProperty(weight_property_name)

	def _prune_(self):
		'''
		Gets rid of nodes with degree 1 not having proper type
		(type not equal to the projected_entity_value)
		'''
		start_time = time.time()
		#print('BEFORE PRUNING, NB NODES:', self.result_graph.numberOfNodes())
		degree = self.result_graph.getLocalDoubleProperty('local_degree')
		params = tlp.getDefaultPluginParameters('Degree', self.result_graph)
		params['result'] = degree
		self.result_graph.applyDoubleAlgorithm('Degree', degree, params)
		nodes = list(filter(lambda x: self.item_type[x] != self.projected_type, sorted([n for n in self.result_graph.getNodes()], key=lambda x: degree[x])))
		while len(nodes) > 0 and degree[nodes[0]] <= 1:
			self.result_graph.delNode(nodes[0])
			self.result_graph.applyDoubleAlgorithm('Degree', degree, params)
			nodes = list(filter(lambda x: self.item_type[x] != self.projected_type, [n for n in self.result_graph.getNodes()]))
			nodes = sorted(nodes, key=lambda x: degree[x])
		#print('AFTER PRUNING, NB NODES:', self.result_graph.numberOfNodes())
		end_time = time.time()
		return end_time - start_time

	def _merge_multiple_edges_(self):
		#print('BEFORE MERGE, NB EDGES:', self.result_graph.numberOfEdges())
		start_time = time.time()
		#nb_added_edges = 0
		result, parallel_edges, loops = tlp.SimpleTest.simpleTest(self.result_graph)
		skip = []
		for e in parallel_edges:
			history = []
			compute_history = []
			if self.item_id[e] not in skip:
				source = self.result_graph.source(e)
				target = self.result_graph.target(e)
				s_edges = self.result_graph.getInOutEdges(source)
				t_edges = self.result_graph.getInOutEdges(target)
				to_merge_edges = set(s_edges).intersection(set(t_edges))
				w = self.ring.merge_operator([self.weight[e] for e in to_merge_edges])
				merged_edge = self.result_graph.addEdge(source, target)
				#nb_added_edges += 1
				self.weight[merged_edge] = w
				for ee in to_merge_edges:
					skip.append(self.item_id[ee])
					history.append(self.history[ee])
					compute_history.append(self.compute_history[ee])
					self.result_graph.delEdge(ee)
				merge_history = f"{';'.join(history)}"
				self.history[merged_edge] = merge_history
				merge_compute_history = f"{';'.join(compute_history)}"
				self.compute_history[merged_edge] = f"M({merge_compute_history})"
				self.item_id[merged_edge] = self.compute_history[merged_edge]
		end_time = time.time()
		return end_time - start_time

	def _contract_node_deg_2_(self, node):
		'''
		Important: node is assumed to have (undirected) degree exactly 2
		'''
		neighbors = []
		for n in self.result_graph.getInOutNodes(node):
			neighbors.append(n)
		weights = []
		history = []
		compute_history = []
		for e in self.result_graph.getInOutEdges(node):				
			weights.append(self.weight[e])
			history.append(self.history[e])
			compute_history.append(self.compute_history[e])
			try:
				self.result_graph.delEdge(e)
			except Exception as e:
				print(f"Node {self.result_graph['viewLabel'][node]}")
				print(f"Edge source {self.result_graph['viewLabel'][self.result_graph.source(e)]}")
				print(f"Edge target {self.result_graph['viewLabel'][self.result_graph.target(e)]}")
				raise e
		e = self.result_graph.addEdge(neighbors[0], neighbors[1])
		self.weight[e] = self.ring.contract_operator(weights)
		contract_history = f"{';'.join(history)}"
		contract_compute_history = f"C({';'.join(compute_history)})"
		self.history[e] = contract_history
		self.compute_history[e] = contract_compute_history
		self.item_id[e] = self.compute_history[e]

	def _contract_deg_2_(self):
		'''
		At this point, non person nodes in resulting graph necessarily have degree >= 2
		This method takes care of nodes of degree exactly equal to 2
		'''
		#print(f'BEFORE CONTRACTING (DEG 2), NB NODES: {self.result_graph.numberOfNodes()}, NB EDGES: {self.result_graph.numberOfEdges()}')
		start_time = time.time()
		degree = self.result_graph.getLocalDoubleProperty('local_degree')
		params = tlp.getDefaultPluginParameters('Degree', self.result_graph)
		params['result'] = degree
		self.result_graph.applyDoubleAlgorithm('Degree', degree, params)
		nodes = list(filter(lambda x: self.item_type[x] != self.projected_type and degree[x] == 2, [n for n in self.result_graph.getNodes()]))
		while len(nodes) > 0:
			candidate_node = nodes[0]
			self._contract_node_deg_2_(candidate_node)
			self._merge_multiple_edges_()
			self.result_graph.applyDoubleAlgorithm('Degree', degree, params)
			nodes = list(filter(lambda x: self.item_type[x] != self.projected_type and degree[x] == 2, [n for n in self.result_graph.getNodes()]))
		#print(f'AFTER CONTRACTING (DEG 2), NB NODES: {self.result_graph.numberOfNodes()}, NB EDGES: {self.result_graph.numberOfEdges()}')
		end_time = time.time()
		return end_time - start_time
		
	def _are_neighbours_(self, anode, bnode):
		e = self.result_graph.existEdge(anode, bnode, directed=False)
		return e.isValid()

	def _contract_simple_paths_(self):
		'''
		At this point, resulting graph only contains non person nodes of degree > 2.
		We thus fall onto the phase where we process simple paths.
		'''
		#print('CONTRACTING SIMPLE PATHS')
		total_time = 0.0
		subgraphs = []
		connected_components = self.result_graph.getDoubleProperty('connected_component')
		params = tlp.getDefaultPluginParameters('Connected Components', self.result_graph)
		params['result'] = connected_components
		self.result_graph.applyDoubleAlgorithm('Connected Components', connected_components, params)
		projected_nodes = list(filter(lambda x: self.item_type[x] == self.projected_type, [n for n in self.result_graph.getNodes()]))
		simpath = DFS(self.original_multivariate_graph, None, None, constraint = lambda x: self.item_type[x] != self.projected_type)
		collected_paths = []
		to_create_edges = []
		for i, start_node in enumerate(projected_nodes):
			for j, end_node in enumerate(projected_nodes):
				if j > i and connected_components[start_node] == connected_components[end_node]:
					start_start_time = time.time()
					simpath.reset(start_node, end_node)
					paths = sorted(simpath.getSimplePaths(), key = lambda x: - self._simple_path_weight_(x))
					node_size, edge_size = self.subgraph_size(paths)
					collected_paths += paths
					for p in self._sort_out_paths_(paths):
						to_create_edges.append([p, self._simple_path_weight_(p)])
					end_end_time = time.time()
					if node_size > 2:
						total_time += end_end_time - start_start_time
						subgraphs.append([self.graph['viewLabel'][start_node], self.graph['viewLabel'][end_node], node_size, edge_size])
		self._create_edges_(to_create_edges)
		self._clean_up_paths_(collected_paths)
		return total_time, subgraphs		

	def subgraph_size(self, paths):
		node_set = set()
		edge_set = set()
		for p in paths:
			for i in range(len(p)//2):
				node_set.add(p[2*i])
				edge_set.add(p[2*i+1])
			node_set.add(p[-1])
		return len(node_set), len(edge_set)

	def _sort_out_paths_(self, path_list):
		while(len(path_list) > 0):
			p = path_list.pop(0)
			yield p
			try:
				path_list = self._filter_paths_(p, path_list)
			except IndexError:
				# this error only happens after path_list is emptied
				# by the previous pop instruction
				# which means the next iteration does not trigger
				# and the function returns
				pass

	def _filter_paths_(self, path, path_list):
		admissible_paths = []
		path_set = set(path[1:-1])
		for p in path_list:
			if len(path_set.intersection(set(p))) == 0:
				admissible_paths.append(p)
		return admissible_paths

	def _create_edges_(self, path_weight_list):
		for p, w in path_weight_list:
			self._create_one_edge_(p, w)

	def _create_one_edge_(self, path, weight):
		source = path[0]
		target = path[-1]
		history = [self.history[path[i]] for i in range(1, len(path), 2)]
		compute_history = [self.compute_history[path[i]] for i in range(1, len(path), 2)]
		e = self.result_graph.addEdge(source, target)
		self.weight[e] = weight
		self.history[e] = f"{';'.join(history)}"

		if len(compute_history) == 1:
			self.compute_history[e] = compute_history[0]
		else:
			self.compute_history[e] = f"C({';'.join(compute_history)})"
		self.item_id[e] = self.compute_history[e]

	def _clean_up_paths_(self, path_list):
		for p in path_list:
			for i in range(1, len(p), 2):
				try:
					self.result_graph.delEdge(p[i])
				except Exception:
					continue

	def _simple_path_weight_(self, path):
		return self.ring.contract_operator([self.weight[path[i]] for i in range(1, len(path), 2)])

	def save_graph(self, filename):
		tlp.saveGraph(self.graph, filename)

	def run_algorithm(self):
		pruning = 0.0
		merging = 0.0
		contracting = 0.0
		pruning += self._prune_()
		merging += self._merge_multiple_edges_()
		pruning += self._prune_()
		contracting += self._contract_deg_2_()
		pruning += self._prune_()
		path_contract_time, subgraphs = self._contract_simple_paths_()
		contracting += path_contract_time
		merging += self._merge_multiple_edges_()
		pruning += self._prune_()
		return pruning, merging, contracting, subgraphs

def main(graph):
	# graph is a multivariate multigraph
	# the routine creates a clone subgraph of graph
	# and a social network subgraph
	mmr = MMG_reduction(graph, MMG_max_product())
	mmr.set_projected_type(projected_type = 'PERSON')
	mmr.set_weight_property(weight_property_name = 'weight')
	mmr.run_algorithm()
