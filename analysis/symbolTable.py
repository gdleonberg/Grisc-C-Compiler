import copy
import inspect

integrals = {"char" : 1, "int" : 4, "short" : 2, "long" : 4, "float" : 4, "double" : 8, "bool" : 1}

class symbolTableError(Exception):
    pass

class Variable:
    def __init__(self, name, m_type, pointerDepth, arrayLen):
        self.name = name
        self.pointerDepth = pointerDepth
        self.type = m_type
        self.arrayLen = arrayLen

class Integral:
    def __init__(self, m_type):
        self.classType = "integral"
        self.type = m_type
        self.size = integrals[m_type]

class Enum:
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

class Union:
    def __init__(self, name, members):
        self.classType = "union"
        self.name = name
        self.members = members
        self.size = 0
        for member in self.members:
            if member.size > self.size:
                self.size = member.size

class Struct:
    def __init__(self, name, members):
        self.classType = "struct"
        self.name = name
        self.members = members
        self.memberLocs = []
        self.size = 0
        for member in self.members:
            self.memberLocs.append(self.size)
            self.size += member.size

class Typedef:
    def __init__(self, origType, newType):
        self.classType = "typedef"
        self.orig = origType
        self.new = newType

def getTokenList(node):
    retTokens = []
    retTokens.append(node)
    for child in node.children:
        tokens = getTokenList(child)
        for token in tokens:
            retTokens.append(token)
    return retTokens

