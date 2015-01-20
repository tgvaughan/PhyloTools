#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from sys import argv, exit

import Graph
import Parser

def trimGraphRootEdges(graph):
    """Removes root edges from graph.  In the case of a tree, results in a single root with
    in-degree 0 and out-degree >=2."""

    for startNode in graph.getStartNodes():
        newStartNode = startNode
        while len(newStartNode.children)==1:
            newStartNode = newStartNode.children[0]

        graph.startNodes[graph.getStartNodes().index(startNode)] = newStartNode
        newStartNode.branchLength = 0.0

def sortGraph(graph):
    """Sorts children of each node according to the number of children in each of
    their subgraphs."""
    graph.reorder()

def removeSingletons(graph):
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


actionFuncs = {"trim": trimGraphRootEdges,
               "sort": sortGraph,
               "removeSingletons": removeSingletons}

if __name__=='__main__':

    parser = ArgumentParser(description="Various tools for modifying phylogenetic networks.")
    parser.add_argument("graphfile", type=FileType('r'),
                        help="File containing graph data.")
    parser.add_argument("outfile", type=FileType('w'),
                        help="File to write result to.")
    parser.add_argument("actions", type=str, nargs="+",
            help="One or more actions to perform.  Available actions: " + ", ".join(actionFuncs.keys()))

    # Parse arguments
    args = parser.parse_args(argv[1:])

    # Parse graph file
    graphs = Parser.readFile(args.graphfile)

    # Perform processing
    for action in args.actions:
        if action in actionFuncs.keys():
            for graph in graphs:
                actionFuncs[action](graph)
                args.outfile.write(graph.getNewick() + "\n")
        else:
            raise Exception("Unsupported action {}".format(action))

