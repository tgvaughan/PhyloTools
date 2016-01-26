#!/usr/bin/env python

from argparse import ArgumentParser, FileType
from sys import exit

import Graph
import Parser

if __name__=='__main__':

    parser = ArgumentParser(description="Extract attributes of nodes belonging to phylogenetic network.")
    parser.add_argument("graphfile", type=FileType('r'), help="File containing graph data."
            + " If the file contains more than one graph, only the first is used.")
    parser.add_argument("-l","--list", action='store_true', help="List names of available attributes.")
    parser.add_argument("-n","--no_header", action='store_false', help="Do not print header.")
    parser.add_argument("attribute", type=str, nargs='*', help="Attributes to display.")

    # Parse arguments
    args = parser.parse_args()

    # Parse graph file
    graphs = Parser.readFile(args.graphfile)

    if len(graphs) == 0:
        print "File contains no trees/networks."
        exit(1)

    # Assemble list of attribute names:
    attribNames=set()
    for node in graphs[0].getNodeList():
        for key in node.annotation.keys():
            attribNames.add(key)

    if args.list:
        if len(attribNames)>0:
            print "\n".join(attribNames)

    else:
        if len(args.attribute)>0:
            attribNames = filter(lambda a: a in args.attribute, attribNames)

        if args.no_header:
            print "Label Node_Type Node_Age " + " ".join(attribNames)

        # Display event times and types

        for node in graphs[0].getNodeList():
            if node.label != None:
                print node.label,
            else:
                print "NA",

            if len(node.children)>0:
                if len(node.parents)>0:
                    print "internal",
                else:
                    print "root",
            else:
                print "leaf",

            print node.height,

            for name in attribNames:
                if node.annotation.has_key(name):
                    print node.annotation[name],
                else:
                    print "NA",
            
            print

