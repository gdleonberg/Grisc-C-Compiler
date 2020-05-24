import parsing.tree as tree
import copy

def prune(node, depth):
    retVal = 0
    for child in node.getChildren():
        retVal += prune(child, depth + 1)
    if node.getChildren() == []:
        if (node.value == [None, None, None, None, None]) and (node.rule not in ["scope_rise", "scope_drop"]):
            if node.getParent() != None:
                node.parent.removeChild(node)
                retVal += 1
    return retVal

def renamePrimes(node):
    if not(node.rule is None):
        node.rule = node.rule.replace("_prime", "")
    if not(node.subRule is None):
        node.subRule = node.subRule.replace("_prime", "")
    for child in node.children:
        renamePrimes(child)

def flattenRepetition(node):

    # if child rule ends in _prime and subRule is None and value[0] is None, replace child with its children
    flag = True
    while flag:
        flag = False
        for i, child in enumerate(node.children):
            if child.rule.endswith("_prime") and (child.subRule is None) and (child.value[0] is None) and (len(child.children) != 0):
                node.children = node.children[:i] + node.children[i].children + node.children[i+1:]
                flag = True
                break

    # work top down
    for child in node.children:
        flattenRepetition(child)

def removeSuperfluousGroupingAndSeperators(node):
    
    flag = True
    while flag:
        flag = False 
        for i in range(0, len(node.children)):
            if (node.children[i].value[0] in ['{', '}', '(', ')', ';', ',', '[', ']']) or (node.children[i].subRule == "EOF"):
                del node.children[i]
                flag = True
                break

    for child in node.children:
        removeSuperfluousGroupingAndSeperators(child)

def removeSingleSuccessors(node):

    flag = True
    while flag:
        flag = False
        if (len(node.children) == 1) and (node.rule not in ["array_optional", "array_optional_prime"]):
            node.become(node.children[0])
            flag = True

    for child in node.children:
        removeSingleSuccessors(child)

def toAst(cst):
    ast = copy.deepcopy(cst)

    # remove all superfluous parantheses and curly braces
    removeSuperfluousGroupingAndSeperators(ast)

    while(prune(ast, 0)):
        pass

    # flatten all repetition that's represented as recursion
    flattenRepetition(ast)

    # remove all single-sucessor nodes
    removeSingleSuccessors(ast)

    # rename _prime nodes
    renamePrimes(ast)

    # update depth property of all nodes in tree (used for calculating scope during symbol and type checking)
    ast.updateDepth(0)

    return ast