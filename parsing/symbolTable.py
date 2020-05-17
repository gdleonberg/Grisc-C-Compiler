integrals = {"char" : 1, "int" : 4, "short" : 2, "long" : 4, "float" : 4, "double" : 8, "pointer" : 4, "bool" : 1}

class variable:
    def __init__(self, name, m_type, pointerDepth):
        self.name = name
        self.pointerDepth = pointerDepth

class integral:
    def __init__(self, m_type):
        self.classType = "integral"
        self.type = m_type
        self.size = integrals[m_type]

class enum:
    def __init__(self, name, members):
        self.classType = "enum"
        self.name = name
        self.options = options
        self.size = integrals["int"]

        # first value is 0 if not defined, every subsequent value is previous + 1 if not defined
        for i in range(0, len(self.members)):
            if self.members[self.members.keys()[i]] is None:
                if i == 0:
                    self.members[self.members.keys()[i]] = 0
                else:
                    self.members[self.members.keys()[i]] = self.members[self.members.keys()[i - 1]] + 1

class struct:
    def __init__(self, name, members):
        self.classType = "struct"
        self.name = name
        self.members = members
        self.size = 0
        for member in self.members:
            self.size += member.size

class typedef:
    def __init__(self, origType, newType):
        self.classType = "typedef"
        self.orig = origType
        self.new = newType

class symbolTable:

    def __init__(self, ast):
        self.definitions = []
        self.variables = []
        self.ast = ast

        for key in integrals:
            self.definitions.append((None, integral(key))) 

    # do a post-order traversal
    # collect definitions as we encounter them
    # check variables against definitions as we encounter them
    # collect variables as encounter them
    def traverse(self):
        
        # do a post-order traversal


        pass
        