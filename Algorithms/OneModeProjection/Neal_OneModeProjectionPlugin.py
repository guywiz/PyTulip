from tulip import *
import tulipplugins

class Neal_OneModeProjection(tlp.Algorithm):

	def __init__(self, context):
		tlp.Algorithm.__init__(self, context)
		# you can add parameters to the plugin here through the following syntax
		# self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
		# (see documentation of class tlp.WithParameter to see what types of parameters are supported)
		self.addStringPropertyParameter("Entity type", "Property from which entity type is inspected", 'type')
		self.addStringParameter("Substrates (projected entities)", "Entity type (name) on which two-mode graph is projected", "person")
		self.addFloatParameter("Threshold", "Value to filter edges in projected graph", "0.1")

	def binomial(self, n, k):
		fact_k = 1
		for i in range(2, k+1):
			fact_k *= i
		num_n_k = 1
		for i in range(n, n-k, -1):
			num_n_k *= i
		return num_n_k // fact_k

	def probability(self, P1, P2, C):
		if C > min(P1, P2):
			return 0
		E = self.nbCatalysts
		p = 1.0
		p *= self.binomial(E, C)
		p *= self.binomial(E - C, P1 - C)
		p *= self.binomial(E - P1, P2 - C)
		p /= self.binomial(E, P1)
		p /= self.binomial(E, P2)
		return p
	
	def max_probability(self, P1, P2):
		max_C_value = 0
		p = self.probability(P1, P2, max_C_value)
		q = self.probability(P1, P2, max_C_value + 1)
		while q > p:
			p = q
			max_C_value += 1
			q = self.probability(P1, P2, max_C_value + 1)
		return max_C_value

	def thresholds(self, P1, P2, alpha):
		C = self.max_probability(P1, P2)
		p = self.probability(P1, P2, C)
		lower_threshold = C
		upper_threshold = C
		print('Curr p, 1-alpha, low, high, P1, P2', p < 1-alpha, C >= min(P1, P2), lower_threshold, upper_threshold)
		while p < 1 - alpha:
			print('Curr p, low, high', p, lower_threshold, upper_threshold)
			lower_threshold -= 1
			upper_threshold += 1
			p += self.probability(P1, P2, lower_threshold) + self.probability(P1, P2, upper_threshold)
		return lower_threshold, upper_threshold

	def plainProject(self):
		'''
		parse all nodes of type 'not substrate'
		for each,
		grab their neighbors (they are of type 'substrate')
		build a clique (add all missing edges, as some might already be there)
		'''
		self.plainOneModeGraph = self.graph.getSubGraph('NealOneMode_plain')
		if self.plainOneModeGraph == None:
			self.plainOneModeGraph = self.graph.addSubGraph()
			self.plainOneModeGraph.setName('NealOneMode_plain')
			for n in self.two_mode_graph.getNodes():
				print('Node', self.two_mode_graph['viewLabel'][n])
				if self.two_mode_graph['type'][n] == self.substrateType:
					self.plainOneModeGraph.addNode(n)
					print('Node', self.two_mode_graph['viewLabel'][n])

		for node in self.two_mode_graph.getNodes():
			if self.type[node] != self.substrateType:
				for neigh1 in self.two_mode_graph.getInOutNodes(node):
					for neigh2 in self.two_mode_graph.getInOutNodes(node):
						if neigh1.id != neigh2.id:
							self.plainOneModeGraph.addEdge(neigh1, neigh2)
		params = tlp.getDefaultPluginParameters('Make Simple', self.plainOneModeGraph)
		self.plainOneModeGraph.applyAlgorithm('Make Simple', params)

	def NealProject(self, alpha):
		self.NealOneModeGraph = self.graph.addSubGraph()
		self.NealOneModeGraph.setName('NealOneModeNew_' + str(alpha))
		[self.NealOneModeGraph.addNode(n) if self.two_mode_graph['type'][n] == self.substrateType else 0 for n in self.two_mode_graph.getNodes()]
		neighborhoods = {}
		for n in self.NealOneModeGraph.getNodes():
			neighborhoods[n] = set([nn for nn in self.two_mode_graph.getInOutNodes(n)])
		for e in self.plainOneModeGraph.getEdges():
			source = self.plainOneModeGraph.source(e)
			#print(source)
			target = self.plainOneModeGraph.target(e)
			#print(target)
			N_source = neighborhoods[source]
			#print('N_source', source, self.two_mode_graph.deg(source), ':', N_source)
			N_target = neighborhoods[target]
			#print('N_target', target, self.two_mode_graph.deg(target), ':', N_target)
			N_s_t = N_source.intersection(N_target)
			#print(N_s_t)
			low, high = self.thresholds(len(N_source), len(N_target), alpha)
			print('Low, High', low, high)
			if len(N_s_t) > high:
				#print('Nb common events', len(N_s_t), 'greater than threshold', C)
				self.NealOneModeGraph.addEdge(e)

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
		type_property = self.dataSet['Entity type']
		substrateType = self.dataSet['Substrates (projected entities)']
		alpha = self.dataSet['Threshold']

		self.two_mode_graph = self.graph.getSubGraph('Original two mode graph (clone)')
		if self.two_mode_graph == None:
			self.two_mode_graph = self.graph.addCloneSubGraph('Original two mode graph (clone)')
		self.type = type_property
		self.name = self.graph.getStringProperty('name')
		self.substrateType = substrateType
		self.nbCatalysts = sum([1 if self.type[n] != self.substrateType else 0 for n in self.two_mode_graph.getNodes()])

		self.plainProject()
		self.NealProject(alpha)

		return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("Neal_OneModeProjection", "Z. Neal One-Mode Projection", "Guy Melancon", "6/11/2016", "", "1.0", "Two_mode_Networks")
