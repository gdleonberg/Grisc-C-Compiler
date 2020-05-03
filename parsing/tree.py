def updateDepth(node, depth):
    node.depth = depth
    for child in node.getChildren():
        updateDepth(child, depth + 1)

def prune(node, depth):
    retVal = 0
    for child in node.getChildren():
        retVal += prune(child, depth + 1)
    if len(node.getChildren()) == 0:
        print((depth * "\t") + "Node has no children: " + node.toString())
        if (node.value == [None, None, None, None, None]):
            print((depth * "\t") + "Node has empty value")
            if node.getParent() != None:
                print((depth * "\t") + "Node has parent. Pruning...")
                node.parent.removeChild(node)
                retVal += 1
    return retVal

class tree:

    def __init__(self, rule, subRule, value):
        self.rule = rule
        self.subRule = subRule
        self.value = value
        self.parent = None
        self.children = []
        self.depth = 0

    def reset(self):
        self.children = []

    def addChildNode(self, rule, subRule, value):
        child = tree(rule, subRule, value)
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)

    def addChildTree(self, child):
        child.parent = self
        child.depth = self.depth + 1

        # update all child node depths in the subtree
        for childNode in child.getChildren():
            updateDepth(childNode, self.depth)

        self.children.append(child)

    def getDepth(self):
        return self.depth

    def getParent(self):
        return self.parent

    def getChildren(self):
        return self.children

    def removeChild(self, childRef):
        print("Node: " + self.toString() + " Removing child: " + childRef.toString())
        childIndex = -1
        for i, child in enumerate(self.getChildren()):
            if child is childRef:
                childIndex = i
        if childIndex != -1:
            print("Child found at index " + str(childIndex))
            print(self.children)
            self.children.pop(childIndex)
            print("Child removed")
            print(self.children)
        else:
            print("Child not found")

    def toString(self):
        return self.rule + " | " + self.subRule + " | " + str(self.value[0])

    def pprint(self, _prefix="", _last=True):
        if(self.value[0] != None):
            print(_prefix, "`- " if _last else "|- ", self.toString(), sep="")
        else:
            print(_prefix, "`- " if _last else "|- ", str(self.rule), sep="")
        _prefix += "   " if _last else "|  "
        child_count = len(self.getChildren())
        for i, child in enumerate(self.getChildren()):
            _last = i == (child_count - 1)
            child.pprint(_prefix, _last)
