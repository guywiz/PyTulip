"""
Created on 10 fevr. 2012

@author: melancon
"""

from numpy import *


class Dijkstra(object):
    """
    computes distances from a source using Dijkstra's algorithm
    optionally displays shortest path between two node

    the given graph is assumed to be connected
    """

    def __init__(self, graph):
        """
        stores the graph
        instantiates the necessary boolean properties
        """
        self.graph = graph
        self.source = None
        self.dist_to_source = self.graph.getDoubleProperty("dist_to_source")
        self.infinity = self.graph.numberOfNodes()
        self.parent = {}
        self.nodeList = [n for n in self.graph.getNodes()]

    def compute_distance_from(self, source):
        """
        distances from the given node are computed
        """
        for n in self.graph.getNodes():
            self.dist_to_source[n] = self.infinity
            self.parent[n] = None
        self.dist_to_source[source] = 0.0

        while len(self.nodeList) > 0:
            u = self.__minNode__()
            for v in self.graph.getInOutNodes(u):
                tmp_dist = self.dist_to_source[u] + self.dist_between(u, v)
                if tmp_dist < self.dist_to_source[v]:
                    self.dist_to_source[v] = tmp_dist
                    self.parent[v] = u

    def __minNode__(self):
        values = list(map(lambda x: self.dist_to_source[x], self.nodeList))
        min_value = min(values)
        min_node = self.nodeList.pop(values.index(min_value))
        return min_node

    def dist_between(self, u, v):
        """
        nodes u and v are assumed to be neighbor nodes
        """
        return 1


def main(graph):
    dijk = Dijkstra(graph)
    source = graph.getOneNode()
    dijk.compute_distance_from(source)
