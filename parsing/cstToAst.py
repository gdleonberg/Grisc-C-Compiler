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

    repFlag = True
    while repFlag:
        repFlag = False
        for child in node.getChildren():
            retValAdd = flattenRepetition(child)
            retVal += retValAdd
            if retValAdd != 0:
                repFlag = True

    for i, child in enumerate(node.getChildren()):
        if (child.rule == node.rule + "_prime"):# or (child.rule == node.rule):
            print("At node: " + node.toString() + " Flattening " + child.toString())
            temp = copy.copy(child.children)
            for newChild in temp:
                newChild.updateDepth(node.depth + 1)
            node.children = node.children[:i] + temp  + node.children[i+1:]
            retVal += 1

    return retVal

def removeSuperfluousGrouping(node):
    retVal = 0

    return retVal

def removeSingleSuccessors(node):
    retVal = 0

    # if the node only has one child, replace itself with the child
    flag = True
    while flag:
        flag = False
        if len(node.children) == 1:
            node.become(node.children[0])
            node.updateDepth(node.depth)
            flag = True

    # call recursively on each child
    else:
        for child in node.children:
            removeSingleSuccessors(child)

    return retVal

def toAst(cst):
    ast = copy.deepcopy(cst)

    # flatten all repetition that's represented as recursion
    while(flattenRepetition(ast)):
        pass

    # remove all superfluous parantheses and curly braces
    #while(removeSuperfluousGrouping(ast)):
    #    pass

    # remove all single-sucessor nodes
    while(removeSingleSuccessors(ast)):
        pass

    cst.updateDepth(0)

    return ast