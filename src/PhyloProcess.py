#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
from sys import argv, exit

import Graph
import Parser

def trimGraphRootEdges(graph, params):
    """Removes root edges from graph.  In the case of a tree, results in a single root with
    in-degree 0 and out-degree >=2."""

    for startNode in graph.getStartNodes():
        newStartNode = startNode
        while len(newStartNode.children)==1:
            newStartNode = newStartNode.children[0]

        graph.startNodes[graph.getStartNodes().index(startNode)] = newStartNode
        newStartNode.branchLength = 0.0

def sortGraph(graph, params):
    """Sorts children of each node according to the number of children in each of
    their subgraphs."""

    graph.reorder()

def removeSingletons(graph, params):
    """Removes all single-child nodes from a graph."""

    for node in graph.getNodeList():
        if len(node.children)!=1 or len(node.parents)>1:
            for parent in node.parents:
                trueParent = parent
                prevParent = node
                while trueParent != None and len(trueParent.parents)<=1 and len(trueParent.children)==1:
                    prevParent = trueParent
                    node.branchLength += trueParent.branchLength
                    if len(trueParent.parents)==0:
                        trueParent = None
                    else:
                        trueParent = trueParent.parents[0]

                if trueParent == None:
                    graph.startNodes[graph.startNodes.index(prevParent)] = node
                else:
                    trueParent.children[trueParent.children.index(prevParent)] = node
                    trueParent.height = node.height + node.branchLength
                node.parents[node.parents.index(parent)] = trueParent

def binarizeMultifurcations(graph, params):
    """Replace multifurcations with a sequence of bifurcations."""

    nodeList = graph.getNodeList()

    for node in graph.getNodeList():

        if len(node.children)>2:
            nodeChildren = node.children[:]

            if len(params)>0:
                offset = float(params[0])
            else:
                offset = 0
        
            prevParent = node;
            for childIdx in range(1,len(nodeChildren)-1):
                child = nodeChildren[childIdx]
                node.children.remove(child)
                child.parents.remove(node)
                dummy = Graph.Node()
                dummy.branchLength = offset
                child.branchLength -= offset*childIdx
                prevParent.addChild(dummy)
                dummy.addChild(child)
                prevParent = dummy

            lastChild = nodeChildren[len(nodeChildren)-1]
            node.children.remove(lastChild)
            lastChild.parents.remove(node)
            prevParent.addChild(lastChild)
            lastChild.branchLength -= offset*(len(nodeChildren)-2)

def scaleGraph(graph, params):
    """Scales ages of all nodes in graph by given factor."""

    factor = float(params[0])

    for node in graph.getNodeList():
        node.height *= factor
        node.branchLength *= factor


actionFuncs = {"trim": trimGraphRootEdges,
               "sort": sortGraph,
               "removeSingletons": removeSingletons,
               "scale": scaleGraph,
               "binarize": binarizeMultifurcations}

if __name__=='__main__':

    parser = ArgumentParser(description="Various tools for modifying phylogenetic networks.")
    parser.add_argument("graphfile", type=FileType('r'),
                        help="File containing graph data.")
    parser.add_argument("outfile", type=FileType('w'),
                        help="File to write result to.")
    parser.add_argument("actions", type=str, nargs="+", metavar='action',
            help="One or more actions to perform.  Available actions: " + ", ".join(actionFuncs.keys()) +
            ". The scale action requires a scale factor f which is specified by appending :f to the " +
            "action name. The binarize action optionally takes a finite edgelength value d which is " +
            "specified by appending :d to the action name.")

    # Parse arguments
    args = parser.parse_args(argv[1:])

    # Parse graph file
    graphs = Parser.readFile(args.graphfile)

    # Perform processing
    for actionStr in args.actions:
        actionParts = actionStr.split(":")
        action = actionParts[0]
        actionParams = actionParts[1:]
        if action in actionFuncs.keys():
            for graph in graphs:
                actionFuncs[action](graph, actionParams)
                args.outfile.write(graph.getNewick() + "\n")
        else:
            raise Exception("Unsupported action {}".format(action))

