class Node:

    def __init__(self, *parents):
        self.parents = []
        self.children = []
        self.branchLength = None
        self.height = None
        self.label = None
        self.annotation = {}

        for parent in parents:
            self.addParent(parent)

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
    
    def isRoot(self):
        if len(parent)==0:
            return True
        else:
            return False

    def isLeaf(self):
        if len(children)==0:
            return True
        else:
            return False
    
    def getHeight(self):
        return self.height
    

class Graph:
    def __init__(self, *startNodes):
        self.startNodes = list(startNodes)

    def getNodeList(self):
        nodes = set()
        for startNode in self.startNodes:
            self.addNodesFromSubgraph(startNode, nodes)

        return list(nodes)

    def addNodesFromSubgraph(self, node, nodeSet):
        nodeSet.add(node)

        for child in node.children:
            self.addNodesFromSubgraph(child, nodeSet)
