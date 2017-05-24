# Simmelian backbone

Computes the backbone subgraph of a simple non-directed graph following Bobo Nick's algorithm

  * Nick, B., C. Lee, et al. (2013). Simmelian Backbones: Amplifying Hidden Homophily in Facebook Networks.
    Advances in Social Network Analysis and Mining (ASONAM).

  * Uses an optional argument (name of a double property) that stores edge strength.
  * Edge strength is used to sort edges (from highest strength -- strongest edges first -- down to weakest edges). Edge strength is either based on a user-defined property, or it is computed based on number of common neighbors of incident nodes, as suggested by Nick.
    * A first parameter then indicates how many edges will be considered (when computing edge redundancy), thus putting the focus on the k strongest edges.
  * Implements the parametric and non-parametric versions of edge redundancy (see paper for details).
    * Parametric version requires a fixed number of common neighbors between incident nodes of an edge -- for the edge to qualify as being part of the backbone.
    * Non-parametric version goes through strongest edges, considering the strongest, then the 2 strongest, up to all k strongest edges each time computing a Jaccard measure, thus ending with a sequences of values j1, j2, ..., jk. The non -parametric redundance measure is then max(j1, ..., jk) 

  * The selected redundancy value is thus specified either as an integer (parametric) or real x in [0, 1] value (no parametric). The plugin thus needs to distinguish these two cases.

