# distribution packages
import numpy as np
import pandas as pd
import networkx as nx
from tulip import tlp
from graph_converter import *
import leidenalg

# local package
from Dijkstra import *

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

class BrokerScore:
    def __init__(
        self, graph, community_property_name, score_property_name="broker_score"
    ):
        print('-----')
        print(graph)
        print(community_property_name)
        print(score_property_name)
        print('-----')
        self.graph = graph
        self.community_property_name = community_property_name
        self.score_property_name = score_property_name
        # check whether the graph already stores a property for node communities
		# if not, compute communities
        communities_exist = self.graph.existProperty(self.community_property_name)
        print(f'Communities exist: {communities_exist}')
        self.community = self.graph.getLocalDoubleProperty(community_property_name)
        if not communities_exist:
            self.run_community_finding_algorithm()
        self.neighbor_communities = {}
        self.neighbor_communities_property = self.graph.getStringVectorProperty(
            "neighbor_communities"
        )
        # instantiate communities as subgraphs
		# check whether communities have already been instanciated as subgraphs
		# no fancy stuff here, if there are subgraphs assume everything works fine
		# no name checking or number of subgraphs etc.
		# its all or nothing
        test_community = len(list(self.graph.getSubGraphs())) > 0
        if not test_community:
            print('Need to build communities as subgraphs')
            self.build_communities()
        else:
            print('Communities already instanciated as subgraphs')
        self.collect_community_names()
        
    def _standardize_community_names_(self):
        # normalize community names (subgraphs)
        # we assume subgraphs have been named by the Equal value plugin
        # (using its input metric name)
        # !!! and that communities are labelled using consecutive integers starting from 0 !!!
        print()
        print('_standardize_community_names_', [sub.getName() for sub in self.graph.getSubGraphs()])
        for sub in self.graph.getSubGraphs():
            # for what its worth, when using EqualValue, subgraphs are named using 
            # the property name and metric (integer) values, using colon ":"
            if not ':' in sub.getName():
                return
            else:
                sub.setName(f'{self.community_property_name}_{sub.getName().split(":")[1].strip()}')

    def build_communities(self):
        params = tlp.getDefaultPluginParameters("Equal Value", self.graph)
        params["property"] = self.community
        self.graph.applyAlgorithm("Equal Value", params)
        self._standardize_community_names_()

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
        print()
        print('collect_community_names', [sub.getName() for sub in self.graph.getSubGraphs()])
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
                # happens if a community reduces to a single noe
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

    def to_dataframes(self):
        nodes_df = pd.DataFrame(
            {
                "node_id": [node.id for node in self.graph.getNodes()],
                "community": [
                    int(self.community[node]) for node in self.graph.getNodes()
                ],
            }
        )
        edges_df = pd.DataFrame(
            {
                "left": [self.graph.source(edge).id for edge in self.graph.getEdges()],
                "right": [self.graph.target(edge).id for edge in self.graph.getEdges()],
            }
        )
        return nodes_df, edges_df

    def compute_node_vector(self, node):
        node_vector = np.zeros(self.nb_communities)
        node_vector[int(self.community[node])] = 1
        if len(self.neighbor_communities[node]) > 0:
            for i in self.neighbor_communities[node]:
                node_vector[i] = 1
        return node_vector

    def node_brokerage_score(self):
        self.compute_neighbor_communities()
        C = self.compute_community_vector()
        M = self.compute_community_matrix()

        self.graph.getLocalDoubleProperty(self.score_property_name)
        for node in self.graph.getNodes():
            node_vector = np.zeros(self.nb_communities)
            node_vector[int(self.community[node])] = 1
            if len(self.neighbor_communities[node]) > 0:
                for i in self.neighbor_communities[node]:
                    node_vector[i] = 1
                V = np.multiply(node_vector, C)
                self.graph[self.score_property_name][node] = V.dot(M.transpose())[
                    int(self.community[node])
                ]

    def compute_broker_network(self):
        i = 0
        current_graph = self.graph
        community_property_name = f"community_{i}"
        score_property_name = f"broker_score_{i}"
        selection_property_name = f"is_broker_{i}"
        # level 0 coincides with original graph
        community_0 = current_graph.getLocalDoubleProperty(community_property_name)
        community_0.copy(self.community)

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


def main(graph):
    BS = BrokerScore(graph, "community", "broker_score")
    BS.node_brokerage_score()
    BS.compute_broker_network()
