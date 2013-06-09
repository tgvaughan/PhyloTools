import re
import sys
from Graph import Node, Graph

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class NewickGraph(Graph):

    def __init__(self, newickStr, afTrait=None, debug=False):
        Graph.__init__(self)

        self.newickStr = newickStr

        # Initialise dictionary for recording ancestral
        # sequence fragment information
        self.afTrait = afTrait
        if afTrait != None:
            self.ancestralFragments = {}

        self.doParse(debug=debug)

    def doParse(self, debug=False):

        # Tokenise input string:
        self.doLex(debug=debug)

        # Initialise dictionary to keep track of hybrid nodes:
        self.hybrids = {}

        # Parse token list via recursive decent:
        self.i=0
        self.indent=0
        self.ruleG(debug=debug)

        if debug:
            print "{} nodes read.".format(len(self.getNodeList()))

        # Calculate absolute node heights
        self.getHeights()

        # Merge hybrid nodes
        self.mergeHybrids()

    ##########################
    # TOKENIZER

    def doLex(self, debug=False):

        tokens = [
            ('LPAREN',  '\('),
            ('RPAREN',  '\)'),
            ('COLON',   ':'),
            ('NUM', '\d+(\.\d+)?([eE]-?\d+)?'),
            ('STRING', '"[^"]*"'),
            ('LABEL',   '[a-zA-Z0-9_]+'),
            ('HASH', '#'),
            ('OPENA', '\[&'),
            ('EQUALS', '='),
            ('OPENV', '{'),
            ('CLOSEV','}'),
            ('CLOSEA', '\]'),
            ('COMMA',   ','),
            ('SEMI',    ';')
            ]

        valueTokens = ['NUM','LABEL', 'STRING']

        idx=0
        tokenList=[]
        valueList=[]

        while idx < len(self.newickStr):

            noMatch = True

            for k in range(len(tokens)):

                match = re.match(tokens[k][1], self.newickStr[idx:])

                if match != None:             

                    tokenList.append(tokens[k][0])
                    idx += len(match.group(0))

                    if tokens[k][0] in valueTokens:
                        valueList.append(match.group(0))
                    else:
                        valueList.append(None)

                    if debug:
                        print "{}: {} '{}'".format(idx, tokens[k][0], valueList[len(valueList)-1])
                                               
                    noMatch = False
                    break

            if noMatch:
                raise ParseError('Lex error at character ' + str(idx) + ": '"
                        + self.newickStr[idx] + "'.")

        self.tokenList = tokenList
        self.valueList = valueList

    ##########################
    # RECURSIVE DECENT PARSER

    def parseError(self):
        raise ParseError('Error parsing token {} ({})'.format(
                self.tokenList[self.i], self.valueList[self.i]))

    def acceptToken(self, token, manditory=False):
        if self.tokenList[self.i]==token:
            self.i = self.i + 1
            return True
        else:
            if not manditory:
                return False
            else:
                self.parseError()

    def indentOut(self):
        sys.stdout.write(" "*self.indent) 

    def ruleG(self, debug=False):
        self.startNodes.append(self.ruleN(None, debug=debug))
        self.startNodes.extend(self.ruleZ(None, debug=debug))
        self.acceptToken('SEMI', manditory=True)
    
    def ruleZ(self, parent, debug=False):
        if self.acceptToken('COMMA'):
            siblings = [self.ruleN(parent, debug=debug)]
            siblings.extend(self.ruleZ(parent, debug=debug))
            return siblings
        else:
            # accept epsilon
            return []

    def ruleN(self, parent, debug=False):
        if debug:
            self.indentOut()
        if parent != None:
            node = Node(parent)
        else:
            node = Node()
        self.ruleS(node, debug=debug)
        self.ruleL(node, debug=debug)
        self.ruleH(node, debug=debug)
        self.ruleA(node, parent, debug=debug)
        self.ruleB(node, debug=debug)

        if debug:
            print

        return node

    def ruleS(self, node, debug=False):
        if self.acceptToken('LPAREN'):
            
            if debug:
                print "("
                self.indent += 1

            self.ruleN(node, debug=debug)
            self.ruleZ(node, debug=debug)

            self.acceptToken('RPAREN', manditory=True)

            if debug:
                self.indent -= 1
                self.indentOut()
                print  ")",

        else:
            # accept epsilon
            return

    def ruleL(self, node, debug=False):
        if self.acceptToken('LABEL') or self.acceptToken('NUM'):
            if debug:
                sys.stdout.write(" Lab:" + str(self.valueList[self.i-1]))

            node.setLabel(self.valueList[self.i-1])
        else:
            # accept epsilon
            return

    def ruleH(self, node, debug=False):
        if self.acceptToken('HASH'):
            if not (self.acceptToken('LABEL') or self.acceptToken('NUM')):
                self.parseError()

            hlabel = self.valueList[self.i-1]
            if hlabel in self.hybrids.keys():
                self.hybrids[hlabel].append(node)
            else:
                self.hybrids[hlabel] = [node]

            if debug:
                sys.stdout.write(" Hybrid:" + str(hlabel))
        else:
            # accept epsilon
            return

    def ruleA(self, node, parent, debug=False):
        if self.acceptToken('OPENA'):
            self.ruleC(node, parent, debug=debug)
            self.ruleD(node, parent, debug=debug)
            self.acceptToken('CLOSEA', manditory=True)
        else:
            # accept epsilon
            return

    def ruleC(self, node, parent, debug=False):
        self.acceptToken('LABEL', manditory=True)

        key = self.valueList[self.i-1]

        self.acceptToken('EQUALS', manditory=True)

        value = self.ruleV()

        if hasattr(self, "ancestralFragments") and key == self.afTrait:
            if (node,parent) not in self.ancestralFragments:
                self.ancestralFragments[(node,parent)] = [value]
            else:
                self.ancestralFragments[(node,parent)].append(value)
        else:
            node.annotate(key, value)

        if debug:
            sys.stdout.write(" Annot:{}={}".format(key,value))

    def ruleD(self, node, parent, debug=False):
        if self.acceptToken('COMMA'):
            self.ruleC(node, parent, debug=debug)
            self.ruleD(node, parent, debug=debug)
        else:
            # accept epsilon
            return

    def ruleV(self, debug=False):
        if self.acceptToken('LABEL') or self.acceptToken('NUM') or self.acceptToken('STRING'):
            return self.valueList[self.i-1]
        else:
            self.acceptToken('OPENV', manditory=True)
            self.acceptToken('NUM', manditory=True)
            valueVec = [float(self.valueList[self.i-1])]
            self.ruleQ(valueVec, debug=debug)
            self.acceptToken('CLOSEV', manditory=True)
            return valueVec

    def ruleQ(self, valueVec, debug=False):
        if self.acceptToken('COMMA'):
            self.acceptToken('NUM', manditory=True)
            valueVec.append(float(self.valueList[self.i-1]))
            self.ruleQ(valueVec, debug=debug)
        else:
            # accept epsilon
            return

    def ruleB(self, node, debug=False):
        if self.acceptToken('COLON'):
            self.acceptToken('NUM', manditory=True)
            node.setBranchLength(float(self.valueList[self.i-1]))

            if debug:
                sys.stdout.write(" Blength:" + str(node.branchLength))

        else:
            # accept epsilon
            return

    ##########################
    # TIDY UP

    def getHeights(self):
        if len(self.startNodes)>1:
            for startNode in self.startNodes:
                if "height" not in startNode.annotation.keys():
                    raise ParseError("Graphs with multiple start nodes require height annotation.")
                else:
                    startNode.setHeight(float(startNode.annotation['height']))
                    self.getHeightsRecurse(startNode, None)
        else:
            self.startNodes[0].setHeight(0.0)
            self.getHeightsRecurse(self.startNodes[0], None)

    def getHeightsRecurse(self, node, last):
        if last != None:
            node.setHeight(last.getHeight()+node.getBranchLength())

        for child in node.children:
            self.getHeightsRecurse(child, node)

    def mergeHybrids(self):

        for group in self.hybrids.keys():
            
            # Find primary node:
            primaryNode = None
            for node in self.hybrids[group]:
                if primaryNode == None or len(node.children)>0:
                    primaryNode = node

            # Replace all non-primary nodes with primary node:
            for node in self.hybrids[group]:
                if node == primaryNode:
                    continue
                
                node.parents[0].children.remove(node)
                node.parents[0].addChild(primaryNode)
                primaryNode.annotation.update(node.annotation)

                # Deal with ancestral fragment annotations:
                if hasattr(self, "ancestralFragments"):
                    if (primaryNode,node.parents[0]) in self.ancestralFragments:
                        self.ancestralFragments[(primaryNode, node.parents[0])].extend(self.ancestralFragments[(node,node.parents[0])])
                    else:
                        self.ancestralFragments[(primaryNode, node.parents[0])] = self.ancestralFragments[(node,node.parents[0])]

                    del self.ancestralFragments[(node, node.parents[0])]
        
        del self.hybrids


