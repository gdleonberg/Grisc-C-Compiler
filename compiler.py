import sys
import io
import lexing.preProcessor as preProcessor
import lexing.lexer as lexer
import parsing.tokenConverter as tokenConverter
import parsing.genParser as genParser
import parsing.tree as tree
import parsing.cstToAst as cstToAst
import analysis.graphVisualizer as graphVisualizer
import analysis.symbolTable as symbolTable

# store old stdout for print redirection
old_stdout = sys.stdout

# get command line arguments
inFilename = sys.argv[1]
outFilename = sys.argv[2]
parserDebug = False
if len(sys.argv) > 3:
    parserDebug = True

# generate parser from bnf
try:
    genParser.generateFromBnf("autoGenParser.py", "grammars/grammar.bnf", parserDebug)
except genParser.genParserError as e:
    print(e)
    quit()
import parsing.autoGenParser as autoGenParser

# resolve all includes and get final lexed program
try:
    tokens = preProcessor.preProcessor(inFilename).preProcess()
    with open("logs/1_preProcessedTokens.log", "w") as outFile:
        for token in tokens:
            outFile.write("{0:<60s}".format("'" + token[0] + "'") + " : " + "{0:<15s}".format(token[1])
                        + " : " + "{0:<15s}".format(token[2]) + " : " +"{0:<15s}".format(token[3])
                        + " : " + "{0:<15s}".format(token[4]) + "\n")
except (preProcessor.preProcessorError, lexer.lexerError) as e:
    print(e)
    quit()

## feed to parser to make CST
## (https://dev.to/lefebvre/compilers-102---parser-2gni)
tokens = tokenConverter.tokenConverter(tokens).convert()
with open("logs/2_convertedTokens.log", "w") as outFile:
    for token in tokens:
        outFile.write("{0:<60s}".format("'" + token[0] + "'") + " : " + "{0:<15s}".format(token[1])
                    + " : " + "{0:<15s}".format(token[2]) + " : " +"{0:<15s}".format(token[3])
                    + " : " + "{0:<15s}".format(token[4]) + "\n")

myParser = autoGenParser.parser(tokens)

new_stdout = io.StringIO()
sys.stdout = new_stdout
parseStatus, parseTree = myParser.parse()
parseDebugLog = new_stdout.getvalue()

new_stdout = io.StringIO()
sys.stdout = new_stdout
parseTree.pprint()
pprintedParseTree = new_stdout.getvalue()

new_stdout = io.StringIO()
sys.stdout = new_stdout
while(cstToAst.prune(parseTree, 0)):
    pass
pruneLog = new_stdout.getvalue()

new_stdout = io.StringIO()
sys.stdout = new_stdout
parseTree.pprint()
pprintedParseTreePruned = new_stdout.getvalue()

sys.stdout = old_stdout
print(parseStatus)

with open("logs/3_parse.log", "w") as log:
    log.write(parseDebugLog)
    log.write("\n\n\n")
    log.write(parseStatus)
with open("logs/4_CST.log", "w") as log:
    log.write(pprintedParseTreePruned)
if("failure" in parseStatus):
    exit(0)

# make AST from CST
ast = cstToAst.toAst(parseTree)
new_stdout = io.StringIO()
sys.stdout = new_stdout
ast.pprint(False)
astText = new_stdout.getvalue()
with open("logs/5_AST.log", "w") as log:
    log.write(astText)

# print post-order traversal of AST to log
new_stdout = io.StringIO()
sys.stdout = new_stdout
ast.postorderPprint(False)
astText = new_stdout.getvalue()
with open("logs/5_AST_postorder.log", "w") as log:
    log.write(astText)

# generate png of tree and hide tree too large warning
new_stderr = io.StringIO()
sys.stderr = new_stderr
graphVisualizer.visualize(ast, "logs/5_AST.png")
sys.stderr = old_stderr

# apply symbol table checking
new_stdout = io.StringIO()
sys.stdout = new_stdout
mySymbolTable = symbolTable.symbolTable(ast)
try:
    mySymbolTable.addSymbols()
    symbolTableText = new_stdout.getvalue()
    with open("logs/6_symbolTable.log", "w") as log:
        log.write(symbolTableText)
except symbolTable.symbolTableError as e:
    sys.stdout = old_stdout
    print(e)
    symbolTableText = new_stdout.getvalue()
    with open("logs/6_symbolTable.log", "w") as log:
        log.write(symbolTableText)
    quit()


# restore stdout
sys.stdout = old_stdout

# print final generated code
#with open(outFilename, "w") as outFile:
#    outFile.write(str(parseTree))

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