#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from sys import argv, exit

import Graph
import Parser

statFuncs = {"height": lambda x: x.getGraphHeight()}

if __name__=='__main__':

    parser = ArgumentParser(description="Calculate stats from phylogenetic graphs.")
    parser.add_argument("graphfile", type=FileType('r'), help="File containing graph data.")
    parser.add_argument("-n", action="store_true", help="Do NOT prepend statistic names to output.")
    parser.add_argument("stats", type=str, nargs="+", help="""One or more statistics to calculate.""")

    # Parse arguments
    args = parser.parse_args(argv[1:])

    # Parse graph file
    graphs = Parser.readFile(args.graphfile)
    
    # Calculate and display stats:
    for stat in args.stats:
        if stat in statFuncs.keys():
            if not args.n:
                print stat,
        else:
            raise Exception("Unsupported statistic {}".format(stat))
    if not args.n:
        print
    
    for i,graph in enumerate(graphs):
        for stat in args.stats:
            print statFuncs[stat](graph),
        print
