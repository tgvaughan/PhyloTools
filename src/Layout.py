from random import random

def layout(graph):
    """Determine optimal (in some sense) physical positions for
    nodes on a graph."""

    # Need true height of graph for vertical positioning:
    graphHeight = graph.getGraphHeight()

    # Each leaf gets its own "slot":
    leaves = graph.getLeafList()
    dx = 1.0/(len(leaves)-1)

    for n, leaf in enumerate(leaves):
        leaf.position = (n*dx, leaf.height/graphHeight)

    # Positions of parents are defined in terms of positions of children
    # (obviously this is only well-specified if graph is in fact a tree)

    for startNode in graph.startNodes:
        layoutSubGraph(startNode, graphHeight)

    # Position branches between nodes and parents:
    for startNode in graph.startNodes:
        layoutParentBranches(startNode)


def layoutSubGraph(node, graphHeight):

    if node.isLeaf():
        return node.position[0]

    xPos = 0.0
    for child in node.children:
        xPos += layoutSubGraph(child, graphHeight)

    xPos /= len(node.children)
    node.position = (xPos, node.height/graphHeight)

    return xPos

def layoutParentBranches(node):

    nParents = len(node.parents)

    if nParents == 1:
        node.parentBranchPositions = [node.position[0]]

    else:
        if nParents > 1:

            # Determine range of allowable branch positions:
            node.parentBranchPositions = range(nParents)
            minPos = node.position[0]-0.01*(1+random())
            maxPos = node.position[0]+0.01*(1+random())
            for parent in node.getParents():
                if parent.position[0]<minPos:
                    minPos = parent.position[0]
                if parent.position[0]>maxPos:
                    maxPos = parent.position[0]

            # Obtain indices of parents sorted in order of
            # their horizontal node positions:
            pidx = range(nParents)
            pidx.sort(key=lambda x: node.getParents()[x].position[0])

            # Select parent branch positions:
            delta = (maxPos-minPos)/float(nParents - 1)
            for i,parent in enumerate(node.getParents()):
                if len(parent.children)==1:
                    node.parentBranchPositions[i] = parent.position[0]
                else:
                    node.parentBranchPositions[i] = minPos + delta*pidx[i]
                    #node.parentBranchPositions[i] = node.position[0]

            
    for child in node.children:
        layoutParentBranches(child)
