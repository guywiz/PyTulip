from tulip import *
import tulipplugins

class Simmelian_Backbone(tlp.Algorithm):
    '''
    Computes the Simmelian backbone of a non-directed graph according to Bobo Nick's approach:
    Nick, B., C. Lee, et al. (2013). Simmelian Backbones: Amplifying Hidden Homophily in Facebook Networks.
    Advances in Social Network Analysis and Mining (ASONAM).

    Implements the non parametric version of edge redundancy (see paper for details).

    Uses an optional double property argument (that stores edge strength).
    '''

    def __init__(self, context):
        tlp.Algorithm.__init__(self, context)
        # you can add parameters to the plugin here through the following syntax
        # self.add<Type>Parameter("<paramName>", "<paramDoc>", "<paramDefaultValue>")
        # (see documentation of class tlp.WithParameter to see what types of parameters are supported)
        self.addDoublePropertyParameter("Edge strength", "Property from which edge strength is inferred", "viewMetric")
        self.addIntegerParameter("Max rank", "Number of edges used to compute redundancy", "10")
        self.addFloatParameter("Min redundancy", "(Redundancy) Threshold used to filter out edges in graph", "7")

    def compute_edge_strength(self):
        for e in self.graph.getEdges():
            ego = self.graph.source(e)
            alter = self.graph.target(e)
            ego_neighs = self.graph.getInOutNodes(ego)
            alter_neighs = self.graph.getInOutNodes(alter)

            mutuals = list(set(ego_neighs) & set(alter_neighs))
            # strength corresponds to the number of common neighbors
            self.edge_strength[e] = len(mutuals)

            print('Strength edge', e, ':', self.edge_strength[e])

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
            edges = self.graph.getInOutEdges(node)
            self.ranked_edges[node] = sorted(edges, key=lambda x: - self.edge_strength[x]) # cmp=self.edge_compare)

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

        self.edge_strength = self.dataSet['Edge strength']
        if self.edge_strength.getEdgeMax() == 0.0:
            # non parametric approach
            print('Non parametric')
            self.compute_edge_strength()

        max_rank = self.dataSet['Max rank']
        min_redundancy = self.dataSet['Min redundancy']

        self.ranked_edges = {}
        self.rank_edges()
        self.edge_redundancy = self.graph.getDoubleProperty('edge_redundancy')

        self.simmelian_backbone(max_rank, min_redundancy)

        return True

# The line below does the magic to register the plugin to the plugin database
# and updates the GUI to make it accessible through the menus.

tulipplugins.registerPluginOfGroup("Simmelian_Backbone", "Simmelian Backbone", "Guy Melancon", "6/11/2016", "", "1.0", "Two_mode_Networks")
