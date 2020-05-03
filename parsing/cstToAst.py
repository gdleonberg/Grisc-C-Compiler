import parsing.tree as tree
import copy

def prune(node, depth):
    retVal = 0
    for child in node.getChildren():
        retVal += prune(child, depth + 1)
    if node.getChildren() == []:
        print((depth * "\t") + "Node has no children: " + node.toString())
        if node.value == [None, None, None, None, None]:
            print((depth * "\t") + "Node has empty value")
            if node.getParent() != None:
                print((depth * "\t") + "Node has parent. Pruning...")
                node.parent.removeChild(node)
                retVal += 1
    return retVal

def flattenRepetition(node):
    retVal = 0

    for i, child in enumerate(node.getChildren()):
        if child.rule == node.rule + "_prime":
            print("At node: " + node.toString() + " Flattening " + child.toString())
            temp = copy.deepcopy(child.children)
            for newChild in temp:
                newChild.updateDepth(node.depth + 1)
            node.children = node.children[:i] + temp  + node.children[i+1:]
            retVal += 1

    for child in node.getChildren():
        retVal += flattenRepetition(child)

    return retVal

def removeSuperfluousGrouping(node):
    retVal = 0

    return retVal

def removeSingleSuccessors(node):
    retVal = 0

    for i, child in enumerate(node.getChildren()):
        if child.rule == node.rule + "_prime":
            print("At node: " + node.toString() + " Flattening " + child.toString())
            temp = copy.deepcopy(child.children)
            for newChild in temp:
                newChild.updateDepth(node.depth + 1)
            node.children = node.children[:i] + temp  + node.children[i+1:]
            retVal += 1

    for child in node.getChildren():
        retVal += flattenRepetition(child)

    return retVal

def toAst(cst):
    ast = copy.deepcopy(cst)

    # flatten all repetition that's represented as recursion
    while(flattenRepetition(ast)):
        pass

    # remove all superfluous parantheses and curly braces
    while(removeSuperfluousGrouping(ast)):
        pass

    # remove all single-sucessor nodes
    while(removeSingleSuccessors(ast)):
        pass

    return ast