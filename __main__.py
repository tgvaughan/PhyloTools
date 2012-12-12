from sys import argv, exit
from argparse import ArgumentParser, FileType

import Parser, Painter, Layout

parser = ArgumentParser("PhyloPaint", description="""
Paints graphical representations of annotated phylogenetic trees and networks.""")

parser.add_argument("infile", type=FileType('r'), help="""
Phylogenetic tree/network in extended NEXUS format.""")
parser.add_argument("-r","--rect", action="store_true", help="""
Use rectangular edges when drawing graph.""")
parser.add_argument("-d","--drawNodes", action="store_true", help="""
Draw additional circles representing nodes.""")
parser.add_argument("-s","--sortTree", action="store_true",help="""
Sort child nodes in order of clade size.""")
    
if len(argv)<2:
    parser.print_usage()
    exit(0)
        
args = parser.parse_args(argv[1:])
graph = Parser.NexusGraph(args.infile)

# Sort nodes:
if args.sortTree:
    graph.reorder()

# Position nodes within a unit square:
Layout.layout(graph)

# Draw positioned nodes to output file using Cairo:
painting = Painter.Painting(graph, rect=args.rect, drawNodes=args.drawNodes)
painting.writePDF("out.pdf")
