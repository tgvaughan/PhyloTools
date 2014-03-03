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
        
actionFuncs = {"trim": trimGraphRootEdges,
               "sort": sortGraph}
        
if __name__=='__main__':

    parser = ArgumentParser(description="Various tools for modifying phylogenetic networks.")
    parser.add_argument("graphfile", type=FileType('r'),
                        help="File containing graph data.")
    parser.add_argument("outfile", type=FileType('w'),
                        help="File to write result to.")
    parser.add_argument("actions", type=str, nargs="+",
                        help="One or more actions to perform. (Currently only trim and reorder.)")

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
            raise Exception("Unsupported action {}".format(stat))
