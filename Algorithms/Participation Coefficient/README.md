# Participation coefficient

Computes the participation coefficient of nodes as defined by R. Guimera in the papers:

Guimera, R., Mossa, S., Turtschi, A., & Amaral, L. N. (2005).
The worldwide air transportation network: Anomalous centrality, community structure, and cities' global roles. Proceedings of the National Academy of Sciences, 102(22), 7794-7799.

and

Guimera, R., & Amaral, L. A. N. (2005). Cartography of complex networks: modules and universal roles. Journal of Statistical Mechanics: Theory and Experiment, 2005(02), P02001.

This is a meso level statistics requiring and depending on a community structure of the graph. Because community structures may not be stable, the routine iteratively calls the Leiden community finding algorithm before computing a ratio reflecting how much a node connects to other communities in a diverse manner.