class symbolTable:

    def __init__(self, ast):
        self.definitions = {}
        self.variables = {}
        self.ast = ast
        self.tokens = getTokenList(self.ast)

        for key in integrals:
            self.definitions[key] = Integral(key)

        print("Integrals are: " + ", ".join([(str(key) + ":" + str(self.definitions[key].size)) for key in self.definitions]) + "\n\n")

    # collect definitions as we encounter them
    # check variables against definitions as we encounter them
    # collect variables as encounter them
    def addSymbols(self):

        i = 0
        while i < len(self.tokens):
            
            incVal = 0
            oldSymbolTable = copy.copy(self) #copy.deepcopy(self)

            if incVal == 0:
                incVal = self.tryVariable(i)
            if incVal == 0:
                incVal = self.tryDefinition(i)

            for loc in range(0, incVal):
                self.tokens[i + loc].symbolTable = oldSymbolTable

            if incVal == 0:
                incVal = 1
            i += incVal
            
        
    def tryVariable(self, currPos):

        incVal = 0

        if self.tokens[currPos + incVal].rule != "variable_declarations_and_optional_assignments":
            return 0

        print("Begin list of variable declarations and optional assignments")

        if not (self.tokens[currPos + incVal].value[0] is None):
            print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
        incVal += 1

        # get total type
        if (self.tokens[currPos + incVal].rule != "type") and (self.tokens[currPos + incVal].rule != "total_type"):
            print("No type!")
            return 0
        
        currDepth = self.tokens[currPos + incVal].depth
        if self.tokens[currPos + incVal].rule == "total_type":
            if not (self.tokens[currPos + incVal].value[0] is None):
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
            incVal += 1

        total_type = []
        if (self.tokens[currPos + incVal].rule == "type"):
            total_type.append(self.tokens[currPos + incVal].value[0])
            if not (self.tokens[currPos + incVal].value[0] is None):
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
            incVal += 1
        else:
            while self.tokens[currPos + incVal].depth != currDepth:
                total_type.append(self.tokens[currPos + incVal].value[0])
                if not (self.tokens[currPos + incVal].value[0] is None):
                    print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1
                

        if len(total_type) == 0:
            print("No total type!")
            return 0

        print("Total type is: \"" + " ".join(total_type) + "\"")

        # for each variable in the list
        variable_list = []
        while self.tokens[currPos + incVal].depth >= currDepth:

            # get pointer amount
            pointer_depth = 0
            while self.tokens[currPos + incVal].rule == "pointer_optional":
                if self.tokens[currPos + incVal].value[0] == '*':
                    pointer_depth += 1
                if not (self.tokens[currPos + incVal].value[0] is None):
                    print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1
                

            print("Pointer depth is " + str(pointer_depth))

            if (self.tokens[currPos + incVal].value[1] != "IDENTIFIER"):
                return 0

            # get variable name
            variable_name = self.tokens[currPos + incVal].value[0]
            if self.tokens[currPos + incVal].value[0] is not None:
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
            print("Variable name is \"" + variable_name + "\"")
            incVal += 1

            # if it's an array, we need to calculate the size and record it
            array_value = None
            if self.tokens[currPos + incVal].rule == "array_optional":
                print("Array found!")
                
                #print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1

                while self.tokens[currPos + incVal].value[0] is None:
                    #print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                    incVal += 1

                array_expr, currPos, incVal = self.collectArrayExpr(currPos, incVal)

                print("Array expression is: " + str(array_expr))

                # evaluate array expression
                if array_expr != []:
                    array_value = self.evaluate(array_expr)
                    print("Simplified array expression is: [" + str(array_value) + "]")
                else:
                    array_value = "empty"
                    print("Simplified array expression is: [" + str(array_value) + "]")



            # if we find an assignment, we need to check cast types and variable names
            # we also need to use initializer list length to calculate sizeof if there is one
            if self.tokens[currPos + incVal].rule == "assignment":
                print("Assignment found!")
                currDepth2 = self.tokens[currPos + incVal].depth
                if not (self.tokens[currPos + incVal].value[0] is None):
                    print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1
                while self.tokens[currPos + incVal].depth > currDepth2:

                    # if identifier, check against defined variables or typedef
                    #if self.tokens[currPos + incVal].value[1] == "IDENTIFIER":

                        # check if is declared variable or is enum value

                    # else if struct or enum, collect and then collect identifier and check against defined types
                    #elif (self.tokens[currPos + incVal].value[0] == "enum") or ()

                    # else advance to next token
                    #else:
                    if not (self.tokens[currPos + incVal].value[0] is None):
                        print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                    incVal += 1
                    
                print("End assignment")
                    

            variable_list.append([pointer_depth, variable_name, array_value])

        
        # for all variables, add them to our symbol table
        for var in variable_list:
            array_str = ""
            if var[2] is not None:
                array_str = "[" + str(var[2]) + "]"
            else:
                var[2] = 0
            print("Adding \"" + " ".join(total_type) + " " + ("*" * var[0]) + var[1] + array_str + "\"")
            self.variables[var[1]] = Variable(var[1], " ".join(total_type), var[0], var[2])
        
        print("")
        
        return incVal

    def collectArrayExpr(self, currPos, incVal):

        array_expr = []
        currDepth = self.tokens[currPos + incVal].depth
        while self.tokens[currPos + incVal].depth >= currDepth:

            if self.tokens[currPos + incVal].depth > currDepth:
                #print("Calling collectArrayExpr")
                temp_array_expr, currPos, incVal = self.collectArrayExpr(currPos, incVal)
                array_expr.append(temp_array_expr)

            else:
                if (self.tokens[currPos + incVal].value[0] is not None) and (self.tokens[currPos + incVal].value[0] not in ['[', ']']):
                    array_expr.append(self.tokens[currPos + incVal].value[0])
                #print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1
            
        #print("Returning: " + str(array_expr))
        return array_expr, currPos, incVal

    def evaluate(self, expression):

        operators = {    
        "+" : lambda x, y: x + y,
        "-" : lambda x, y: x - y,
        "/" : lambda x, y: x // y,
        "*" : lambda x, y: (x * y) // 1,
        "%" : lambda x, y: (x % y) // 1,
        "<<" : lambda x, y: x << y,
        ">>" : lambda x, y: x >> y
        }

        flatList = []

        # for each term in list
        for term in expression:
        
            # if is single term, add it to our flattened expression
            if type(term) != list:
                #print("Append to list: " + str(term))
                flatList.append(term)

            # if is list, call evaluate on it and add result term to our flattened expression
            else:
                #print("Call evaluate on subterm: " + str(term))
                flatList.append(self.evaluate(term))

        # evaluate flattened expression left to right
        retVal = "-1"
        
        # is sizeof
        if flatList[0] == "sizeof":
            if flatList[1] in self.variables:
                if(self.variables[flatList[1]].pointerDepth != 0):
                    retVal = integrals["int"]
                elif self.variables[flatList[1]].type in self.definitions:
                    if self.variables[flatList[1]].arrayLen != 0:
                        retVal = self.definitions[self.variables[flatList[1]].type].size * self.variables[flatList[1]].arrayLen
                    else:
                        retVal = self.definitions[self.variables[flatList[1]].type].size
                else:
                    raise symbolTableError("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": Undefined type '" + self.variables[flatList[1]].type + "' for variable '" + flatList[1] + "'")
            elif flatList[1] in self.definitions:
                retVal = self.definitions[flatList[1]].size
            else:
                raise symbolTableError("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ": Unable to evaluate sizeof for: " + str(flatList))

            #print(str(flatList) + " = " + str(retVal))

        # is normal math expression on constants
        elif len(flatList) > 1:
            retVal = flatList[0]
            i = 1
            while i < len(flatList):
                if flatList[i] in operators:
                    #print("A operand is: " + str(retVal))
                    #print("Operator is: " + str(flatList[i]))
                    #print("B operand is: " + str(flatList[i + 1]))
                    retVal = operators[flatList[i]](int(retVal), int(flatList[i + 1]))
                else:
                    print("Error in evaluating constant expression!")
                    return -1
                i += 2

        # is a single constant with no operations on it
        else:
            retVal = flatList[0]

        return str(retVal)
    
    def tryDefinition(self, currPos):

        incVal = 0

        if incVal == 0:
           incVal = self.tryUnion(currPos)

        if incVal == 0:
            incVal = self.tryStruct(currPos)

        if incVal == 0:
            incVal = self.tryEnum(currPos)

        if incVal == 0:
            incVal = self.tryTypedef(currPos)

        return incVal

    def tryUnion(self, currPos):

        incVal = 0

        return incVal

    def tryStruct(self, currPos):

        incVal = 0

        return incVal

    def tryEnum(self, currPos):

        incVal = 0

        return incVal

    def tryTypedef(self, currPos):

        incVal = 0

        return incVal

    