import cairo
from random import random
from Graph import Graph
from math import sqrt
        
class Painting:

    def __init__(self, graph, rect=True):
        self.graph = graph
        self.rect = rect

    def writePDF(self, outFileName):

        surface = cairo.PDFSurface(outFileName, 100, sqrt(2)*100)
        context = cairo.Context(surface)
        context.scale(100,100)

        self.drawPhylo(context)

        surface.finish()

    def scaledPos(self, position, margin, aspect):
        
        xPrintableFrac = 1.0 - margin;
        yPrintableFrac = aspect - margin

        offset = 0.5*margin

        x,y = position
        newx = xPrintableFrac*x + offset
        newy = yPrintableFrac*y + offset

        return (newx, newy)

    def drawPhylo(self, context):

        context.set_source_rgb(0,0,0)
        context.set_line_width(.001)
        graphHeight = self.graph.getGraphHeight()

        for node in self.graph.getNodeList():

            x,y = self.scaledPos(node.getPosition(), 0.1, sqrt(2.0))

            for child in node.children:
                context.move_to(x, y)
                xc, yc = self.scaledPos(child.getPosition(), 0.1, sqrt(2.0))

                if self.rect:
                    context.line_to(xc, y)
                    context.line_to(xc, yc)
                else:
                    context.line_to(xc, yc)
        
        context.stroke()
