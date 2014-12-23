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
        while len(newStartNode.getChildren())==1:
            newStartNode = newStartNode.getChildren()[0]

        graph.startNodes[graph.getStartNodes().index(startNode)] = newStartNode
        newStartNode.branchLength = 0.0
        
def sortGraph(graph):
    """Sorts children of each node according to the number of children in each of
    their subgraphs."""
    graph.reorder()


def collapseSingletons(node, parent):
    if len(node.getChildren()) == 1 and len(node.getParents()) == 1:
        node.children[0].branchLength += node.branchLength
        parent.children[parent.children.index(node)] = node.children[0]
        node.children[0].parents[node.children[0].parents.index(node)] = parent
        collapseSingletons(node.children[0], parent)

def removeSingletons(graph):
    """Removes all single-child nodes from a graph."""
    for node in graph.getNodeList():
        if len(node.getChildren())>1:
            for i,v in enumerate(node.getChildren()):
                collapseSingletons(v, node)

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
