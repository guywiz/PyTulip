# One Mode Projection
Computes a projection of a two mode network onto a one mode network (selecting entities of a given type).

Implements the projection of two-mode networks (type A and B nodes) onto one-mode networks (type A nodes),
with different possible weighting schemes:

*   uniform weights equal to 1 for all edges (same as assigning no weight ...)

*   Giatsidis, borrowed from:

	Giatsidis, C., D. M. Thilikos, et al. (2011)
	Evaluating Cooperation in Communities with the k-Core Structure.
	Advances in Social Networks Analysis and Mining (ASONAM), 87-93.

   where each type B node u contribute each projected edge a weight of 1/deg(u)

*   clique, a variation on Giatsidis where each type B node u contribute each projected edge a weight of 1 / [(deg(u)*(deg(u)-1)]/2


Starts from a two-mode network, project onto a one-mode network. Entities on which projection is performed must be specified as a string parameter. An existing node type string property is assumed (must be specified as part of the plugin parameters).
