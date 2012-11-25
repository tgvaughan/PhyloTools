import cairo
from random import random
from Graph import Graph
        
class Painting:

    def __init__(self, graph):
        self.graph = graph
        self.nodePlacements = {}
        self.placeNodes()

    def placeNodes(self):
        
        nodeList = self.graph.getNodeList()
        graphHeight = self.graph.getGraphHeight()
        
        for node in nodeList:
            x = random()
            y = node.getHeight()/graphHeight
            self.nodePlacements[node] = [x,y]
        
    def writePDF(self, outFileName):

        surface = cairo.PDFSurface(outFileName, 100, 200)
        context = cairo.Context(surface)
        context.scale(100,100)

        self.drawPhylo(context)

        surface.finish()

    def drawPhylo(self, context):

        context.set_source_rgb(0,0,0)
        context.set_line_width(.005)

        for node in self.nodePlacements.keys():
            x,y = self.nodePlacements[node]

            for child in node.children:
                context.move_to(x, 2.0*y)
                xc, yc = self.nodePlacements[child]
                context.line_to(xc, 2.0*yc)
        
        context.stroke()
