import cairo
from random import random
from Graph import Graph
from math import sqrt, pi
from random import random
        
class Painting:

    def __init__(self, graph, rect=True, drawNodes=False, bow=0.2):
        self.graph = graph
        self.rect = rect
        self.drawNodes = drawNodes
        self.bow = bow

        self.margin = .1
        self.aspect = sqrt(2)

        self.xPrintableFrac = 1.0 - self.margin
        self.yPrintableFrac = self.aspect - self.margin

    def writePDF(self, outFileName):

        surface = cairo.PDFSurface(outFileName, 100, sqrt(2)*100)
        context = cairo.Context(surface)
        context.scale(100,100)

        self.drawPhylo(context)

        surface.finish()

    def scaledPos(self, position):
        
        x,y = position
        newx = self.xPrintableFrac*x + 0.5*self.margin
        newy = self.yPrintableFrac*y + 0.5*self.margin

        return (newx, newy)

    def scaledXPos(self, x):

        return self.xPrintableFrac*x + 0.5*self.margin

    def drawPhylo(self, context):

        context.set_source_rgb(0,0,0)
        context.set_line_width(.001)
        graphHeight = self.graph.getGraphHeight()

        for node in self.graph.getNodeList():

            x,y = self.scaledPos(node.getPosition())

            # Check whether any parents of node have the same
            # x position:
            if not self.rect:
                nParents = len(node.getParents())
                parentsSamePos = [False]*nParents
                parentCount = [0]*nParents
                for i in range(nParents):
                    iPos = node.getParents()[i].getPosition()[0]
                    for j in range(i):
                        jPos = node.getParents()[j].getPosition()[0]
                        if abs(iPos-jPos)<0.001:
                            parentsSamePos[i] = True
                            parentsSamePos[j] = True

            # Draw circle at node:
            if self.drawNodes:
                context.move_to(x+.003,y)
                context.arc(x,y,.003,0,2*pi)

            for i,parent in enumerate(node.parents):
                context.move_to(x, y)

                xp, yp = self.scaledPos(parent.getPosition())

                if self.rect:
                    xpb = self.scaledXPos(node.parentBranchPositions[i])
                    context.line_to(xpb,y)
                    context.line_to(xpb,yp)
                    context.line_to(xp,yp)
                else:
                    if parentsSamePos[i]:
                        # Use a Bezier curve offset randomly
                        # to the left or right:
                        cpy = 0.5*(y+yp)
                        dy = abs(y-yp)
                        cpx = x - self.bow*dy+2*self.bow*dy*random()
                        context.curve_to(cpx,cpy,cpx,cpy,xp,yp)
                    else:
                        context.line_to(xp, yp)
        
        context.stroke()
