from tulip import *
from sympy import *
from GraphUtils import *
from Queue import *

class OneModeProjection(object):
    '''
    this class implements Z. Neal's technique for computing
    a one mode projection of a bipartite network

    we agree to distinguish nodes by assinging them a type
    stored in a string property
    for convenience we call nodes either substrates or catalysts
    to distinguish these two types
    substrates are those nodes of the indicated type
    '''
    
    def __init__(self, graph, nodeType, alphas = [0.01]):
        self.graph = graph
        self.type = self.graph.getStringProperty('type')
        self.name = self.graph.getStringProperty('name')

        self.plainOneModeGraph = self.graph.getSuperGraph().addSubGraph('plainOneMode_country')
        self.substrateType = nodeType
        self.strength = self.plainOneModeGraph.getDoubleProperty('Neal strength')

        self.nbCatalysts = 0
        for node in self.graph.getNodes():
            if self.type[node] != self.substrateType:
                self.nbCatalysts += 1

        self.alphas = alphas
        
        for node in self.graph.getNodes():
            if self.type[node] == self.substrateType:
                self.plainOneModeGraph.addNode(node)
        
        self.neighborSets = {}
        self.probabilities = {}
        self.utils = GraphUtils()
        
    def computeNeighborSets(self):
        for node in self.graph.getNodes():
            if self.type[node] == self.substrateType:
                neighbors = []
                for neigh in self.graph.getInOutNodes(node):
                    neighbors.append(neigh.id)
                self.neighborSets[node.id] = frozenset(neighbors)

    def probability(self, P1, P2, C):
        E = self.nbCatalysts        
        p = 1.0
        p *= binomial(E, C)
        p *= binomial(E - C, P1 - C)
        p *= binomial(E - P1, P2 - C)
        p /= binomial(E, P1)
        p /= binomial(E, P2)
        return p
    
    def cumulProbability(self, P1, P2, C):
        s = 0.0
        for c in range(C+1):
            s += self.probability(P1, P2, c)
        return s

    def inverseCPF(self, P1, P2, alpha):
        '''
        (CPF stands for cumulatice probability function)
        determine C such that the probability that
        P1 and P2 share C common neighbors or less is at least alpha
        '''
        C = min(P1, P2) + 1
        cumulProb = 0.0
        while cumulProb < alpha:
            C -= 1
            cumulProb += self.probability(P1, P2, C)
        return C + 1

    def induceEdge(self, node1, node2):
        try:
            set1 = self.neighborSets[node1.id]
        except KeyError:
            print node1, self.type[node1], self.name[node1]
        P1 = len(set1)
        set2 = self.neighborSets[node2.id]
        P2 = len(set2)
        intersection = set1.intersection(set2)
        C = len(intersection)
        for i in range(len(self.alphas)):
            alpha = self.alphas[i]
            oneModeGraph = self.oneModeGraphs[i]
            if C >= self.inverseCPF(P1, P2, alpha):
                edge = self.utils.findEdge(node1, node2, oneModeGraph)
                #print edge
                if edge == None:
                    edge = oneModeGraph.addEdge(node1, node2)
                    self.strength[edge] = self.cumulProbability(P1, P2, C)
                    label = '(' + str(node1.id) + ', ' + str(node2.id) + ', ' + str(self.inverseCPF(P1, P2, alpha)) + ')'
                    self.invCPFProperty[edge] = label
        
    def plainProjection(self):
        '''
        take all pairs of distance-2 neighbors of type A
        (connected through a type B common neighbor)
        induce an edge between nodes in a unimode (type A) graph
        '''
        visited = set()
        queue = Queue()

        '''
        find a node of proper type
        '''
        for node in self.sandBoxGraph.getNodes():
            if self.type[node] == self.substrateType:
                queue.put(node)
                break

        nbProcessedEdges = 0
        while not queue.empty():
            node1 = queue.get()
            visited.add(node1.id)
            if len(visited) % 10 == 0:
                print 'processed ' + str(len(visited)) + ' substrate nodes'
            for node in self.sandBoxGraph.getInOutNodes(node1):
                for node2 in self.sandBoxGraph.getInOutNodes(node):
                    if node2.id not in visited:
                        queue.put(node2)
                        edge = self.utils.findEdge(node1, node2, self.plainOneModeGraph)
                        if edge == None:
                            edge = self.plainOneModeGraph.addEdge(node1, node2)
                        nbProcessedEdges += 1

    def computeEdgeStrength(self, node1, node2):
        set1 = self.neighborSets[node1.id]
        P1 = len(set1)
        set2 = self.neighborSets[node2.id]
        P2 = len(set2)
        intersection = set1.intersection(set2)
        C = len(intersection)
        strength = 0
        for k in range(C+1):
            strength += self.probability(P1, P2, k)
        return strength

    def projectNeal(self, alphas):
        '''
        this is Zachary Neal's trick
        
        take all pairs of distance-2 neighbors of type A
        (connected through a type B common neighbor)
        if number of common neighbors (of type B)
        is at lest equal to inverseCPF(alpha)
        induce an edge between nodes in a unimode (type A) graph
        '''
        visited = set()
        queue = Queue()

        '''
        find a node of proper type
        '''
        for node in self.sandBoxGraph.getNodes():
            if self.type[node] == self.substrateType:
                queue.put(node)
                break

        nbProcessedEdges = 0
        while not queue.empty():
            substrate1 = queue.get()
            visited.add(substrate1.id)
            if len(visited) % 10 == 0:
                print 'processed ' + str(len(visited)) + ' substrate nodes'
            for catalyst in self.sandBoxGraph.getInOutNodes(substrate1):
                for substrate2 in self.sandBoxGraph.getInOutNodes(catalyst):
                    if substrate2.id not in visited:
                        queue.put(substrate2)        
                        self.induceEdge(substrate1, substrate2, alpha)
                        nbProcessedEdges += 1
        
    def efficientProject(self):
        '''
        parse all nodes of type 'not substrate'
        for each,
        grab their neighbors (they are of type 'substrate')
        build a clique (add all missing edges, as some might already be there)
        '''
        denom = self.graph.numberOfNodes() - self.plainOneModeGraph.numberOfNodes()
        numer = 0
        percentProcessedNodes = 0.0
        for node in self.graph.getNodes():
            if self.type[node] != self.substrateType:
                numer += 1
                for neigh1 in self.graph.getInOutNodes(node):
                    for neigh2 in self.graph.getInOutNodes(node):
                        if neigh1.id != neigh2.id:
                            edge = self.utils.findEdge(neigh1, neigh2, self.plainOneModeGraph)
                            if edge == None:
                                edge = self.plainOneModeGraph.addEdge(neigh1, neigh2)
                            self.strength[edge] = self.computeEdgeStrength(neigh1, neigh2)
            newPercentProcessedNodes = round(float(numer)/denom * 100)
            if newPercentProcessedNodes > percentProcessedNodes:
                percentProcessedNodes = newPercentProcessedNodes
                print 'Processed ', percentProcessedNodes, '% nodes, (', numer, ' non substrate) nodes'

    def efficientNealProject(self):
        for i in range(len(self.alphas)):
            alpha = self.alphas[i]
            print '   Computing Neal projection' + str(alpha)
            nodeSet = set()
            self.plainOneModeGraph.getBooleanProperty('select')              
            for edge in self.plainOneModeGraph.getEdges():
                node1 = self.plainOneModeGraph.source(edge)
                set1 = self.neighborSets[node1.id]
                P1 = len(set1)
                node2 = self.plainOneModeGraph.target(edge)
                set2 = self.neighborSets[node2.id]
                P2 = len(set2)
                intersection = set1.intersection(set2)
                C = len(intersection)
                
                if C >= self.inverseCPF(P1, P2, alpha):
                    nodeSet.add(node1)
                    nodeSet.add(node2)

            subGraph = self.plainOneModeGraph.inducedSubGraph(nodeSet)
            subGraph.setName('plainOneMode_country_' + str(alpha))
            print '   Finished - Computing Neal projection' + str(alpha)
                
def  main(graph):	
        omp = OneModeProjection(graph, 'country', [0.1, 0.05, 0.02, 0.01])
        #print 'Computing neighboour sets'
        omp.computeNeighborSets()
        #print 'Finished - Computing neighboour sets'
        print 'Computing plain projection'
        omp.efficientProject()
        print 'Finished - Computing plain projection'
        print 'Computing Neal projection'
        omp.efficientNealProject()
        #print 'Computing Neal projection'
        #omp.plainProjection()
        #omp.project(0.05)   
