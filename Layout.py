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
        leaf.setPosition((n*dx, leaf.getHeight()/graphHeight))

    # Positions of parents are defined in terms of positions of children
    # (obviously this is only well-specified if graph is in fact a tree)

    for startNode in graph.getStartNodes():
        layoutSubGraph(startNode, graphHeight)

    # Position branches between nodes and parents:
    for startNode in graph.getStartNodes():
        layoutParentBranches(startNode)


def layoutSubGraph(node, graphHeight):

    if node.isLeaf():
        return node.getPosition()[0]

    xPos = 0.0
    for child in node.getChildren():
        xPos += layoutSubGraph(child, graphHeight)

    xPos /= len(node.getChildren())
    node.setPosition((xPos, node.getHeight()/graphHeight))

    return xPos

def layoutParentBranches(node):

    nParents = len(node.getParents())

    if nParents == 1:
        node.parentBranchPositions = [node.getPosition()[0]]

    else:
        if nParents > 1:
            node.parentBranchPositions = range(nParents)
            minPos = node.getPosition()[0]-0.01*(1+random())
            maxPos = node.getPosition()[0]+0.01*(1+random())
            for parent in node.getParents():
                if parent.getPosition()[0]<minPos:
                    minPos = parent.getPosition()[0]
                if parent.getPosition()[0]>maxPos:
                    maxPos = parent.getPosition()[0]

            delta = (maxPos-minPos)/float(nParents - 1)

            for i,parent in enumerate(node.getParents()):
                if len(parent.getChildren())==1:
                    node.parentBranchPositions[i] = parent.getPosition()[0]
                else:
                    node.parentBranchPositions[i] = minPos + delta*i
                    #node.parentBranchPositions[i] = node.getPosition()[0]

            
    for child in node.getChildren():
        layoutParentBranches(child)
