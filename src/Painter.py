import cairo
from random import random
from Graph import Graph
from math import sqrt, pi
from random import random
        
class Painting:

    def __init__(self, graph, rect=True, drawNodes=False, colourTrait=None, ancestralFragmentTrait=None,
                 lineWidth=1.0, bow=0.2, aspect=sqrt(2), margin=.1):
        self.graph = graph
        self.rect = rect
        self.drawNodes = drawNodes
        self.bow = bow
        self.colourTrait = colourTrait
        self.ancestralFragmentTrait = ancestralFragmentTrait
        self.lineWidth = lineWidth

        self.margin = margin
        self.aspect = aspect

        self.xPrintableFrac = 1.0 - self.margin
        self.yPrintableFrac = self.aspect - self.margin

        self.seenTraits = []

    def writePDF(self, outFileName):

        surface = cairo.PDFSurface(outFileName, 595, self.aspect*595)
        context = cairo.Context(surface)
        context.scale(595,595)

        self.drawPhylo(context)

        surface.finish()

    def writeSVG(self, outFileName):

        surface = cairo.SVGSurface(outFileName, 595, self.aspect*595)
        context = cairo.Context(surface)
        context.scale(595,595)

        self.drawPhylo(context)

        surface.finish()

    def writePS(self, outFileName):

        surface = cairo.PSSurface(outFileName, 595, self.aspect*595)
        context = cairo.Context(surface)
        context.scale(595,595)

        self.drawPhylo(context)

        surface.finish()

    def writePNG(self, outFileName):

        surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                     1000, int(self.aspect*1000))

        # Get surface context:
        context = cairo.Context(surface)

        # Give image a white background (black by default):
        context.set_source_rgb(1,1,1)
        context.rectangle(0,0, surface.get_width(), surface.get_height())
        context.fill()

        # Scale context so that painting method doesn't have to know
        # physical dimensions:
        context.scale(1000,1000)

        # Draw phylogeny:
        self.drawPhylo(context)

        # Write to file and finish:
        surface.write_to_png(outFileName)
        surface.finish()

    def scaledPos(self, position):
        
        x,y = position
        newx = self.xPrintableFrac*x + 0.5*self.margin
        newy = self.yPrintableFrac*y + 0.5*self.margin

        return (newx, newy)

    def scaledXPos(self, x):

        return self.xPrintableFrac*x + 0.5*self.margin

    def selectColour(self, node, context):
        
        if self.colourTrait == None:
            context.set_source_rgb(0,0,0)
            return

        pallet = [(0,0,1), (0,1,0), (0,1,1), (1,0,0), (1,0,1), (1,1,0)]

        value = None
        if len(node.annotation.values())>0:
            keys = node.annotation.values()[0]
            if self.colourTrait in keys:
                value = node.annotation[self.colourTrait]

        if value in self.seenTraits:
            idx = self.seenTraits.index(value)
        else:
            self.seenTraits.append(value)
            idx = len(self.seenTraits)-1

        g,r,b = pallet[idx%len(pallet)]
        context.set_source_rgb(r,g,b)

    def drawAncestral(self, node, parent, pos, context):

        if self.ancestralFragmentTrait == None:
            return

        if (parent not in node.annotation) or (self.ancestralFragmentTrait not in node.annotation[parent].keys()):
            return

        width=.05
        height=.005

        # Draw empty box:
        widthP = width
        heightP = height
        context.set_source_rgb(1,1,1)
        x1,y1=self.scaledPos((pos[0]-0.5*widthP,pos[1]-0.5*heightP))
        x2,y2=self.scaledPos((pos[0]+0.5*widthP,pos[1]+0.5*heightP))
        context.rectangle(x1, y1, x2-x1, y2-y1)
        context.fill()

        # Draw box boundary
        self.selectColour(node, context)
        x1,y1=self.scaledPos((pos[0]-0.5*width,pos[1]-0.5*height))
        x2,y2=self.scaledPos((pos[0]+0.5*width,pos[1]+0.5*height))
        context.rectangle(x1, y1, x2-x1, y2-y1)
        context.stroke()

        # Fill ancestral fragments:
        fragments = node.annotation[parent][self.ancestralFragmentTrait]
        nfrag = len(fragments)/2
        for i in range(nfrag):
            boundary1 = fragments[i*2]
            boundary2 = fragments[i*2 + 1]

            xb1 = self.scaledXPos(pos[0]-0.5*width + boundary1*width)
            xb2 = self.scaledXPos(pos[0]-0.5*width + boundary2*width)

            context.rectangle(xb1, y1, xb2-xb1, y2-y1)
            context.fill()

    def drawPhylo(self, context):

        context.set_source_rgb(0,0,0)
        context.set_line_width(.001*self.lineWidth)
        graphHeight = self.graph.getGraphHeight()

        # Draw graph:
        for node in self.graph.getNodeList():

            x,y = self.scaledPos(node.getPosition())

            # Choose colour from pallet:
            self.selectColour(node, context)

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
            if self.drawNodes and not node.isLeaf():
                context.move_to(x+.003,y)
                context.arc(x,y,.003,0,2*pi)
                context.fill()

            for i,parent in enumerate(node.parents):
                context.move_to(x, y)

                xp, yp = self.scaledPos(parent.getPosition())

                if self.rect:
                    xpb = self.scaledXPos(node.parentBranchPositions[i])
                    context.line_to(xpb,y)
                    context.line_to(xpb,yp)
                    context.line_to(xp,yp)
                    context.stroke()
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


        # Draw ancestral sequence fragments:
        for node in self.graph.getNodeList():

            for i,parent in enumerate(node.parents):

                if self.rect:
                    barPosX = node.parentBranchPositions[i]
                    r = random()*0.5 + 0.25
                    barPosY = r*parent.getPosition()[1] + (1-r)*node.getPosition()[1]
                    self.drawAncestral(node, parent, (barPosX, barPosY), context)
