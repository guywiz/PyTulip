# Broker Score
This script offers an alternative to Paquet-Clouston an Bouchard `python` package computing their meso level broker score defined on nodes of a network. Please refer to their paper:

Paquet-Clouston, M., & Bouchard, M. (2023). A Robust Measure to Uncover Community Brokerage in Illicit Networks. _Journal of Quantitative Criminology_, 39(3), 705-733.

or to [their GitHub repository](https://github.com/Masarah/community_broker_score) for code relying on `pandas` dataframes and `networkx` to store network data and compute the score. Our approach alternatively relies on [`tulip-python`](https://pypi.org/project/tulip-python/), a python binding of the [C++ Graph Visualization framework Tulip](https://tulip.labri.fr/).

Our code follows from the reformulation of Paquet-Clouston and Bouchard formula as a vector and matrix product. The measure can be obtained by computing a matrix

$$M = \left[ \begin{matrix} 1 & 0 \\ 0 & 1 \end{matrix} \right]$$

The main class `BrokerScore` implements all necessary methods, partly relying on the `Dijkstra` class to run a dfs and compute a community cohesion score. In order to stick with Paquet-Clouston and Bouchard definition of cohesion, we invoke networkX average path length routine which requires to convert from Tulip into the iGraph format.

The score is computed in a matter of (tenth of a) seconds for graph containing thousands of nodes and edges and even faster for smaller graphs.

## Using the script from within Tulip
You may either use the code as a script, which will load a plugin after it is run. You then need to invoke the plugin through the GUI, paying attention to the parameters the plugin needs to properly run. Another avenue is to invoke the pluging through a script, typically in the main function:
```
def main(graph):
    params = tlp.getDefaultPluginParameters('Broker score', graph)
    community = graph.getIntegerProperty('community')
    params['communities'] = community
    broker = graph.getDoubleProperty('broker_score')
    params['result'] = broker
    graph.applyDoubleAlgorithm('Broker score', broker, params)
```
Note that the BrokerScore class can be used to build a sub-network (induced subgraph) solely consisting of brokers. The construct can be iterated, as not all brokers act as broker iin the broker network. The iteration ultiately ends, giving rise to a hierarchyof sub-networks.

## Dependencies
The BrokerScore class depends on a set of libraries that should be installed using the accompanying `requirements.txt` file. Note that versions have not been tightfully checked and my depend on how these third party libraries evolve.


