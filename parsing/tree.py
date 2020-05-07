class tree:

    def __init__(self, rule, subRule, value):
        self.rule = rule
        self.subRule = subRule
        self.value = value
        self.parent = None
        self.children = []
        self.depth = 0

    def become(self, node):
        self.rule = node.rule
        self.subRule = node.subRule
        self.value = node.value
        self.children = node.children
        
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
            childNode.updateDepth(child.depth)

        self.children.append(child)

    def updateDepth(self, depth):
        self.depth = depth
        for child in self.getChildren():
            child.updateDepth(depth + 1)

    def getDepth(self):
        return self.depth

    def getParent(self):
        return self.parent

    def getChildren(self):
        return self.children

    def findChild(self, childRef):
        childIndex = -1
        for i, child in enumerate(self.children):
            if child is childRef:
                childIndex = i
        return childIndex

    def removeChild(self, childRef):
        print("Node: " + self.toString() + " Removing child: " + childRef.toString())
        childIndex = self.findChild(childRef) 
        if childIndex != -1:
            print("Child found at index " + str(childIndex))
            print(self.children)
            self.children.pop(childIndex)
            print("Child removed")
            print(self.children)
        else:
            print("Child not found")

    def toString(self):
        return str(self.rule) + " | " + str(self.subRule) + " | " + str(self.value[0])

    def pprint(self, drawSpacers=True, _prefix="", _last=True):
        
        if drawSpacers:
            if(self.value[0] != None):
                print(_prefix, "`- " if _last else "|- ", self.toString(), sep="")
            else:
                print(_prefix, "`- " if _last else "|- ", str(self.rule), sep="")
            _prefix += "   " if _last else "|  "
        else:
            if(self.value[0] != None):
                print(_prefix, "   ", self.toString(), sep="")
            else:
                print(_prefix, "   ", str(self.rule), sep="")
            _prefix += "   "

        child_count = len(self.getChildren())
        for i, child in enumerate(self.getChildren()):
            _last = i == (child_count - 1)
            child.pprint(drawSpacers, _prefix, _last)
