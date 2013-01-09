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
parser.add_argument("-f","--format",type=str, help="""
Specify format of output file.  Default is to infer from
output file name extension.""")
parser.add_argument("-t","--tree", type=int, default=None, help="""
If more than one tree/network exists in input file, specifies
particular tree to graph.""")

# Graphical style options
parser.add_argument("-r","--rect", action="store_true", help="""
Use rectangular edges when drawing graph.""")
parser.add_argument("-d","--drawNodes", action="store_true", help="""
Draw additional circles representing nodes.""")
parser.add_argument("-s","--sortTree", action="store_true", help="""
Sort child nodes in order of clade size.""")
parser.add_argument("-l","--lineWidth", type=float, default=1.0, help="""
Relative width of lines.""")
parser.add_argument("-c","--colourTrait", type=str, help="""
Give unique values of this trait different colours.""")

    
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

# Parse graphs:
graphs = Parser.readFile(args.infile, graphNum=args.tree)
if len(graphs)>1:
    print "Cannot yet deal with multiple trees.  Please select an individual tree using --tree."
    exit(1)
graph = graphs[0]

# Sort nodes:
if args.sortTree:
    graph.reorder()

# Position nodes within a unit square:
Layout.layout(graph)

# Draw positioned nodes to output file using Cairo:
painting = Painter.Painting(graph, rect=args.rect, drawNodes=args.drawNodes, colourTrait=args.colourTrait, lineWidth=args.lineWidth)

writerMap = {"svg": painting.writeSVG,
             "pdf": painting.writePDF,
             "ps": painting.writePS,
             "png": painting.writePNG}
writerMap[args.format](args.outfile)
