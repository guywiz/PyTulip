from tulip import *
import tulipplugins

def printit(f):
    def printed(*args, **kw):
        result = f(*args, **kw)
        #print 'Executed method: %s ' % (f.__name__)
        return result
    return printed

class OneModeProjection(object):
	'''
	Implements the projection of two-mode networks onto one-mode networks, with different possible weighting schemes:

	- uniform weights equal to 1 for all edges (same as assigning no weight ...)
	- Giatsidis
	Giatsidis, C., D. M. Thilikos, et al. (2011)
	Evaluating Cooperation in Communities with the k-Core Structure.
	Advances in Social Networks Analysis and Mining (ASONAM), 87-93.
	- clique

	Starts from a two-mode graph, project onto a one-mode graph. Entities on which projection is performed
	must be specified as a string parameter. An existing node type string property is assumed (must
	be specified as part of the plugin parameters).
	'''

	@printit
	def __init__(self, graph, weighting_scheme = 'Giatsidis', entity_type = None, substrates_name = None):
		'''
		The graph needs to have a subgraph containing (usually a cloned copy of) the two-mode network,
		with default name 'Two_mode_graph'.
		The projected one-mode network will thenbe created as a sibling of that two mode network.
		'''
		self.graph = graph
		self.weighting_scheme = weighting_scheme
		if entity_type == None:
			self.entity_type = self.graph.getStringProperty('viewLabel')
		else:
			self.entity_type = entity_type
		if substrates_name == None:
			self.substrates_name = 'A'
		else:
			self.substrates_name = substrates_name

		self.catalyst_map = {}

	@printit
	def neighbor_sets(self):
		for s in self.substrates:
			self.catalyst_map[s] = frozenset([catalyst for catalyst in self.two_mode_graph.getInOutNodes(s)])

	@printit
	def project(self):
		self.edge_type_attributes = self.substrate_graph.getStringProperty('edge_type_attributes')
		catalysts = [n for n in self.two_mode_graph.getNodes() if self.entity_type[n] != self.substrates_name]
		for c in catalysts:
			try:
				c_weight = self.weight_function(c)
				substrates = [neigh for neigh in self.two_mode_graph.getInOutNodes(c)]
				for i, si in enumerate(substrates):
					for j, sj in enumerate(substrates):
						if i < j:
							try:
								e = self.substrate_graph.existEdge(si, sj, False)
								if not e.isValid():
									e = self.substrate_graph.addEdge(si, sj)
									self.edge_type_attributes[e] += self.two_mode_graph['Type'][c]
								else:
									self.edge_type_attributes[e] += ';' + self.two_mode_graph['Type'][c]
								self.edge_weight[e] += c_weight
							except ZeroDivisionError: # happens when c has degree 1, in which case there are no inferred edges
								pass
			except Exception:
				print(self.graph['viewLabel'][si], self.graph['viewLabel'][sj])

	@printit
	def Giatsidis_weight_function(self, catalyst):
		return 1.0 / self.graph.deg(catalyst)

	@printit
	def clique_weight_function(self, catalyst):
		return 2.0 / self.graph.deg(catalyst) / (self.graph.deg(catalyst) - 1)

	@printit
	def uniform_weight(self, catalyst):
		return 1.0

	@printit
	def check(self):
		# This method is called before applying the algorithm on the input graph.
		# You can perform some precondition checks here.
		# See comments in the run method to know how to access to the input graph.

		# Must return a tuple (boolean, string). First member indicates if the algorithm can be applied
		# and the second one can be used to provide an error message
		return (True, "")

	@printit
	def run(self):
		# This method is the entry point of the algorithm when it is called
		# and must contain its implementation.

		# The graph on which the algorithm is applied can be accessed through
		# the "graph" class attribute (see documentation of class tlp.Graph).

		# The parameters provided by the user are stored in a Tulip DataSet
		# and can be accessed through the "dataSet" class attribute
		# (see documentation of class tlp.DataSet).

		# The method must return a boolean indicating if the algorithm
		# has been successfully applied on the input graph.
		self.two_mode_graph = self.graph.getSubGraph('Two_mode_graph')
		if self.two_mode_graph == None:
			self.two_mode_graph = self.graph.addCloneSubGraph('Two_mode_graph')
		self.substrates = [n for n in self.two_mode_graph.getNodes() if self.entity_type[n] == self.substrates_name]
		self.substrate_graph = self.graph.addSubGraph()
		self.substrate_graph.setName(self.substrates_name + '_graph_' + self.weighting_scheme)
		for s in self.substrates:
			self.substrate_graph.addNode(s)

		self.edge_weight = self.substrate_graph.getDoubleProperty('edge_weight')
		if self.weighting_scheme == 'Giatsidis':
			self.weight_function = self.Giatsidis_weight_function
		elif self.weighting_scheme == 'Clique':
			self.weight_function = self.clique_weight_function
		else: # self.dataSet['Weighting scheme'] == 'Uniform 1.0'
			self.weight_function = self.uniform_weight

		self.neighbor_sets()
		self.project()
		return True


@printit
def main(graph):
	et = graph.getStringProperty('Type')
	omp = OneModeProjection(graph, weighting_scheme='Uniform 1.0 weight', entity_type=et, substrates_name='website')
	omp.run()
