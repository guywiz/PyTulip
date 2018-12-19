# Second order centrality

Computes the second order centrality of nodes as defined in:

  * Kermarrec, A.-M., et al. (2011). "Second order centrality: Distributed assessment of nodes criticity in complex networks." Computer Communications 34(5): 619-628.

  * Uses a set of classes:
    * The RandomWalk class implements a generic random walk on a graph and relies on python's yield mechanism. It also uses a dedicated select_neighbour method that is superseeded by subclasses.
  * PlainWalk is used merely for testing purpose.
  * Subclasses need to implement a updateInfo method collecting values generated during the walk.
    * These info can then be used to compute whatever metric on nodes after the walk is over.

Second order centrality relies on a simple idea that, on average, central node experience a higher variation between timestamps at which they are visited.
