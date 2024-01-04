# When the plugin development is finished, you can copy the associated
# Python file to /Users/melancon/.Tulip-5.7/plugins/python
# and it will be automatically loaded at Tulip startup

from tulip import tlp
import tulipplugins
import igraph
import networkx as nx
import leidenalg

class iGraphConverter():
	'''
	Utility class to convert grpahs between formats,
	baiscally Tulip and iGraph
	(used by the iGrpah implementation of the Leiden algorithm)
	'''
	def __init__(self, tulip_graph):
		super(iGraphConverter, self).__init__()
		self.tulip_graph = tulip_graph
		tulip_nodes = [n for n in self.tulip_graph.getNodes()]
		tulip_edges = [e for e in self.tulip_graph.getEdges()]
		self.node_to_index = {tulip_nodes[i]: i for i in range(self.tulip_graph.numberOfNodes())}
		self.index_to_node = {i: tulip_nodes[i] for i in range(self.tulip_graph.numberOfNodes())}
		self.edge_to_index = {e: self._edge_index_(e) for e in tulip_edges}
		self.index_to_edge = {}
		for tulip_edge, edge_index in self.edge_to_index.items():
			self.index_to_edge[edge_index] = tulip_edge

	def _edge_index_(self, tulip_edge):
		s = self.tulip_graph.source(tulip_edge)
		t = self.tulip_graph.target(tulip_edge)
		i = self.node_to_index[s]
		j = self.node_to_index[t]
		return i * self.tulip_graph.numberOfNodes() + j

	def to_igraph(self, exported_node_properties = [], exported_edge_properties = []):
		nb_vertices = self.tulip_graph.numberOfNodes()
		edges = [(self.node_to_index[self.tulip_graph.source(e)], self.node_to_index[self.tulip_graph.target(e)]) for e in self.tulip_graph.getEdges()]
		iG = igraph.Graph(nb_vertices)
		iG = igraph.Graph.as_directed(iG, 'random')
		iG.add_edges(edges)
		for p in exported_node_properties:
			self.write_node_property(iG, p)
		for p in exported_edge_properties:
			self.write_edge_property(iG, p)
		return iG

	def write_node_property(self, i_graph, property_name):
		values = []
		#for i in range(self.tulip_graph.numberOfNodes():
		# tulip_node_from_index = self.index_to_node[i]
		# property_value = self.tulip_graph[property_name]
		i_graph.vs[property_name] = [self.tulip_graph[property_name][self.index_to_node[i]] for i in range(self.tulip_graph.numberOfNodes())]

	# edge in igraph, index of source and target in igraph, convert to unique integer
	# use map integer -> edge in tulip graph
	def write_edge_property(self, i_graph, property_name):
		property_values = []
		for e in i_graph.es:
			i = e.source
			j = e.target
			edge_index = i * self.tulip_graph.numberOfNodes() + j
			e_tulip = self.index_to_edge[edge_index]
			property_values.append(self.tulip_graph[property_name][e_tulip])
		i_graph.es[property_name] = property_values

class ParticipationCoefficient(tlp.DoubleAlgorithm):
    """
    Computes the participation coefficient of nodes as defined by R. Guimera:
    
    Guimera, R., Mossa, S., Turtschi, A., & Amaral, L. N. (2005).
    The worldwide air transportation network: Anomalous centrality, community structure, and cities' global roles.
    Proceedings of the National Academy of Sciences, 102(22), 7794-7799.
    and/or
    Guimera, R., & Amaral, L. A. N. (2005). Cartography of complex networks: modules and universal roles.
    Journal of Statistical Mechanics: Theory and Experiment, 2005(02), P02001.

    This is a meso level statistics in that it depends on a community structure for the graph.
    """
    def __init__(self, context):
        tlp.DoubleAlgorithm.__init__(self, context)
        # You can add parameters to the plugin here through the
        # following syntax:
        # self.add<Type>Parameter('<paramName>', '<paramDoc>',
        #                         '<paramDefaultValue>')
        # (see the documentation of class tlp.WithParameter to see what
        #  parameter types are supported).
        self.addIntegerPropertyParameter('communities', help='Integer property holding commmunity membership of nodes', defaultValue='', isMandatory=True, inParam=True, outParam=False, valuesDescription  ='Integer property holding commmunity membership of nodes')
        self.addIntegerParameter('nb iterations', help='Number of trials (community detection runs)', defaultValue='50', isMandatory=True, inParam=True, outParam=False, valuesDescription  ='Number of trials (community detection runs)')
        self.addDoublePropertyParameter('result', help='Double property holding the resulting coefficient', defaultValue='', isMandatory=True, inParam=True, outParam=False, valuesDescription  ='Participation coefficient of nodes')

    def participation_coefficient(self, node):
        self.nb_communities = int(self.community_property.getNodeMax() + 1)
        distrib = [0 for i in range(self.nb_communities)]
        for neigh in self.graph.getInOutNodes(node):
            distrib[int(self.community_property[neigh])] += 1
        d = sum(distrib)
        return 1 - sum(list(map(lambda x: (x / d) ** 2, distrib)))

    def check(self):
        # This method is called before applying the algorithm on the
        # input graph. You can perform some precondition checks here.
        # See comments in the run method to know how to have access to
        # the input graph.
        #
        # Must return a tuple (Boolean, string). First member indicates if the
        # algorithm can be applied and the second one can be used to provide
        # an error message.
        return (True, '')

    def run_community_finding_algorithm(self):
        """
        Uses Leiden's (improvement over Louvain) implemented under igraph
        """
        gc = iGraphConverter(self.graph)
        iG = gc.to_igraph()
        communities = leidenalg.find_partition(
            iG, leidenalg.ModularityVertexPartition
        )
        node_partition = [set(communities[i]) for i in range(len(communities))]
        try:
            modularity = nx.community.modularity(nx.Graph(iG.get_edgelist()), node_partition)
        except nx.algorithms.community.quality.NotAPartition as e:
            if not tlp.ConnectedTest.isConnected(self.graph):
                print(f'Graph is not connected')
                raise e
        membership = communities.membership
        for n in self.graph.getNodes():
            self.community_property[n] = membership[gc.node_to_index[n]]
        return len(communities), modularity

    def run(self):
        # This method is the entry point of the algorithm when it is called
        # and must contain its implementation.
        #
        # The graph on which the algorithm is applied can be accessed through
        # the 'graph' class attribute (see documentation of class tlp.Graph).
        #
        # The parameters provided by the user are stored in a dictionary
        # that can be accessed through the 'dataSet' class attribute.
        #
        # The result of this double algorithm must be stored in the
        # double property accessible through the 'result' class attribute
        # (see documentation to know how to work with graph properties).
        #
        # The method must return a Boolean indicating if the algorithm
        # has been successfully applied on the input graph.
        self.community_property = self.dataSet['communities']
        nb_iterations = self.dataSet['nb iterations']
        part_coeff = self.dataSet["result"]
        part_coeff.setAllNodeValue(0.0)
        for k in range(nb_iterations):
            self.run_community_finding_algorithm()
            for node in self.graph.getNodes():
                part_coeff[node] += self.participation_coefficient(node)
        for node in self.graph.getNodes():
            part_coeff[node] /= nb_iterations
        return True

# The line below does the magic to register the plugin into the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup('ParticipationCoefficient', 'Participation Coefficient', 'G.M.', '21/12/2023', 'Computes the participation coefficient of nodes as defined by Guimera et al.', '1.0', 'Graph')
