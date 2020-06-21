import copy
import inspect
from random import randint

integrals = {"char" : 1, "int" : 4, "short" : 2, "long" : 4, "float" : 4, "double" : 8, "bool" : 1}
type_qualifiers = ["unsigned", "const"]
type_qualifiers_sorted = {
    "sign" : ["unsigned"],
    "misc" : ["const"]
}
qualifiable_integrals = {
    "sign_misc" : ["char", "int", "short", "long"],
    "misc" : ["bool", "float", "double"]
}


def list_is_unique(listIn):
    uniques = []
    for item in listIn:
        if item not in uniques:
            uniques.append(item)
        else:
            return False
    return True

def dissectType(total_type):
    unsigned = False
    const = False
    constPtr = False
    type_tokens = total_type.split(" ")
    baseType = " ".join([word for word in type_tokens if word not in type_qualifiers])

    if total_type.find(baseType) != 0:
        if "const" in total_type.split(baseType)[0].split(" "):
            const = True
        if "unsigned" in total_type.split(baseType)[0].split(" "):
            unsigned = True

    if (total_type.find(baseType) + len(baseType)) != len(total_type):
        if "const" in total_type[total_type.find(baseType) + len(baseType):].split(" "):
            constPtr = True
    
    return baseType, const, constPtr, unsigned

class symbolTableError(Exception):
    pass

class Variable:
    def __init__(self, name, m_type, pointerDepth, arrayLen, symbolTable):
        self.name = name
        self.pointerDepth = int(pointerDepth)
        self.type, self.const, self.constPtr, self.unsigned = dissectType(m_type)
        self.arrayLen = int(arrayLen)
        self.size = symbolTable.definitions[self.type].size
        if pointerDepth > 0:
            self.size = integrals["int"]
        if self.arrayLen > 1:
            self.size *= self.arrayLen

    def toString(self):
        return " ".join([val for val in [(self.const * "const"), (self.unsigned * "unsigned"), self.type, (self.pointerDepth * '*'), (self.constPtr * "const"), self.name, ((self.arrayLen > 1) * ("[" + str(self.arrayLen) + "]")), "(size: " + str(self.size) + ")"] if val != ""])

class Integral:
    def __init__(self, m_type):
        self.classType = "integral"
        self.type = m_type
        self.size = integrals[m_type]
    def toString(self):
        return " ".join([self.type])

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

    def toString(self):
        retStr = "enum " + self.name
        for option in self.options:
            retStr += "\t" + option + ": " + str(self.options[option]) + "\n"
        return retStr

class Union:
    def __init__(self, name, members):
        self.classType = "union"
        self.name = name
        self.members = members
        self.size = 0
        for member in self.members:
            if member.size > self.size:
                self.size = member.size

    def toString(self):
        retStr = "union " + self.name + " (size: " + str(self.size) + ")\n"
        for member in self.members:
            retStr += "\t" + member.toString() + "\n"
        return retStr

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

    def toString(self):
        retStr = "struct " + self.name + " (size: " + str(self.size) + ")\n"
        for i in range(0, len(self.members)):
            retStr += "\toffset " + str(self.memberLocs[i]) + ": " + self.members[i].toString() + "\n"
        return retStr

