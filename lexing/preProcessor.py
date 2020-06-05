import sys
import io
import os
import datetime
import lexing.lexer as lexer

class preProcessorError(Exception):
    pass

class preProcessor:

    def buildSource(self, openFile):
        source = []
        filepath = os.path.realpath(openFile.name).replace("\\", "/")
        filename = filepath.rsplit("/", 1)[1]
        currLine = 1
        for line in openFile:
            source.append([line, filename, currLine])
            currLine += 1
        return source
    
    def __init__(self, filename):
        
        self.protected = ["__FILE__", "__LINE__", "__BASE_FILE__", "__DATE__", "__TIME__", "NULL"]
        self.filename = filename

    def preProcess(self):
        inFile = open(self.filename, "r")
        filepath = os.path.realpath(inFile.name).replace("\\", "/")
        filename = filepath.rsplit("/", 1)[1]
        filepath = filepath.rsplit("/", 1)[0]
        
        defines = {"__FILE__" : '"' + filename + '"', "__LINE__" : 1}
        defines["NULL"] = '(void *)0'
        defines["__DATE__"] = '"' + datetime.date.today().strftime("%b %d %Y") + '"'
        defines["__TIME__"] = '"' + datetime.datetime.now().strftime("%H:%M:%S") + '"'
        defines["__BASE_FILE__"] = '"' + filename + '"'
        
        retTokens, defines = self.include(filename, filepath, defines)
        
        # combine adjacent string literals               
        finalTokens = []
        i = 0
        while i < len(retTokens):
            currToken = retTokens[i]
            if (currToken[1] == "string_literal") and (i < len(retTokens) - 1):
                i += 1
                while (retTokens[i][1] == "string_literal") and (i < len(retTokens)):
                    currToken[0] = currToken[0][:-1] + retTokens[i][0][1:]
                    if retTokens[i][3] != currToken[3]:
                        currToken[3] = retTokens[i][3]
                        currToken[4] += retTokens[i][4]
                    i += 1
                finalTokens.append(currToken)
            else:
                if "comment" not in currToken[1]:
                    finalTokens.append(currToken)
                i += 1
        retTokens = finalTokens
        
        return retTokens

    def include(self, filename, filepath, defines):
        
        retTokens = []
        defines["__FILE__"] = '"' + filename + '"'
        inFile = open(filepath + "/" + filename, "r")
        filepath = os.path.realpath(inFile.name).replace("\\", "/")
        filepath = filepath.rsplit("/", 1)[0]
        #print(filename)
        tempSource = self.buildSource(inFile)
        #print(tempSource)
        old_stdout = sys.stdout
        new_stdout = io.StringIO()
        sys.stdout = new_stdout
        tokens = lexer.lexer(tempSource, tempSource).lex()
        sys.stdout = old_stdout
        with open("logs/0_lexer.log", "w") as outFile:
            outFile.write(new_stdout.getvalue())
            for token in tokens:
                outFile.write("{0:<60s}".format("'" + token[0] + "'") + " : " + "{0:<15s}".format(token[1])
                            + " : " + "{0:<15s}".format(token[2]) + " : " +"{0:<15s}".format(token[3])
                            + " : " + "{0:<15s}".format(token[4]) + "\n")
        
        tokenNum = 0
        while tokenNum != len(tokens):
            
            defines["__LINE__"] = tokens[tokenNum][3]
            
            if tokens[tokenNum][1] == "preprocessor_command":
                if tokens[tokenNum][0].find("#define") == 0:
                    definedName = tokens[tokenNum][0].split()[1]
                    definedVal = 1
                    if len(tokens[tokenNum][0].split()) > 2:
                        definedVal = tokens[tokenNum][0].split(definedName, 1)[1]
                    if (definedName not in self.protected) and (definedName not in defines):
                        defines[definedName] = definedVal
                    else:
                        raise preProcessorError("Define error in file " + filename + " at line " + str(defines["__LINE__"]))
                    
                elif tokens[tokenNum][0].find("#undef") == 0:
                    definedName = tokens[tokenNum][0].split()[1]
                    if (definedName not in self.protected) and (definedName in defines):
                        del defines[definedName]
                    else:
                        raise preProcessorError("Undef error in file " + filename + " at line " + str(defines["__LINE__"]))
                    
                elif tokens[tokenNum][0].find("#ifdef") == 0:
                    definedName = tokens[tokenNum][0].split()[1]
                    if definedName not in defines:
                        endifStack = 1
                        while(endifStack != 0):
                            tokenNum += 1
                            if tokens[tokenNum][0] == "#endif":
                                endifStack -= 1
                            if (tokens[tokenNum][0].find("#ifdef") == 0) or (tokens[tokenNum][0].find("#ifndef") == 0):
                                endifStack += 1
                            #print("searching for endif: " + tokens[tokenNum][0])
                            #print("endifStack: " + str(endifStack))
                            
                elif tokens[tokenNum][0].find("#ifndef") == 0:
                    definedName = tokens[tokenNum][0].split()[1]
                    if definedName in defines:
                        endifStack = 1
                        while(endifStack != 0):
                            tokenNum += 1
                            if tokens[tokenNum][0] == "#endif":
                                endifStack -= 1
                            if (tokens[tokenNum][0].find("#ifdef") == 0) or (tokens[tokenNum][0].find("#ifndef") == 0):
                                endifStack += 1
                            #print("searching for endif: " + tokens[tokenNum][0])
                            #print("endifStack: " + str(endifStack))
                    
                elif tokens[tokenNum][0].find("#include") == 0:
                    includedFile = tokens[tokenNum][0].split("#include", 1)[1].split('"')[1].strip()
                    oldLine = defines["__LINE__"]
                    oldFileName = defines["__FILE__"]
                    #print("Including: " + includedFile)
                    retTokensInclude, defines = self.include(includedFile, filepath, defines)
                    defines["__FILE__"] = oldFileName
                    defines["__LINE__"] = oldLine
                    for token in retTokensInclude:
                        retTokens.append(token)
                    
            else:
                                
                if (tokens[tokenNum][1] != "identifier") or (tokens[tokenNum][0] not in defines):
                    retTokens.append(tokens[tokenNum])
                    
                else: 
                    # substitute recursively until we can't any more
                    expanded_macro = str(defines[tokens[tokenNum][0]])
                    loopFlag = True
                    while loopFlag:
                        loopFlag = False
                        #print("expanded macro: '" + expanded_macro + "'")
                        old_stdout = sys.stdout
                        new_stdout = io.StringIO()
                        sys.stdout = new_stdout
                        localTokens = lexer.lexer([[expanded_macro, filename, defines["__LINE__"]]], self.buildSource(inFile)).lex()  
                        sys.stdout = old_stdout
                        currLocalToken = 0
                        while currLocalToken != len(localTokens):
                            if (localTokens[currLocalToken][1] != "identifier") or (localTokens[currLocalToken][0] not in defines):
                                retTokens.append([localTokens[currLocalToken][0], localTokens[currLocalToken][1], localTokens[currLocalToken][2], localTokens[currLocalToken][3], tokens[tokenNum][4], localTokens[currLocalToken][5]])
                                currLocalToken += 1
                            else:
                                
                                expanded_macro = str(defines[localTokens[currLocalToken][0]]) + " "
                                for token in localTokens[currLocalToken + 1:]:
                                    expanded_macro += " " + token[0]
                                loopFlag = True
                                break
                    
            tokenNum += 1
            
        return retTokens, defines
