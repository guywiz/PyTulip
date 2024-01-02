# distribution packages
import numpy as np
import pandas as pd
import networkx as nx
from tulip import tlp
import tulipplugins
import leidenalg

# local package
from Dijkstra import *
#from utils import *

"""
This script offers an alternative to Paquet-CLouston an Bouchard `python` package
computing their broker score defined on node sof a network. Please refer to their paper

	Paquet-Clouston, M., & Bouchard, M. (2023).
	A Robust Measure to Uncover Community Brokerage in Illicit Networks.
	_Journal of Quantitative Criminology_, 39(3), 705-733.

Our code follows from the reformulation of Paquet-Clouston and Bouchard formula as a vector and matrix product.

The main class `BrokerScore` implements all necessary methods, partly relying on the `Dijkstra` class
to run a dfs and compute a community cohesion score. In order to stick with Paquet-Clouston and Bouchard definition
of cohesion, we invoke networkX average path length routine which requires
to convert from Tulip into the iGraph format.

A code snippet at the bottom of the BrokerScore class file alows the use of the code
from within the Tulip desktop applicaiton. Running the script should be easy. Make sure
the local hierarchy is clean and does not contain any subgraph, as the script does produce
a series of subgraph and makes use of unrobust naming conventions.
"""
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

class BrokerScore(tlp.DoubleAlgorithm):
    def __init__(self, context):
        tlp.DoubleAlgorithm.__init__(self, context)
        # You can add parameters to the plugin here through the
        # following syntax:
        # self.add<Type>Parameter('<paramName>', '<paramDoc>',
        #                         '<paramDefaultValue>')
        # (see the documentation of class tlp.WithParameter to see what
        #  parameter types are supported).
        self.addIntegerPropertyParameter(
            "communities",
            help="Integer property holding commmunity membership of nodes",
            defaultValue="",
            isMandatory=True,
            inParam=True,
            outParam=False,
            valuesDescription="Integer property holding commmunity membership of nodes",
        )
        self.addIntegerParameter(
            "nb iterations",
            help="Number of trials (community detection runs)",
            defaultValue="50",
            isMandatory=True,
            inParam=True,
            outParam=False,
            valuesDescription="Number of trials (community detection runs)",
        )
        self.addDoublePropertyParameter(
            "result",
            help="Double property holding the resulting coefficient",
            defaultValue="viewMetric",
            isMandatory=True,
            inParam=True,
            outParam=False,
            valuesDescription="Broker score of nodes",
        )

    def check(self):
        # This method is called before applying the algorithm on the
        # input graph. You can perform some precondition checks here.
        # See comments in the run method to know how to have access to
        # the input graph.
        #
        # Must return a tuple (Boolean, string). First member indicates if the
        # algorithm can be applied and the second one can be used to provide
        # an error message.

		# check whether communities have already been instanciated as subgraphs
		# no fancy stuff here, if there are subgraphs assume everything works fine
		# no name checking or number of subgraphs etc.
		# its all or nothing
        test_community = len(list(self.graph.getSubGraphs())) > 0
        if test_community:
            return (False, "Make sure communities have not been computed as subgraphs already (delete all subgraphs).")
        return (True, "")

    def _standardize_community_names_(self):
        # normalize community names (subgraphs)
        # we assume subgraphs have been named by the Equal value plugin
        # (using its input metric name)
        # !!! and that communities are labelled using consecutive integers starting from 0 !!!
        for sub in self.graph.getSubGraphs():
            # for what its worth, when using EqualValue, subgraphs are named using 
            # the property name and metric (integer) values, using colon ":"
            if not ':' in sub.getName():
                return
            else:
                community_property_name = self.community.getName()
                sub.setName(f'{community_property_name}_{sub.getName().split(":")[1].strip()}')

    def build_communities(self):
        # first get rid fo any remaining subgraph structure
        # since a new one is built
        for sub in self.graph.getSubGraphs():
            self.graph.delSubGraph(sub)
        params = tlp.getDefaultPluginParameters("Equal Value", self.graph)
        params["property"] = self.community
        self.graph.applyAlgorithm("Equal Value", params)

    def run_community_finding_algorithm(self, algo="Leiden"):
        """
        Can compute communities using Tulip's Louvain implementation
        or rather use Leiden's (improvement over Louvain) implemented under igraph
        """
        if algo.lower() == "louvain":
            params = tlp.getDefaultPluginParameters("Louvain", self.graph)
            params["result"] = self.community
            self.graph.applyDoubleAlgorithm("Louvain", self.community, params)
        else:  # algo == 'Leiden'
            gc = iGraphConverter(self.graph)
            iG = gc.to_igraph()
            communities = leidenalg.find_partition(
                iG, leidenalg.ModularityVertexPartition
            )
            membership = communities.membership
            for n in self.graph.getNodes():
                self.community[n] = membership[gc.node_to_index[n]]

    def collect_community_names(self):
        self.community_names = sorted(
            [sub.getName() for sub in self.graph.getSubGraphs()],
            key=lambda x: int(x.split("_")[1]),
        )
        self.nb_communities = len(self.community_names)

    def is_broker(self, node):
        for n in self.graph.getInOutNodes(node):
            if self.community[node] != self.community[n]:
                return True
        return False

    def compute_node_average_distance(self, subgraph, node):
        # computes the average distance to a node in a subgraph
        dijk = Dijkstra(subgraph)
        dijk.compute_distance_from(node)
        result = subgraph.getDoubleProperty("dist_to_source")
        ave = sum([result[n] for n in subgraph.getNodes()]) / (
            subgraph.numberOfNodes() - 1
        )
        return ave

    def compute_community_cohesion(self, community_name):
        subgraph = self.graph.getSubGraph(community_name)
        G = nx.Graph()
        for n in subgraph.getNodes():
            G.add_node(n.id)
        for e in subgraph.getEdges():
            G.add_edge(subgraph.source(e).id, subgraph.target(e).id)
        cohesion = nx.average_shortest_path_length(G)
        return cohesion

    def compute_community_cohesion_old(self, community_name):
        """
        go over all nodes
        compute distance to all other nodes, average it
        average these average distance for all nodes
        """
        community_subgraph = self.graph.getSubGraph(community_name)
        average_distance_to_node = {}
        for node in community_subgraph.getNodes():
            average_distance_to_node[node] = self.compute_node_average_distance(
                community_subgraph, node
            )
        cohesion = (
            sum([average_distance_to_node[n] for n in community_subgraph.getNodes()])
            / community_subgraph.numberOfNodes()
        )
        return cohesion

    def compute_cohesion_vector(self):
        vec = np.zeros(self.nb_communities)
        for i, c in enumerate(self.community_names):
            vec[i] = self.compute_community_cohesion(c)
        return vec

    def compute_community_vector(self):
        vec = np.zeros(self.nb_communities)
        for i, c in enumerate(self.community_names):
            community_size = self.graph.getSubGraph(c).numberOfNodes()
            comm_cohesion = self.compute_community_cohesion(c)
            try:
                vec[i] = community_size / comm_cohesion
            except ZeroDivisionError:
                # happens if a community reduces to a single node
                vec[i] = 1
        return vec

    def compute_neighbor_communities(self):
        """
        computes (the index of) neighbor communities to all nodes and store
        that information in a map
        given a node u, a neighbor community to that node is a community C
        admitting a node v which is neighbor to u

        a node u admitting at least one neighbor community (other than the one it belongs to)
        is a broker
        """
        self.neighbor_communities = {}
        for node in self.graph.getNodes():
            neighCommunities = set(
                [int(self.community[neigh]) for neigh in self.graph.getInOutNodes(node)]
            )
            try:
                neighCommunities.remove(int(self.community[node]))
            except KeyError:
                # remove will fail if node has no neighbor in its own community
                # happens if a community contains only one node
                # (happeded with broker's network)
                pass
            self.graph["neighbor_communities"][node] = [
                str(x) for x in neighCommunities
            ]
            self.neighbor_communities[node] = neighCommunities

    def NBC(self, community_index, other_community_index):
        """
        computes the number of nodes in community
        that have (at least one) a neighbor in other_community
        """
        community_name = self.community_names[community_index]
        community_subgraph = self.graph.getSubGraph(community_name)
        n_brokers = 0
        for n in community_subgraph.getNodes():
            if other_community_index in self.neighbor_communities[n]:
                n_brokers += 1
        return n_brokers

    def compute_community_matrix(self):
        M = np.zeros((self.nb_communities, self.nb_communities))
        for i, c in enumerate(self.community_names):
            for j, cc in enumerate(self.community_names):
                if i == j:
                    M[i, j] = 1
                else:
                    nbc = self.NBC(i, j)
                    if nbc != 0:
                        M[i, j] = 1 / np.sqrt(nbc)
        return M

    def compute_node_vector(self, node):
        node_vector = np.zeros(self.nb_communities)
        node_vector[int(self.community[node])] = 1
        if len(self.neighbor_communities[node]) > 0:
            for i in self.neighbor_communities[node]:
                node_vector[i] = 1
        return node_vector

    def number_of_brokers(self):
        return sum([1 if self.graph[self.score_property_name][n] > 0 else 0 for n in self.graph.getNodes()])
    
    def compute_broker_network(self):
        i = 0
        current_graph = self.graph
        community_property_name = f"community_{i}"
        score_property_name = f"broker_score_{i}"
        selection_property_name = f"is_broker_{i}"
        # level 0 coincides with original graph
        community_0 = current_graph.getLocalDoubleProperty(community_property_name)
        try:
            community_0.copy(self.community)
        except TypeError:
            for n in current_graph.getNodes():
                self.community[n] = int(community_0[n])

        while True:
            bs = BrokerScore(
                current_graph, community_property_name, score_property_name
            )
            bs.node_brokerage_score()
            select = current_graph.getBooleanProperty(selection_property_name)
            select.setAllNodeValue(False)
            score = current_graph.getLocalDoubleProperty(score_property_name)
            for n in current_graph.getNodes():
                if score[n] > 0:
                    select[n] = True
            induced_subgraph = current_graph.inducedSubGraph(
                select, name=selection_property_name
            )
            if induced_subgraph.numberOfNodes() == current_graph.numberOfNodes():
                # all nodes in current_graph are brokers
                current_graph.delSubGraph(induced_subgraph)
                return
            else:
                i += 1
                community_property_name = f"community_{i}"
                score_property_name = f"broker_score_{i}"
                selection_property_name = f"is_broker_{i}"
                current_graph = induced_subgraph

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
        self.community = self.dataSet["communities"]
        nb_iterations = self.dataSet["nb iterations"]
        broker_score = self.dataSet["result"]
        broker_score.setAllNodeValue(0.0)

        for k in range(nb_iterations):
            self.run_community_finding_algorithm()
            self.nb_communities = int(self.community.getNodeMax() + 1)
            self.build_communities()
            self._standardize_community_names_()
            self.collect_community_names()
            self.compute_neighbor_communities()

            C = self.compute_community_vector()
            print(f'Community vector\n {C}')
            M = self.compute_community_matrix()
            print(f'Community matrix\n {M}')
            for node in self.graph.getNodes():
                if len(self.neighbor_communities[node]) > 0:
                    node_vector = self.compute_node_vector(node)
                    print(f'Node {node.id} vector {node_vector}')
                    V = np.multiply(node_vector, C)
                    broker_score[node] += V.dot(M.transpose())[
                        int(self.community[node])
                    ]
        for node in self.graph.getNodes():
            broker_score[node] /= nb_iterations
        # cleanup
        for sub in self.graph.getSubGraphs():
            self.graph.delSubGraph(sub)
        return True


# The line below does the magic to register the plugin into the plugin database
# and updates the GUI to make it accessible through the menus.
tulipplugins.registerPluginOfGroup(
    "BrokerScore",
    "Broker score",
    "G.M.",
    "22/12/2023",
    "Computes the broker score of nodes as defined by Paquet-Clouston & Bouchard",
    "1.0",
    "Graph",
)
