from tulip import *
import tulipplugins

class OneModeProjection(tlp.Algorithm):
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

	def project(self):
		catalysts = [n for n in self.two_mode_graph.getNodes() if self.dataSet["Entity type"][n] != self.dataSet["Substrates (projected entities)"]]
		for c in catalysts:
			try:
				c_weight = self.weight_function(c)
				substrates = [neigh for neigh in self.two_mode_graph.getInOutNodes(c)]
				for i, si in enumerate(substrates):
					for j, sj in enumerate(substrates):
						if i < j:
							e = self.substrate_graph.existEdge(si, sj, False)
							if not e.isValid():
								e = self.substrate_graph.addEdge(si, sj)
							self.edge_weight[e] += c_weight
			except ZeroDivisionError: # happens when c has degree 1, in which case there are no inferred edges
				pass
			except Exception:
				print(self.graph['viewLabel'][si], self.graph['viewLabel'][si])

	def Giatsidis_weight_function(self, catalyst):
		return 1.0 / self.graph.deg(catalyst)

	def clique_weight_function(self, catalyst):
		return 2.0 / self.graph.deg(catalyst) / (self.graph.deg(catalyst) - 1)

	def uniform_weight(self, catalyst):
		return 1.0

	def compute_cores(self):
		self.kcore = self.substrate_graph.getDoubleProperty('kcore')
		kcore_dataset = tlp.getDefaultPluginParameters('K-Cores')
		kcore_dataset['metric'] = self.edge_weight
		self.substrate_graph.applyDoubleAlgorithm('K-Cores', self.kcore, kcore_dataset)

		eqvalue_dataset = tlp.getDefaultPluginParameters('Equal Value')
		eqvalue_dataset['Property'] = self.kcore
		self.substrate_graph.applyAlgorithm('Equal Value', eqvalue_dataset)

	def __init__(self, context):
		tlp.Algorithm.__init__(self, context)
		# you can add parameters to the plugin here through the following syntax
		# self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
		# (see documentation of class tlp.WithParameter to see what types of parameters are supported)
		self.addStringPropertyParameter("Entity type", "Property from which entity type is inspected", 'viewLabel')
		self.addStringParameter("Substrates (projected entities)", "Entity type (name) on which two-mode graph is projected", "")
		self.addStringCollectionParameter("Weighting scheme", \
				"Weight computation rule (Giatsidis=catalyst degree / Clique=induced clique size)",\
				"Giatsidis;Clique;Uniform 1.0 weight")
		self.addBooleanParameter("Build k-cores", "Builds core subgraphs", "False")

	def check(self):
		# This method is called before applying the algorithm on the input graph.
		# You can perform some precondition checks here.
		# See comments in the run method to know how to access to the input graph.

		# Must return a tuple (boolean, string). First member indicates if the algorithm can be applied
		# and the second one can be used to provide an error message
		return (True, "")

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
		self.substrates = [n for n in self.two_mode_graph.getNodes() if self.dataSet["Entity type"][n] == self.dataSet["Substrates (projected entities)"]]
		self.substrate_graph = self.graph.addSubGraph()
		for s in self.substrates:
			self.substrate_graph.addNode(s)
		self.substrate_graph.setName(self.dataSet['Substrates (projected entities)'] + '_graph_' + self.dataSet['Weighting scheme'])

		self.edge_weight = self.substrate_graph.getDoubleProperty('edge_weight')
		if self.dataSet['Weighting scheme'] == 'Giatsidis':
			self.weight_function = self.Giatsidis_weight_function
		elif self.dataSet['Weighting scheme'] == 'Clique':
			self.weight_function = self.clique_weight_function
		else: # self.dataSet['Weighting scheme'] == 'Uniform 1.0'
			self.weight_function = self.uniform_weight

		self.project()
		if self.dataSet['Build k-cores']:
			self.compute_cores()
		return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("OneModeProjection", "One-Mode Projection", "Guy Melancon", "24/05/2016", "", "1.0", "Two_mode_Networks")
