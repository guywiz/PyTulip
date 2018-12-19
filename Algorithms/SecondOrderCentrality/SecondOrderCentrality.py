
# -*- coding:utf-8 -*-

from tulip import *
from random import *
from math import *

class RandomWalk(object):
    '''
    implements the core structure of a random walk
    acts as a mother class for specialized subroutines

    makes no special assumptions on the graph
    the walk goes over
    '''
    def __init__(self, graph):
        super(RandomWalk, self).__init__()
        self.graph = graph
        self.previousNode = None
        self.activeNode = None
        self.previousNode = None

        self.selectInitNode()
        self.tick = 0

    def randomWalk(self, nbSteps):
        '''
    this is the core function inherited by subclasses
    running the walk

    should not be overriden, just use as is
    uses all dependent sub-routines
        '''
        stepper = self.randomStep()
        while self.tick < nbSteps:
            self.activeNode = stepper.send(None)
            self.updateInfo()
            self.previousNode = self.activeNode

    def randomStep(self):
        while True:
            self.selectNeighbor()
            yield self.activeNode

    def updateInfo(self):
        '''
        updates a node's local information directly related
        to what the walk is meant to compute
        this method is a stub that sould be overriden
        by the subclass

        note: updateInfo is responsible for managing ticks
        as this may depend on the walk specificities
        '''
        self.tick += 1
        return None

    def selectInitNode(self):
        '''
        selects a node from which the walk is initiated
        the node is chosen acccording to some process
        that's psecific to the subclass

        this method is a stub that sould be overriden
        by the subclass
        '''
        self.activeNode = self.graph.getOneNode()

    def selectNeighbor(self):
        '''
        selects a neighbor of the active node
        the node is chosen acccording to some process
        that's specific to the subclass

        this method is a stub that sould be overriden
        by the subclass
        '''
        neighbors = [neigh for neigh in self.graph.getInOutNodes(self.activeNode) ]
        self.activeNode = neighbors[randint(0, len(neighbors)-1)]

class PlainWalk(RandomWalk):
    '''
    Plain walk on a graph,  chossing neighbor uniformy at random
    The walk obviously converges towards the degree of nodes
    '''
    def __init__(self, graph):
        super(PlainWalk, self).__init__(graph)
        self.frequency = self.graph.getIntegerProperty('freq')

    def updateInfo(self):
        self.frequency[self.activeNode] += 1

class SecondOrderCentrality(RandomWalk):

    def __init__(self, graph):
        super(SecondOrderCentrality, self).__init__(graph)
        self.nbSteps = 0
        self.tickVector = self.graph.getIntegerVectorProperty('tickVector')

    def updateInfo(self):
        if self.activeNode != self.previousNode:
            L = self.tickVector[self.activeNode]
            L.append(self.tick)
            self.tickVector[self.activeNode] = L
            self.tick += 1
        self.nbSteps += 1
        if (self.nbSteps + 1) % 1000 == 0:
            print('... step ', self.nbSteps + 1)        

    def selectInitNode(self):
        '''
        finds a node that has viewSelection to True
        if None, selects a node at random
        '''
        select = self.graph.getBooleanProperty('viewSelection')
        for node in self.graph.getNodes():
            if select[node]:
              self.activeNode = node
        if self.activeNode == None:
            N = self.graph.numberOfNodes()
            nodes = list(self.graph.getNodes())
            self.activeNode = nodes[randint(0, N - 1)]

    def selectNeighbor(self):
        neighbors = list(self.graph.getInOutNodes(self.activeNode))
        selectedNeighbor = neighbors[randint(0, len(neighbors)-1)]
        ratio = float(self.graph.deg(self.activeNode)) / float(self.graph.deg(selectedNeighbor))
        if random() < ratio:
            self.activeNode = selectedNeighbor

def main(graph):
    print 'Processing graph ' + graph.getName()
    soc = SecondOrderCentrality(graph)
    print('Walking', 25*graph.numberOfEdges())
    soc.randomWalk(25*graph.numberOfEdges())
    property = graph.getDoubleProperty('second order centrality')
    print('Computing second order centrality')
    for n in graph.getNodes():
        V = graph['tickVector'][n]
        L = V[0:len(V)-1]
        LL = V[1:len(V)]
        deltas = map(lambda x: x[1]-x[0], zip(L, LL))
        mean = sum(deltas)/len(deltas)
        stddev = sqrt(sum(map(lambda x: (x-mean)**2, deltas)) / len(deltas))
        property[n] = stddev
