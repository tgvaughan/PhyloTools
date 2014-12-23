#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from sys import argv, exit

import Graph
import Parser

def formatNewick(graphs, outfile):

    for graph in graphs:
        outfile.write(graph.getNewick() + "\n")

def formatNEXUS(graphs, outfile):
    outfile.write("#nexus\n")
    outfile.write("begin trees;\n")
    for i,graph in enumerate(graphs):
        outfile.write("tree TREE_" + str(i) + " = " + graph.getNewick() + "\n")
    outfile.write("end;\n")

def formatExpoTree(graphs, outfile):
    """Translates graph into something akin to the format used by Gabriel's expoTree."""

    if len(graphs) != 1:
        print "ExpoTree format applicable only to files containing a single graph."
        exit(1)

    for node in sorted(graphs[0].getNodeList(), key=lambda node: node.height):

        # skip singletons:
        if len(node.children) == 1:
            continue

        if node.isLeaf():
            code = 0
        else:
            code = 1
        outfile.write("{} {}\n".format(node.height, code))

    outfile.write(str(graphs[0].getGraphOrigin()) + " 1\n")

formatFuncs = {
    "newick": formatNewick,
    "nexus": formatNEXUS,
    "expoTree": formatExpoTree}


if __name__ == '__main__':

    parser = ArgumentParser(description="Convert between different phylogenetic network description formats.")
    parser.add_argument("infile", type=FileType('r'), help="File containing graph data (Newick or NEXUS).")
    parser.add_argument("outfile", type=FileType('w'), help="Output file to write.")
    parser.add_argument("format", type=str,
        help="Format of output file.  May be one of the following: " + ", ".join(formatFuncs.keys()))

    # Parse arguments
    args = parser.parse_args(argv[1:])

    # Parse graph file
    graphs = Parser.readFile(args.infile)

    if len(graphs) == 0:
        print "Skipping empty graph file."
        exit(0)

    if args.format in formatFuncs.keys():
        formatFuncs[args.format](graphs, args.outfile)
    else:
        print "Unrecognized format '{}'".format(args.format)
