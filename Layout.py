def layout(graph):
    """Determine optimal (in some sense) physical positions for
    nodes on a graph."""

    # Need true height of graph for vertical positioning:
    graphHeight = graph.getGraphHeight()

    # Each leaf gets its own "slot":
    leaves = graph.getLeafList()
    dx = 1.0/(len(leaves)-1)

    for n, leaf in enumerate(leaves):
        leaf.setPosition((n*dx, leaf.getHeight()/graphHeight))

    # Positions of parents are defined in terms of positions of children
    # (obviously this is only well-specified if graph is in fact a tree)

    for startNode in graph.getStartNodes():
        layoutSubGraph(startNode, graphHeight)


def layoutSubGraph(node, graphHeight):

    if node.isLeaf():
        return node.getPosition()[0]

    xPos = 0.0
    for child in node.getChildren():
        xPos += layoutSubGraph(child, graphHeight)

    xPos /= len(node.getChildren())
    node.setPosition((xPos, node.getHeight()/graphHeight))

    return xPos
