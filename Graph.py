class Node:

    def __init__(self, *parents):
        self.parents = []
        self.children = []
        self.branchLength = None
        self.height = None
        self.label = None
        self.annotation = {}
        self.position = None
        self.nDecendents = None

        for parent in parents:
            self.addParent(parent)

        # Horizontal position (set by layout engine)
        self.position = None

    def addChild(self, child):
        self.children.append(child)
        child.parents.append(self)

    def addParent(self, parent):
        self.parents.append(parent)
        parent.children.append(self)
    
    def setLabel(self, label):
        self.label = label

    def annotate(self, key, value):
        self.annotation[key] = value
    
    def setBranchLength(self, branchLength):
        self.branchLength = branchLength

    def setHeight(self, height):
        self.height = height
    
    def setPosition(self, position):
        self.position = position
    
    def isRoot(self):
        return len(self.parent)==0

    def isLeaf(self):
        return len(self.children)==0

    def getParents(self):
        return self.parents

    def getChildren(self):
        return self.children

    def getPosition(self):
        return self.position
    
    def getHeight(self):
        return self.height

    def getBranchLength(self):
        return self.branchLength

    def getSubGraphHeight(self):

        if len(self.children)==0:
            return self.height

        maxHeight = 0
        for child in self.children:
            maxHeight  =  max(child.getSubGraphHeight(), maxHeight)
        return maxHeight

    def getDecendentCount(self):

        if self.nDecendents == None:
            self.nDecendents = 0
            for child in self.getChildren():
                self.nDecendents += 1+child.getDecendentCount()

        return self.nDecendents


class Graph:
    def __init__(self, *startNodes):
        self.startNodes = list(startNodes)

    def getStartNodes(self):
        return self.startNodes

    def getNodeList(self):
        nodes = set()
        for startNode in self.startNodes:
            self.addNodesFromSubgraph(startNode, nodes)

        return list(nodes)

    def addNodesFromSubgraph(self, node, nodeSet):
        nodeSet.add(node)

        for child in node.children:
            self.addNodesFromSubgraph(child, nodeSet)

    def getGraphHeight(self):
        
        maxHeight = 0
        for startNode in self.startNodes:
            maxHeight = max(startNode.getSubGraphHeight(), maxHeight)

        return maxHeight

    def getLeafList(self):
        leavesSeen = set()
        leaves = []
        for startNode in self.startNodes:
            leaves.extend(self.getSubGraphLeaves(startNode, leavesSeen))

        return leaves

    def getSubGraphLeaves(self, node, leavesSeen):
        if len(node.children)==0 and (node not in leavesSeen):
            leavesSeen.add(node)
            return [node]
        else:
            leaves = []
            for child in node.children:
                leaves.extend(self.getSubGraphLeaves(child, leavesSeen))
            return leaves

    def reorder(self, ascending=True):
        """Sort children of each node according to their number of decendents."""

        for startNode in self.getStartNodes():
            self.reorderSubGraph(startNode, ascending)
        

    def reorderSubGraph(self, node, ascending):

        for child in node.getChildren():
            self.reorderSubGraph(child, ascending)

        node.children.sort(cmp=nodeDecCompare, reverse=not ascending)

def nodeDecCompare(nodeA, nodeB):
    diff =  nodeA.getDecendentCount() - nodeB.getDecendentCount()
    if diff == 0:
        return 0
    else:
        return diff/abs(diff)
                               
            

        
