from tulip import *
import tulipplugins

class MakeSimpleCount(tlp.Algorithm):
	'''
	Simplifies a multiple edge graph into a simple edge graph,
	preserving orientation,
	and assinging edge a cardinality property counting the number
	of edges underlying the singleD out edge.
	'''

	def __init__(self, context):
		tlp.Algorithm.__init__(self, context)
		# you can add parameters to the plugin here through the following syntax
		# self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
		# (see documentation of class tlp.WithParameter to see what types of parameters are supported)

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
		edge_weight = self.graph.getDoubleProperty('edge_weight')
		to_delete = []
		for n in self.graph.getNodes():
			neighbors = [e for e in self.graph.getInEdges(n)]
			source_set = set([self.graph.source(ee) for ee in neighbors])
			for nn in source_set:
				filtered_ee = filter(lambda x: self.graph.source(x).id == nn.id, neighbors)
				nb_ee = len(filtered_ee)
				for ee in filtered_ee:
					to_delete.append(ee)
				eee = self.graph.addEdge(nn, n)
				edge_weight[eee] = nb_ee
		self.graph.delEdges(to_delete)
		return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup("MakeSimpleCount", "Make Simple with edge multiplicity", "Guy Melancon", "12/12/2017", "", "1.0", "Topology Update")
