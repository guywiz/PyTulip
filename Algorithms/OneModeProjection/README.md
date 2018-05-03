# One Mode Projection
Computes a projection of a two mode network onto a one mode network (selecting entities of a given type).

Starts from a two-mode network, project onto a one-mode network. Entities on which projection is performed must be specified as a string parameter. An existing node type string property is assumed (must be specified as part of the plugin parameters).

--

The **OneModeProjetion** class implements the projection of two-mode networks (type A and B nodes) onto one-mode networks (type A nodes),
with different possible weighting schemes:

*   uniform weights equal to 1 for all edges (same as assigning no weight ...)

*   Giatsidis, borrowed from:

	Giatsidis, C., D. M. Thilikos, et al. (2011)
	Evaluating Cooperation in Communities with the k-Core Structure.
	Advances in Social Networks Analysis and Mining (ASONAM), 87-93.

   where each type B node u contributes each projected edge a weight of 1/deg(u)

*   clique, a variation on Giatsidis where each type B node u contributes each projected edge a weight of 1 / [(deg(u)*(deg(u)-1)]/2

--

The **Neal projection scheme**, implemented in the Neal_OneModeProjetion class, visits all pairs of substrates (those nodes we project onto) and computes a _probability_ that they get connected in the one-mode graph. 

Roughly, codes that share lots of common catalysts (those nodes of the "other" type) get a higher probability of being connected, only if overall they are not individually connected to lots and lots of catalysts -- otherwise the fact that they connect would only be luck, that is, a side effect of the fact that they ech have a high number of neighbours in the two mode graphs.