def layout(graph):
    """Determine optimal (in some sense) physical positions for
    nodes on a graph."""

    # Each leaf gets its own "slot":
    leaves = graph.getLeafList()
    dx = 1.0/(len(leaves)-1)

    for n, leaf in enumerate(leaves):
        leaf.position = n*dx

    # Positions of parents are defined in terms of positions of children
    # (obviously this is only well-specified if graph is in fact a tree)

    
