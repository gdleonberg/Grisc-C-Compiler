import sys
import lexing.preProcessor as preProcessor
import lexing.lexer as lexer
import parsing.tokenConverter as tokenConverter
import parsing.genParser as genParser

inFilename = sys.argv[1]
outFilename = sys.argv[2]
parserDebug = False
if len(sys.argv) > 3:
    parserDebug = True

# generate parser from bnf
#genRules.generateFromBnf("autoGenParser.py", "handGrammar.bnf", parserDebug)
genParser.generateFromBnf("autoGenParser.py", "grammar.bnf", parserDebug)
import parsing.autoGenParser as autoGenParser

# resolve all includes and get final lexed program
tokens = preProcessor.preProcessor(inFilename).preProcess()
"""
with open(outFilename + ".lexed", "w") as outFile:
    for token in tokens:
        outFile.write("{0:<60s}".format("'" + token[0] + "'") + " : " + "{0:<15s}".format(token[1])
                    + " : " + "{0:<15s}".format(token[2]) + " : " +"{0:<15s}".format(token[3])
                    + " : " + "{0:<15s}".format(token[4]) + "\n")
"""

## feed to parser to make CST and then AST
## (https://dev.to/lefebvre/compilers-102---parser-2gni)
tokens = tokenConverter.tokenConverter(tokens).convert()
"""
with open(outFilename + ".converted", "w") as outFile:
    for token in tokens:
        outFile.write("{0:<60s}".format("'" + token[0] + "'") + " : " + "{0:<15s}".format(token[1])
                    + " : " + "{0:<15s}".format(token[2]) + " : " +"{0:<15s}".format(token[3])
                    + " : " + "{0:<15s}".format(token[4]) + "\n")
"""

myParser = autoGenParser.parser(tokens)
parseStatus, parseTree = myParser.parse()

print("Parse: " + str(parseStatus))
#cst = myParser.genCst()
#ast = myParser.genAst(cst)

with open(outFilename, "w") as outFile:
    outFile.write(str(parseTree))

## feed parsed program to semantic analyzer to check for errors,
## analyze type stuff for symbol table, and add implicit nodes to AST
## (https://dev.to/lefebvre/compilers-103--semantic-analyzer-540k)
# mySemanticAnalyzer = semanticAnalyzer.semanticAnalyzer(ast)
# mySemanticAnalyzer.validate()
# finalAst = mySemanticAnalyzer.genFinalAst()

## feed to IR generator
## (https://dev.to/lefebvre/compilers-104---ir-generation-39e8)
# myIrGen = irGen.irGen(finalAst)
# ircode = myIrGen.generateIr()

## feed to assembly generator
##
# myAsmGen = asmGen.asmGen(ircode)
# assembly = myAsmGen.genAsm()