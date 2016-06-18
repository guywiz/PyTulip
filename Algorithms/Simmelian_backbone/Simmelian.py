
from tulip import *

class Simmelian(object):
    '''
    computes the Simmelian backbone of a non-directed graph according to Bobo Nick's approach:
    Nick, B., C. Lee, et al. (2013). Simmelian Backbones: Amplifying Hidden Homophily in Facebook Networks.
    Advances in Social Network Analysis and Mining (ASONAM).

    Implements the non parametric version of edge redundancy (see paper for details).

    Uses an optional double property argument (that stores edge strength).
    '''
    def __init__(self, graph, strength_name_property=None):
        super(Simmelian, self).__init__()
        self.graph = graph
        self.strength_name_property = strength_name_property
        self.ranked_edges = {}
        self.rank_edges()
        self.edge_redundancy = self.graph.getDoubleProperty('edge_redundancy')

    def compute_edge_strength(self, node):
        '''
        computes edge strength, if no double property is assigned
        edges are those incident to node
        (edge strength is not defined globally but locally to nodes)
        (see Bobo Nick's paper for details)
        '''
        if self.strength_name_property != None:
            self.edge_strength = self.graph.getDoubleProperty(self.strength_name_property)
            return
        self.strength_name_property = 'edge_strength'
        self.edge_strength = self.graph.getDoubleProperty(self.strength_name_property)
        for e in self.graph.getInOutEdges(node):
            ego = self.graph.source(e)
            alter = self.graph.target(e)
            ego_neighs = self.graph.getInOutNodes(ego)
            alter_neighs = self.graph.getInOutNodes(alter)

            mutuals = list(set(ego_neighs) & set(alter_neighs))
            # strength corresponds to the number of common neighbors
            self.edge_strength[e] = len(mutuals)

    def edge_compare(self, edge1, edge2):
        '''
        compares edges according to their strength
        -- used as a parameter function to sort edges

        edges are necessarily incident to a same node
        '''
        if self.edge_strength[edge1] > self.edge_strength[edge2]:
            return -1
        elif self.edge_strength[edge1] < self.edge_strength[edge2]:
            return 1
        else:
            return 0

    def rank_edges(self):
        for node in self.graph.getNodes():
            self.compute_edge_strength(node)
            edges = self.graph.getInOutEdges(node)
            self.ranked_edges[node] = sorted(edges, cmp=self.edge_compare)

    def Jaccard(self, set1, set2):
        return float(len(set1.intersection(set2)))/float(len(set1.union(set2)))

    def incident_nodes(self, node, m):
        '''
        computes the set of incident vertices from m strongest ties attached to a node
        returns an ordered list of nodes
        '''
        incident_edges = self.ranked_edges[node][0:m]
        incident_nodes = []
        for e in incident_edges:
            if self.graph.source(e) == node:
                incident_nodes.append(self.graph.target(e))
            else:
                incident_nodes.append(self.graph.source(e))
        return incident_nodes

    def compute_edge_redundancy(self, max_rank, parametric=False):
        for e in self.graph.getEdges():
            ego = self.graph.source(e)
            alter = self.graph.target(e)

            ego_ranked_edges = self.ranked_edges[ego]
            alter_ranked_edges = self.ranked_edges[alter]

            if parametric:
                s_ego = set(self.incident_nodes(ego, max_rank))
                s_alter = set(self.incident_nodes(alter, max_rank))
                r = len(s_ego.intersection(s_alter))
            else:
                r = 0.0
                for k in range(1, max_rank + 1):
                    s_ego = set(self.incident_nodes(ego, k))
                    s_alter = set(self.incident_nodes(alter, k))
                    r = max(r, self.Jaccard(s_ego, s_alter))
            self.edge_redundancy[e] = r

    def simmelian_backbone(self, max_rank, redundancy_min_threshold):
        '''
        computes the Simmelian backbone according to a maximum rank for edges,
        that is redundancy will be computed but only for edges with rank below max_rank
        redundancy threshold x lies in [0, 1], and makes it so that only x% of edges
        are kept as part of the backbone
        '''
        parametric = True
        if redundancy_min_threshold >= 1.0:
            # parametric case
            min_redundancy = redundancy_min_threshold
            self.compute_edge_redundancy(max_rank, True)
        else:
            # non parametric, min_threshold in [0, 1]
            self.compute_edge_redundancy(max_rank, False)
            redundancy_values = sorted([self.edge_redundancy[e] for e in self.graph.getEdges()])
            min_redundancy = redundancy_values[int((1.0 - redundancy_min_threshold) * len(redundancy_values))]

        sg = self.graph.addCloneSubGraph()
        sg.setName('Simmelian_maxrank_' + str(max_rank) + '_redundancymin_' + str(min_redundancy))

        for e in self.graph.getEdges():
            # On retire les aretes dont le rang est trop eleve et/ou la redondance trop faible
            if self.edge_redundancy[e] < min_redundancy:
                sg.delEdge(e)

def main(graph):
    #sb = Simmelian(graph, 'edge_strength')
    sb = Simmelian(graph, 'Disimilarity')

    max_rank = 20
    min_redundancy = 7

    sb.simmelian_backbone(max_rank, min_redundancy)

