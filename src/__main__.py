from sys import argv, exit
from argparse import ArgumentParser, FileType

import Parser, Painter, Layout

parser = ArgumentParser("phylopaint", description="""
Paints graphical representations of annotated phylogenetic trees and networks.""")

parser.add_argument("infile", type=FileType('r'), help="""
Phylogenetic tree/network in extended NEXUS format.
(If no nexus header is found, straight extended Newick is assumed.)
Files can be read in from standard input using - as the input argument.""")
parser.add_argument("outfile", type=str, help="""
Name of output file to create.""")
parser.add_argument("-f","--format",type=str,help="""
Specify format of output file.  Default is to infer from
output file name extension.""")

# Graphical style options
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

# Determine output file format:
if args.format == None:
    components = args.outfile.strip().split('.')
    if len(components)>1:
        args.format = components[len(components)-1]
else:
    args.format = args.format.lower()

if args.format == None:
    print "Could not determine output format from file extention."
    print "(Specify explicitly using --format.)"
    exit(1)

if args.format not in ["pdf","ps", "svg", "png"]:
    print "Unsupported output format '{}'.".format(args.format)
    exit(1)

# Parse graph:
graph = Parser.NexusGraph(args.infile)

# Sort nodes:
if args.sortTree:
    graph.reorder()

# Position nodes within a unit square:
Layout.layout(graph)

# Draw positioned nodes to output file using Cairo:
painting = Painter.Painting(graph, rect=args.rect, drawNodes=args.drawNodes)

writerMap = {"svg": painting.writeSVG,
             "pdf": painting.writePDF,
             "ps": painting.writePS,
             "png": painting.writePNG}
writerMap[args.format](args.outfile)