class Typedef:
    def __init__(self, origType, newType):
        self.classType = "typedef"
        self.orig = origType
        self.new = newType
    def toString(self):
        return " ".join(["typedef", self.orig, self.new])

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
        self.anonymousNames = []
        self.definitions = {}
        self.variables = {}
        self.ast = ast
        self.tokens = getTokenList(self.ast)

        for key in integrals:
            self.definitions[key] = Integral(key)

        print("Integrals are: " + ", ".join([(str(key) + ":" + str(self.definitions[key].size)) for key in self.definitions]) + "\n\n")

    def checkTotalType(self, total_type):

        # check base type is valid (is either integral or defined)
        base_type = " ".join([word for word in total_type if word not in type_qualifiers])
        if not ((base_type in integrals) or (base_type in self.definitions)):
            raise symbolTableError("Unknown base type: " + base_type)
            return False

        # check qualifiers are valid
        qualifier_level = "misc"
        if base_type in integrals:
            for level in qualifiable_integrals:
                if base_type in qualifiable_integrals[level]:
                    qualifier_level = level
                    break
        allowed_qualifiers = []
        for qualifier_category in qualifier_level.split("_"):
            allowed_qualifiers += type_qualifiers_sorted[qualifier_category]
        local_qualifiers = [word for word in total_type if word in type_qualifiers]
        if list_is_unique(local_qualifiers):
            for local_qualifier in local_qualifiers:
                if not(local_qualifier in allowed_qualifiers):
                    raise symbolTableError("Qualifier " + local_qualifier + " not in allowed qualifiers " + str(allowed_qualifiers))
                    return False
        else:
            raise symbolTableError("Qualifier list contains duplicate qualifiers: " + str(local_qualifiers))
            return False
            
        return True

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
            
        
    def tryVariable(self, currPos, parseOnly=False):

        incVal = 0

        if self.tokens[currPos + incVal].rule not in ["variable_declarations_and_optional_assignments", "variable_declarations_and_no_assignments"]:
            return 0

        print("Begin list of variable declarations and optional assignments")

        if not (self.tokens[currPos + incVal].value[0] is None):
            print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
        incVal += 1

        # get total type
        if (self.tokens[currPos + incVal].rule != "type") and (self.tokens[currPos + incVal].rule != "total_type"):
            print("No type!")
            return 0
        
        currDepth = self.tokens[currPos + incVal].depth
        if self.tokens[currPos + incVal].rule == "total_type":
            if not (self.tokens[currPos + incVal].value[0] is None):
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
            incVal += 1

        total_type = []
        if (self.tokens[currPos + incVal].rule == "type"):
            if not (self.tokens[currPos + incVal].value[0] is None):
                total_type.append(self.tokens[currPos + incVal].value[0])
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
            incVal += 1
        else:
            while self.tokens[currPos + incVal].depth != currDepth:
                if not (self.tokens[currPos + incVal].value[0] is None):
                    total_type.append(self.tokens[currPos + incVal].value[0])
                    print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1
                
        if len(total_type) == 0:
            raise symbolTableError("No total type!")
            return 0

        print("Total type is: \"" + " ".join(total_type) + "\"")

        self.checkTotalType(total_type)

        # for each variable in the list
        print("Currdepth is: " + str(currDepth))
        variable_list = []
        while self.tokens[currPos + incVal].depth >= currDepth:

            # get pointer amount
            pointer_depth = 0
            if self.tokens[currPos + incVal].value == [None, None, None, None, None]:
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1
            while self.tokens[currPos + incVal].rule in ["pointer_optional", "pointer"]:
                if self.tokens[currPos + incVal].value[0] == '*':
                    pointer_depth += 1
                if not (self.tokens[currPos + incVal].value[0] is None):
                    print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1

            print("Pointer depth is " + str(pointer_depth))
            
            # check for pointer to const value
            constPtr = False
            if (pointer_depth > 0) and (self.tokens[currPos + incVal].value[0] == "const"):
                constPtr = True
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1

            if (self.tokens[currPos + incVal].value[1] != "IDENTIFIER"):
                print("Expected IDENTIFIER: " + str(self.tokens[currPos + incVal].value) + ", rule: " + self.tokens[currPos + incVal].rule)
                return 0

            # get variable name
            variable_name = self.tokens[currPos + incVal].value[0]
            if self.tokens[currPos + incVal].value[0] is not None:
                print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
            print("Variable name is \"" + variable_name + "\"")
            incVal += 1

            # if it's an array, we need to calculate the size and record it
            array_value = None
            if self.tokens[currPos + incVal].rule == "array_optional":
                print("Array found!")
                
                #print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                incVal += 1

                while self.tokens[currPos + incVal].value[0] is None:
                    #print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
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
                    print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
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
                        print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
                    incVal += 1
                    
                print("End assignment")
                    
            print("Adding to variable list: " + str([pointer_depth, variable_name, array_value]))
            variable_list.append([pointer_depth, variable_name, array_value, constPtr])

        
        # for all variables, add them to our symbol table
        parseOnlyRet = []
        print("Variable list is: " + str(variable_list))
        for var in variable_list:
            array_str = ""
            if var[2] is not None:
                array_str = "[" + str(var[2]) + "]"
            else:
                var[2] = 0
            print("Adding \"" + " ".join(total_type) + " " + ("*" * var[0]) + (" const " * var[3])  + var[1] + array_str + "\"")

            if not parseOnly:
                self.variables[var[1]] = Variable(var[1], " ".join(total_type) + (" const" * var[3]), var[0], var[2], self)
            else:
                parseOnlyRet.append(Variable(var[1], " ".join(total_type) + (" const" * var[3]), var[0], var[2], self))
        
        print("")
        
        if parseOnly:
            return parseOnlyRet, incVal
        else:
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
                #print("symbolTable.py line " + str(inspect.currentframe().f_lineno) + ", Depth " + str(self.tokens[currPos + incVal].depth) +  ": AST token " + str(currPos + incVal + 1) + ": " + str(self.tokens[currPos + incVal].value))
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

        # rule struct_or_union_declaration
        if self.tokens[currPos + incVal].rule != "struct_or_union_declaration":
            return 0
        incVal += 1

        # rule is struct_or_union and value is union
        if self.tokens[currPos + incVal].value[0] != "union":
            return 0
        incVal += 1

        # check for identifier and check uniqueness
        name = "anonymous_identifier_" + str(randint(10000, 99999))
        while name in self.anonymousNames:
            name = "anonymous_identifier_" + str(randint(10000, 99999))
        if self.tokens[currPos + incVal].rule == "identifier_optional":
            name = self.tokens[currPos + incVal].value[0]
            incVal += 1
        else:
            self.anonymousNames.append(name)
        if name in self.definitions:
            raise symbolTableError("Type name '" + name + "' already in use")
            return 0

        print("union " + name + "\nSearching for members...")

        # go through member list
        members = []
        if self.tokens[currPos + incVal].rule != "struct_or_union_member_list":
            raise symbolTableError("Expected union member list")
            return 0
        incVal += 1
        curDepth = self.tokens[currPos + incVal].depth
        while self.tokens[currPos + incVal].depth >= curDepth:
            parseRet = self.tryVariable(currPos + incVal, True)
            incVal += parseRet[1]
            for var in parseRet[0]:
                members.append(var)

        print("Members are:")
        for member in members:
            print(member.toString())

        self.definitions["union " + name] = Union(name, members)
        print("Adding " + self.definitions["union " + name].toString())

        return incVal

    def tryStruct(self, currPos):

        incVal = 0

        # rule struct_or_union_declaration
        if self.tokens[currPos + incVal].rule != "struct_or_union_declaration":
            return 0
        incVal += 1

        # rule is struct_or_union and value is struct
        if self.tokens[currPos + incVal].value[0] != "struct":
            return 0
        incVal += 1

        # check for identifier and check uniqueness
        name = "anonymous_identifier_" + str(randint(10000, 99999))
        while name in self.anonymousNames:
            name = "anonymous_identifier_" + str(randint(10000, 99999))
        if self.tokens[currPos + incVal].rule == "identifier_optional":
            name = self.tokens[currPos + incVal].value[0]
            incVal += 1
        else:
            self.anonymousNames.append(name)
        if name in self.definitions:
            raise symbolTableError("Type name '" + name + "' already in use")
            return 0

        print("struct " + name + "\nSearching for members...")

        # go through member list
        members = []
        if self.tokens[currPos + incVal].rule != "struct_or_union_member_list":
            raise symbolTableError("Expected struct member list")
            return 0
        incVal += 1
        curDepth = self.tokens[currPos + incVal].depth
        while self.tokens[currPos + incVal].depth >= curDepth:
            parseRet = self.tryVariable(currPos + incVal, True)
            incVal += parseRet[1]
            for var in parseRet[0]:
                members.append(var)

        print("Members are:")
        for member in members:
            print(member.toString())

        self.definitions["struct " + name] = Struct(name, members)
        print("Adding " + self.definitions["struct " + name].toString())

        return incVal

    def tryEnum(self, currPos):

        incVal = 0

        return incVal

    def tryTypedef(self, currPos):

        incVal = 0

        return incVal

    