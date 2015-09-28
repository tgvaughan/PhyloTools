#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from sys import argv, exit

import Graph
import Parser

statFuncs = {"height": lambda x,y: x.getGraphHeight(),
             "length": lambda x,y: x.getGraphLength(),
             "origin": lambda x,y: x.getGraphOrigin(),
             "nleaves": lambda x,y: len(x.getLeafList()),
             "nextant": lambda x,y: x.getExtantLineagesCount(float(y[0]))}

if __name__=='__main__':

    parser = ArgumentParser(description="Calculate stats from phylogenetic graphs.")
    parser.add_argument("graphfile", type=FileType('r'), help="File containing graph data.")
    parser.add_argument("-n", action="store_true", help="Do NOT prepend statistic names to output.")
    parser.add_argument("stats", type=str, nargs="+", help=
            "One or more statistics to calculate. Currently may be any of: "
            + ", ".join(statFuncs.keys()) + ". "
            + "Some statistics accept numerical arguments.  These should be appended as "
            + "a colon-delimited list to the statistic name.")

    # Parse arguments
    args = parser.parse_args(argv[1:])

    # Parse graph file
    graphs = Parser.readFile(args.graphfile)

    # Calculate and display stats:
    for stat in args.stats:
        statName = stat.split(':')[0]
        if statName in statFuncs.keys():
            if not args.n:
                print statName,
        else:
            raise Exception("Unsupported statistic {}".format(stat))
    if not args.n:
        print
    
    for i,graph in enumerate(graphs):
        for stat in args.stats:
            a = stat.split(':')
            statName = a[0]
            statArg = a[1:]
            print statFuncs[statName](graph, statArg),
        print
