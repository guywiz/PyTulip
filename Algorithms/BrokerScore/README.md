# Broker Score
This script offers an alternative to Paquet-CLouston an Bouchard `python` package computing their broker score defined on node sof a network. Please refer to their paper:

Paquet-Clouston, M., & Bouchard, M. (2023). A Robust Measure to Uncover Community Brokerage in Illicit Networks. _Journal of Quantitative Criminology_, 39(3), 705-733.

or to [their GitHub repository](https://github.com/Masarah/community_broker_score) for code relying on `pandas` dataframes and `networkx` to store network data and compute the score. Our approach alternatively relies on [`tulip-python`](https://pypi.org/project/tulip-python/), a python binding of the [C++ Graph Visualization framework Tulip](https://tulip.labri.fr/).

Our code follows from the reformulation of Paquet-Clouston and Bouchard formula as a vector and matrix product.

The main class `BrokerScore` implements all necessary methods, partly relying on the `Dijkstra` class to run a dfs and compute a community cohesion score. In order to stick with Paquet-Clouston and Bouchard definition of cohesion, we invoke networkX average path length routine which requires to convert from Tulip into the iGraph format.

The score is computer in a matter of seconds for graph containing thousands of nodes and edges and even faster for smaller graphs.

## Using the script from within Tulip
A code snippet at the bottom of the BrokerScore class file allows the use of the code from within the Tulip desktop application. Running the script should be easy. Make sure the local hierarchy is clean and does not contain any subgraph, as the script does produce a series of subgraph and makes use of unrobust naming conventions.
```
def main(graph):
	BS = BrokerScore(graph, "community", "broker_score")
	BS.node_brokerage_score()
	BS.compute_broker_network()
```
The script also allow to also to build a sub-network (induced subgraph) solely consisting of brokers. The construct can be iterated, as not all brokers act as broker iin the broker network. The iteration ultiately ends, giving rise to a hierarchyof sub-networks.


