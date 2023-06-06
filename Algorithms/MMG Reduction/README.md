# From criminal investigation data to social network
## Reducing a multivariate multigraph through multiple edge merging and path contraction

This git repository contains a series of python scripts implementing a reduction algorithm, extracting a one-mode social network from a multivariate multigraph, that is one containing nodes and edges of multiple types.

The scripts heavily rely on [Tulip](https://tulip.labri.fr/), a `python` library offering a number of methods to handle graphs and subgraphs.

The script can be used from the command line, handling data files and directly outputting the social network in various formats.

We however recommend using it from within the Graph Visualization Framework Tulip, for which it has been specifically designed. Using the scripts with Tulip also provides additional functionalities to explore the resulting social network, as we shall explain below.


### Running the script

You first need to make sure your data is in proper format. The algorithm requires either a Tulip file
or a couple of semi-colon separated csv files (one for nodes, an done for edges):

- In both files, a column named `id` should provides nodes (and edges) a unique identification value (integer or string). Node ids and edge ids should be distinct.
- The node file may contain a column providing a `label` which can be displayed (if the graph or the resulting social network is to be visualized).
- The node file may contain a column indicating what `icon` (selected from awesome font) is to be used when displaying a node.
- Apart form the id attribute, the edge file must specify a `source` and `target` value, pointing at two valid `id`s listed in the node file.
- Edges can also have an optional `type` (not used by the algorithm but that can be useful to the user when navigating the social network together with the original multivariate multigraph. 
- The edge file should contain a column named `weight` with a nuerical value associated with each edge. If no such column is found, a uniform weight of 1 is used.
- The edge file may optionally contain a column providing a `label` which can be displayed.
