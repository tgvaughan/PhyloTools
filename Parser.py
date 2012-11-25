import re
import sys
from Graph import Node, Graph

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)


class NewickGraph(Graph):

    def __init__(self, newickStr):
        Graph.__init__(self)

        self.newickStr = newickStr

        # Tokenise input string:
        self.doLex()

        # Initialise dictionary to keep track of hybrid nodes:
        self.hybrids = {}

        # Parse token list via recursive decent:
        self.i=0
        self.indent=0
        self.ruleG()

        print "{} nodes read.".format(len(self.getNodeList()))

        # Merge hybrid nodes
        self.mergeHybrids()

        # Calculate absolute node heights
        self.getHeights()

    ##########################
    # TOKENIZER

    def doLex(self):

        tokens = [
            ('LPAREN',  '\('),
            ('RPAREN',  '\)'),
            ('COLON',   ':'),
            ('NUM', '\d+(\.\d+)?([eE]-?\d+)?'),
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

        valueTokens = ['NUM','LABEL']

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

                    #print "{}: {} '{}'".format(idx, tokens[k][0], valueList[len(valueList)-1])
                                               
                    noMatch = False
                    break

            if noMatch:
                raise ParseError('Lex error at character' + str(idx) + ": '"
                        + self.newickStr[idx] + "'.")

        self.tokenList = tokenList
        self.valueList = valueList

    ##########################
    # RECURSIVE DECENT PARSER

    def parseError(self):
        raise ParseError('Error parsing token {} ({})'.format(
                self.tokenList[self.i]), self.valueList[self.i])

    def acceptToken(self, token, manditory=False):
        if self.tokenList[self.i]==token:
            #print "Accepted token: {} ({})".format(token, self.valueList[self.i])
            self.i = self.i + 1
            return True
        else:
            if not manditory:
                return False
            else:
                self.parseError()

    def indentOut(self):
        sys.stdout.write(" "*self.indent) 

    def ruleG(self):
        self.startNodes.append(self.ruleN(None))
        self.startNodes.extend(self.ruleZ(None))
        self.acceptToken('SEMI', manditory=True)
    
    def ruleZ(self, parent):
        if self.acceptToken('COMMA'):
            siblings = [self.ruleN(parent)]
            siblings.extend(self.ruleZ(parent))
            return siblings
        else:
            # accept epsilon
            return []

    def ruleN(self, parent):
        self.indentOut()
        if parent != None:
            node = Node(parent)
        else:
            node = Node()
        self.ruleS(node)
        self.ruleL(node)
        self.ruleH(node)
        self.ruleA(node)
        self.ruleB(node)
        print
        return node

    def ruleS(self, node):
        if self.acceptToken('LPAREN'):

            print "("
            self.indent += 1

            self.ruleN(node)
            self.ruleZ(node)

            self.acceptToken('RPAREN', manditory=True)

            self.indent -= 1
            self.indentOut()
            print  ")",

        else:
            # accept epsilon
            return

    def ruleL(self, node):
        if self.acceptToken('LABEL') or self.acceptToken('NUM'):

            sys.stdout.write(" Lab:" + str(self.valueList[self.i-1]))

            node.setLabel(self.valueList[self.i-1])
        else:
            # accept epsilon
            return

    def ruleH(self, node):
        if self.acceptToken('HASH'):
            self.acceptToken('LABEL', manditory=True)
            hlabel = self.valueList[self.i-1]
            if hlabel in self.hybrids.keys():
                self.hybrids[hlabel].append(node)
            else:
                self.hybrids[hlabel] = [node]

            sys.stdout.write(" Hybrid:" + str(hlabel))
        else:
            # accept epsilon
            return

    def ruleA(self, node):
        if self.acceptToken('OPENA'):
            self.ruleC(node)
            self.ruleD(node)
            self.acceptToken('CLOSEA', manditory=True)
        else:
            # accept epsilon
            return

    def ruleC(self, node):
        self.acceptToken('LABEL', manditory=True)

        key = self.valueList[self.i-1]

        self.acceptToken('EQUALS', manditory=True)

        value = self.ruleV()

        node.annotate(key, value)

        sys.stdout.write(" Annot:{}={}".format(key,value))

    def ruleD(self, node):
        if self.acceptToken('COMMA'):
            self.ruleC(node)
            self.ruleD(node)
        else:
            # accept epsilon
            return

    def ruleV(self):
        if self.acceptToken('LABEL'):
            return self.valueList[self.i-1]
        else:
            self.acceptToken('OPENV', manditory=True)
            self.acceptToken('NUM', manditory=True)
            valueVec = [float(self.valueList[self.i-1])]
            self.ruleQ(valueVec)
            self.acceptToken('CLOSEV', manditory=True)
            return valueVec

    def ruleQ(self, valueVec):
        if self.acceptToken('COMMA'):
            self.acceptToken('NUM', manditory=True)
            valueVec.append(float(self.valueList[self.i-1]))
            self.ruleQ(valueVec)
        else:
            # accept epsilon
            return

    def ruleB(self, node):
        if self.acceptToken('COLON'):
            self.acceptToken('NUM', manditory=True)
            node.setBranchLength(float(self.valueList[self.i-1]))

            sys.stdout.write(" Blength:" + str(node.branchLength))

        else:
            # accept epsilon
            return

    ##########################
    # TIDY UP

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
        
        del self.hybrids

    def calcNodeHeights(self):
        seen = set()
        self.calcNodeHeightsRecurse(self.startNodes[0], None, seen)

    def calcNodeHeightsRecurse(self, node, last, seen):
        
        if last==None:
            t = 0
        else:
            if node in last.children:
                t = last.getHeight() + node.getBranchLength()
            else:
                t = last.getHeight() - last.

        node.setHeight(t)

        for child in node.children:
            if child == last:
                continue

            self.calcNodeHeightsRecurse(child, node)

        for parent in node.parents:
            if parent == last:
                continue

            self.calcNodeHeightsRecurse(
