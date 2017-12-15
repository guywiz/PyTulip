# PyTulip

## Make Simple Count

This plugin "simplifies" the topology of the given graph: multiple edges between any two nodes
are aggregated to form a sinlge edge. The plug allows counting the number of edges that were
aggregated, thee values begin stored in a metric provided as parameter.

The same metric can also hold edge weights prior to edge aggregation. Edges in the resulting graph
then hold a weight corresponging to the sum of weights of the aggregated edges.

The author wishes to thank Quentin Rossy (ESC -- UNIL, Lausanne, CH) for suggesting the design of this topology update plugin.

## Merge Subgraphs

This plugin merges subgraphs into a single subgraph. Subgaphs to be merged are selected based on their names.
A subgraph gets selected when its name contains a substring part of a lists of substrings provided by the user
as part of the plugin parameters.

The author wishes to thank Quentin Rossy (ESC -- UNIL, Lausanne, CH) for suggesting the design of this topology update plugin.
