from tulip import *
import tulipplugins

class MergeSubGraphs(tlp.Algorithm):
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
		self.addStringParameter('Subgraphs to be merged. Type in a ;-separated list of words', 'Subgraphs whose names includes at least on of the keywords will be selected.', 'Replace this string by a semi-colon list of keywords such as "Vol;Cambrio"')
		self.addStringParameter('(Optional) Merged subgraph name', 'Name of resulting graph', '', False)

	def merge(self):
		# find which subgraphs should be merged
		# a subgraph is marked as "to be merged" if any (at least one) of its elements
		# is selected (marked as true in the given selection property)
		to_be_merged = self.dataSet['Subgraphs to be merged. Type in a ;-separated list of words'].split(';')
		merge_subgraph_name = self.dataSet['(Optional) Merged subgraph name']
		if merge_subgraph_name == '':
			merge_subgraph_name = '_'.join(to_be_merged)
		merge_subgraph = self.graph.addSubGraph(merge_subgraph_name)
		for sg in self.graph.getSubGraphs():
			if sum(map(lambda x: x in sg.getName(), to_be_merged)) > 0:
				for n in sg.getNodes():
					merge_subgraph.addNode(n)
				for e in sg.getEdges():
					merge_subgraph.addEdge(e)

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
		self.merge()
		return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("MergeSubGraphs", "Merge SubGraphs", "Guy Melancon", "12/12/2017", "", "1.0", "SubGraphs")
