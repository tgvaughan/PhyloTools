PhyloTools
==========

A handful of python scripts I occasionally use to do simple things
with trees/networks.


## PhyloPaint

This program takes extended Newick specifications of phylogenetic
trees and networks and renders them in a variety of output formats via
the Cairo graphics library.  Unlike the majority of tree visualisers
available, this program works non-interactively.

The eventual aim was to provide something similar to GraphViz, but specifically
targeted at rooted and timed phylogenies where one axis is scaled to represent
time.  It can be used to paint readable trees and networks from Nexus files
containing annotated extended Newick trees---as produced by
[MASTER](http://tgvaughan.github.com/MASTER).  The program requires a working
2.7 Python installation and the [pycairo](http://cairographics.org/pycairo/)
module.

**I don't intend to further develop this tool.**

## PhyloProcess

Perform several modifications to phylogenetic trees/networks.

## PhyloStat

Calculate summary statistics for phylogenetic trees/networks.

## PhyloConvert

Convert between a small number of phylogenetic tree/network formats.

## PhyloAttribs

List values of tree/network node attributes.
