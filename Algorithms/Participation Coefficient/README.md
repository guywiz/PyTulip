# Participation coefficient

Computes the participation coefficient of nodes as defined by R. Guimera in the papers:

Guimera, R., Mossa, S., Turtschi, A., & Amaral, L. N. (2005).
The worldwide air transportation network: Anomalous centrality, community structure, and cities' global roles. Proceedings of the National Academy of Sciences, 102(22), 7794-7799.

and

Guimera, R., & Amaral, L. A. N. (2005). Cartography of complex networks: modules and universal roles. Journal of Statistical Mechanics: Theory and Experiment, 2005(02), P02001.

This is a meso level statistics requiring and depending on a community structure of the graph. Because community structures may not be stable, the routine iteratively calls the Leiden community finding algorithm before computing a ratio reflecting how much a node connects to other communities in a diverse manner.

## Installing and using the plugin

The library relies on [`tulip-python`](https://pypi.org/project/tulip-python/), a python binding of the [C++ Graph Visualization framework Tulip](https://tulip.labri.fr/). Tulip also comes as a GUI.

Several libraries need to be installed prior to using the plugin, that can for instance be installed running `poetry install --no-root`. A simple test script can optionally be run.

The plugin itself is typically used as:
```
# assuming a graph as already been defined
params = tlp.getDefaultPluginParameters('Participation Coefficient', graph)
community = graph.getIntegerProperty('community')
params['communities'] = community
particip = graph.getDoubleProperty('participation')
params['result'] = particip
graph.applyDoubleAlgorithm('Broker score', particip, params)
```
Alternatively, the plugin may be used within the Tulip GUI after the script has been loaded and ran.