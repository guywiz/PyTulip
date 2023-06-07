from tulip import *

class DFS(object):
	"""
	This class implements a DFS traversal of a graph in search
	for all simple paths connecting two given nodes,
	optionally requiring that end nodes satisfy a given constraint
	(having a specific property, not belonging to a given type, etc.)

	This class was implemented in teh context of deriving a social network
	(of persons) from a multivariate graph.. Paths were required to have
	their end points to be persons, while inner nodes would not.

	Bruno Pinaud, Maud Bénichou, Guy Melançon (2023).
	Extraction d'un réseau social criminel par transformation d'un graphe d'enquête multivarié.
	Extraction et Gestion des Connaissances (EGC), Revue RNTI (E-39), pp.151-162.
	⟨hal-03929950⟩
	"""
	def __init__(self, graph, start_node, end_node, constraint = lambda x: True):
		super(DFS, self).__init__()
		self.graph = graph
		self.start_node = start_node
		self.end_node = end_node
		self.constraint = constraint
		self.visited = self.graph.getBooleanProperty('visited')
		self.visited.setAllNodeValue(False)
		self.currentPath = []
		self.simplePaths = []

	def _DFS_(self, u, v):
		if self.visited[u]:
			return
		self.visited[u] = True
		self.currentPath.append(u)
		if u == v:
			self.simplePaths.append(self.currentPath[:])
			self.visited[u] = False
			self.currentPath.pop()
			return
		for w in self.graph.getInOutNodes(u):
			if self.constraint(w):
				if not self.visited[w]:
					self._DFS_(w, v)
			else:
				if w == v:
					if not self.visited[w]:
						self._DFS_(w, v)
		self.currentPath.pop()
		self.visited[u] = False

	def _find_edge_(self, source, target):
		for e in self.graph.getInOutEdges(source):
			opposite_node = self.graph.opposite(e, source)
			if opposite_node == target:
				return e
			
	def _fill_in_edges_(self, path):
		path_with_edges = []
		for i in range(len(path) - 1):
			source = path[i]
			target = path[i+1]
			e = self._find_edge_(source, target)
			path_with_edges.append(source)
			path_with_edges.append(e)
		path_with_edges.append(target)
		return path_with_edges

	def reset(self, new_start_node, new_end_node):
		self.start_node = new_start_node
		self.end_node = new_end_node
		self.visited.setAllNodeValue(False)
		self.currentPath = []
		self.simplePaths = []

	def reset_constraint(self, constraint):
		self.constraint = constraint

	def getSimplePaths(self):
		self._DFS_(self.start_node, self.end_node)
		return list(map(self._fill_in_edges_, self.simplePaths))
	
