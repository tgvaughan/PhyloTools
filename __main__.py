from sys import argv, exit
from argparse import ArgumentParser, FileType

import Parser

parser = ArgumentParser("PhyloPaint", description="""
Paints graphical representations of annotated phylogenetic trees and networks.""")

parser.add_argument("infile", type=FileType('r'), help="""
Phylogenetic tree/network in extended Newick or NEXUS format.""")
    
if len(argv)<2:
    parser.print_usage()
    exit(0)
        
args = parser.parse_args(argv[1:])
graph = Parser.NewickGraph(args.infile.readline().strip())