def readFile (fh, debug=False, afTrait=None, graphNum=None):
    """Extract graphs from given file."""

    graphs = []
    
    firstLine = fh.readline()
    if not firstLine.lower().startswith("#nexus"):
        print "Not a valid NEXUS file. Trying to parse as a collection of extended Newick strings..."

        lines = [firstLine]
        lines.extend(fh.readlines())

        # Strip empty/commented lines:
        tmp = []
        for line in lines:
            thisline = line.strip()
            if len(thisline)>0 and (not thisline.startswith("#")):
                tmp.append(thisline)
        lines = tmp

        for n,line in enumerate(lines):
            if graphNum != None and graphNum != n:
                continue
            graphs.append(NewickGraph(line, afTrait=afTrait, debug=debug))
            
        if len(graphs)==0:
            raise ParseError("No graphs found.");
            
        print "Successfuly parsed {} graphs.".format(len(graphs))
        return graphs
        
    treesSectionSeen = False
    inTranslate = False
    newickStr = ""
    n = 0
    for line in fh:
        line = line.lower().strip()
        if not treesSectionSeen:
            if line.startswith("begin trees;"):
                treesSectionSeen = True
            continue

        if not inTranslate and line.startswith("translate"):
            inTranslate = True

        if inTranslate:
            if line.endswith(";"):
                inTranslate = False
            continue
            
        if line.startswith("end;"):
            if len(newickStr)>0:
                if graphNum == None or graphNum == n:
                    graphs.append(NewickGraph(newickStr, afTrait=afTrait, debug=debug))
            break

        if line.startswith("tree "):
            if len(newickStr)>0:
                if graphNum == None or graphNum == n:
                    graphs.append(NewickGraph(newickStr, debug=debug))
                n += 1
            newickStr = line[(line.find('=')+1):].strip()
        else:
            newickStr += line;

    if not treesSectionSeen:
        raise ParseError("No tree section found.")

    if len(graphs)==0:
        raise ParseError("No graphs found.");
    
    if debug:
        print "Successfuly parsed {} graphs.".format(len(graphs))

    fh.close()
    return graphs
