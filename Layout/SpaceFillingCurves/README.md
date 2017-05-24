# Space Filling Curves

Computes an embedding of a graph onto a fractal space filling curve. These layouts actually implement the original pixel-oriented approach by Keim.

*   Keim, D. A. (2000). "Designing pixel-oriented visualization techniques: theory and applications." IEEE Transactions on Visualization and Computer Graphics 6(1): 59-78.

In this setting, only the graph's nodes and attributes are used. Edges are simply ignored. That being said, these layouts would typically be used on multi-dimensional data loaded into Tulip as graphs where nodes hold attributes and without any edge.

The code is organized into a higher level class implemting the generic routine of mapping nodes onto the curve.

The curve itself is specified in a subclass as a L-system. The total order used to map nodes onto the curve is given as a parameter to the class. In case the order follows from a sophisticated algorithm, it should be computed priori to instanciting the class and stored into a node property (integer, double or string).