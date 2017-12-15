# PyTulip

## Make Simple Count

This plugin "simplifies" the topology of the given graph: multiple edges between any two nodes
are aggregated to form a sinlge edge. The plug allows counting the number of edges that were
aggregated, thee values begin stored in a metric provided as parameter.

The same metric can also hold edge weights priori to edge aggregation. Edges in the resulting graph
then hold a weight correspong to the sum of weights of the aggregated edges.

The author wishes to thank Q. Rossy (ESC -- UNIL, Lausanne, CH) for suggesting the design of this topology update plugin.