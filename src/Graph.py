class Node:

    def __init__(self, *parents):
        self.parents = []
        self.children = []
        self.branchLength = None
        self.height = None
        self.label = None
        self.annotation = {}

        self.position = None
        self.parentBranchPositions = []
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

    def annotate(self, key, value):
        self.annotation[key] = value
    
    def isRoot(self):
        return len(self.parent)==0

    def isLeaf(self):
        return len(self.children)==0

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

    def getNewick(self, seenHybrids):
        """Obtain extended Newick representation of subgraph under self."""

        thisStr = ""

        if len(self.parents)>1:
            if self in seenHybrids:
                thisStr = "#H" + seenHybrids.index(self) + ":" + str(self.branchLength)
                return (thisStr)
            else:
                seenHybrids.append(self)

        if len(self.children)>0:
            thisStr += "("
            
            for child in self.children:
                if self.children.index(child)>0:
                    thisStr += ","
                thisStr += child.getNewick(seenHybrids)
                
            thisStr += ")"

        if self.label != None:
            thisStr += self.label
            
        if len(self.parents)>1:
            thisStr += "#H" + seenHybrids.index(self)

        if self.branchLength == None:
            thisStr += ":0.0"
        else:
            thisStr += ":" + str(self.branchLength)

        return (thisStr)
    

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

    def getGraphHeight(self):
        
        maxHeight = 0
        for startNode in self.startNodes:
            maxHeight = max(startNode.height, maxHeight)

        return maxHeight

    def getGraphOrigin(self):

        maxOrigin = 0
        for startNode in self.startNodes:
            maxOrigin = max(startNode.height, maxOrigin)
            if startNode.branchLength != None:
                maxOrigin += startNode.branchLength

        return maxOrigin

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

        node.children.sort(key=lambda x: x.getDecendentCount())                               
            

    def getNewick(self):
        """Obtain extended Newick representation of graph."""
        
        newick = ""
        seenHybrids = []

        for startNode in self.startNodes:
            if self.startNodes.index(startNode)>0:
                newick += ","
            newick += startNode.getNewick(seenHybrids)

        newick += ";"

        return (newick)
