from sys import argv, exit
from argparse import ArgumentParser, FileType

import Parser, Painter, Layout

parser = ArgumentParser("PhyloPaint", description="""
Paints graphical representations of annotated phylogenetic trees and networks.""")

parser.add_argument("infile", type=FileType('r'), help="""
Phylogenetic tree/network in extended Newick or NEXUS format.""")
    
if len(argv)<2:
    parser.print_usage()
    exit(0)
        
args = parser.parse_args(argv[1:])
graph = Parser.NexusGraph(args.infile)

print graph.getStartNodes()[0].getDecendentCount()

# Sort nodes:
graph.reorder()

# Position nodes within a unit square:
Layout.layout(graph)

# Draw positioned nodes to output file using Cairo:
painting = Painter.Painting(graph, rect=True)
painting.writePDF("out.pdf")
