from tulip import *
import tulipplugins

class Multilayer(tlp.Algorithm):
	'''
	Implements the projection of two-mode networks onto one-mode networks,
	aggregating edge types and building different subgraphs (one for each edge type).

	Starts from a two-mode graph, project onto a one-mode graph. Entities on which projection is performed
	must be specified as a string parameter. An existing node type string property is assumed (must
	be specified as part of the plugin parameters).
	'''

	def __init__(self, context):
		tlp.Algorithm.__init__(self, context)
		# you can add parameters to the plugin here through the following syntax
		# self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
		# (see documentation of class tlp.WithParameter to see what types of parameters are supported)
		self.addStringPropertyParameter("Entity type", "Property from which entity type is inspected", 'viewLabel')
		self.addStringParameter("Substrates (projected entities)", "Entity type (name) on which two-mode graph is projected", "")
		self.addStringPropertyParameter("Projected entity type", "Property from which edge type is inferred", 'viewLabel')

	def project(self):
		catalysts = [n for n in self.two_mode_graph.getNodes() if self.dataSet["Entity type"][n] != self.dataSet["Substrates (projected entities)"]]
		edge_types = self.substrate_graph.getStringProperty('Edge types')
		for c in catalysts:
			catalyst_type = self.dataSet["Projected entity type"][c]
			catalyst_subgraph = self.substrate_graph.getSubGraph(catalyst_type)
			if catalyst_subgraph == None:
				catalyst_subgraph = self.substrate_graph.addSubGraph(catalyst_type)
			local_edge_weight = catalyst_subgraph.getLocalDoubleProperty('edge_weight')
			substrates = [neigh for neigh in self.two_mode_graph.getInOutNodes(c)]
			for i, si in enumerate(substrates):
				for j, sj in enumerate(substrates):
					if i < j:
						catalyst_subgraph.addNode(si)
						catalyst_subgraph.addNode(sj)
						e = catalyst_subgraph.existEdge(si, sj, False)
						if not e.isValid():
							e = catalyst_subgraph.addEdge(si, sj)
						self.edge_weight[e] += 1
						local_edge_weight[e] += 1
						type_set = set(edge_types[e].split(';'))
						type_set.add(catalyst_type)
						edge_types[e] = ';'.join(type_set)

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
		self.substrate_graph.setName('Multilayer ' + self.dataSet['Substrates (projected entities)'] + ' Projection')
		self.edge_weight = self.substrate_graph.getDoubleProperty('edge_weight')
		self.project()
		return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("Multilayer", "Multilayer Projection", "Guy Melancon", "12/12/2017", "", "1.0", "Two_mode_Networks")
