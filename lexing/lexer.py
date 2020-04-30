import re
import inspect

class lexer:

    def __init__(self, source, origsource):
        
        self.setSource(source, origsource)
        self.resetParseFlags()
        
        self.eof = "##EOF"
        
        self.reserved_words = [
            "else",	"switch", "break", "FILE", "double", "long",
            "case", "return", "char", "float", 
            "short", "unsigned", "for", "signed", "void",
            "continue",	"goto",	"sizeof", "default", "if",	
            "while", "int", "struct", "double", "bool"
        ]

        self.punctuators = [
            ["<<=", ">>="],
            
            ["->", "++", "--" "<<", ">>", "<=", ">=", "==", "!=", 
            "&&", "||", "*=", "/=", "%=", "+=", "-=", "&=", "^=", "|="],
            
            ["[", "]", "(", ")", "{", "}", ".", "&", "*", "+", "-",
            "~", "!", "/", "%", "<", ">", "^", "|", ";", ",", "=", ":", "?"]
        ]

        # in order of priority top to bottom
        self.regexes = {
            "integer_literal_bool" : re.compile("true|false"),
            "identifier" : re.compile("[a-zA-Z_]+[a-zA-Z0-9_]*"),
            "string_literal" : re.compile('\\"(\\\\.|[^"\\\\])*\\"'),
            "char_literal" : re.compile('\\\'(\\\\.|[^"\\\\])?\\\''),
            "float_literal" : re.compile("[+-]?[0-9]+[.][0-9]+"),
            "integer_literal_hex" : re.compile("[0][x][0-9a-fA-F]+"),
            "integer_literal_oct" : re.compile("[0][0-7]+"),
            "integer_literal_dec" : re.compile("[+-]?[0-9]+"),
            "whitespace" : re.compile("\\s+"),
            "blank_or_whitespace_for_preprocessor_rule_only" : re.compile("\\s*"),
            "anything_for_preprocessor_rule_only" : re.compile(".*"),
        }

        self.preprocessor_commands = {
            "#define" : (self.regexes["whitespace"], self.regexes["identifier"], self.regexes["anything_for_preprocessor_rule_only"]),
            "#undef" : (self.regexes["whitespace"], self.regexes["identifier"], self.regexes["blank_or_whitespace_for_preprocessor_rule_only"]),
            "#ifdef" : (self.regexes["whitespace"], self.regexes["identifier"], self.regexes["blank_or_whitespace_for_preprocessor_rule_only"]),
            "#ifndef" : (self.regexes["whitespace"], self.regexes["identifier"], self.regexes["blank_or_whitespace_for_preprocessor_rule_only"]),
            "#endif" : (self.regexes["blank_or_whitespace_for_preprocessor_rule_only"]),
            "#include" : (self.regexes["whitespace"], self.regexes["string_literal"], self.regexes["blank_or_whitespace_for_preprocessor_rule_only"])
        }
        
    def setSource(self, source, origsource):
        self.source = source
        for i in range(0, len(self.source)):
            self.source[i][2] = int(self.source[i][2])
        self.source.append(["##EOF", source[-1][1], source[-1][2] + 1])
        self.resetParseFlags()
        self.origsource = origsource

    def getSource(self):
        return self.source
    
    def getState(self):
        return [
            self.source, 
            self.inMultiLineComment,
            self.inSingleLineComment,
            self.inString,
            self.curString,
            self.inPreprocessorCommand,
            self.token,
            self.tokenTup
        ]
        
    def setState(self, state):
        self.source = state[0]
        self.inMultiLineComment = state[1]
        self.inSingleLineComment = state[2]
        self.inString = state[3]
        self.curString = state[4]
        self.inPreprocessorCommand = state[5]
        self.token = state[6]
        self.tokenTup = state[7]
        
    def resetParseFlags(self):
        self.inMultiLineComment = False
        self.inSingleLineComment = [False, 1]
        self.inString = False
        self.curString = ""
        self.inPreprocessorCommand = [False, "", 0]
        self.token = ""
        self.tokenTup = ["", "", 0]
        
    def collapseWhitespace(self):
        
        noTabSource = [[line[0].replace("\t", "    "), line[1], line[2]] for line in self.source]
        localSource = noTabSource
        
        retTokens = []
        for i in range(0, len(localSource)):
            line = localSource[i][0].rstrip()
            origLine = line
            
            tokens = []
            while line != "":
                if line.strip() == "":
                    tokens.append(" ")
                else:
                    if line[0] != " ":
                        val = line.split(" ", 1)[0]
                        tokens.append(val)
                        line = line.split(val, 1)[1]
                    else:
                        val = line[self.regexes["whitespace"].match(line).span()[0]: self.regexes["whitespace"].match(line).span()[1]]
                        tokens.append(val)
                        line = line.split(val, 1)[1]
                
            while tokens != []:
                if(len(tokens) >= 2):
                    retTokens.append([tokens[0] + tokens[1], localSource[i][1], localSource[i][2], origLine, i])
                    tokens.pop(0)
                    tokens.pop(0)
                else:
                    retTokens.append([tokens[0], localSource[i][1], localSource[i][2], origLine, i])
                    tokens.pop(0)
            
        return retTokens
    
    def lex(self):
        
        retTokens = []
        startTokens = self.collapseWhitespace()
        
        # lex all tokens and store all not whitespace and not end_of_file
        for i in range(0, len(startTokens)):
            self.tokenTup = startTokens[i]
            self.token = self.tokenTup[0]
            #print("Token to start is: '" + token + "'")
            while self.token.strip() != "":
                retToken = self.getToken()
                if (retToken[1] != "whitespace") and (retToken[1] != "end_of_file") and (retToken[1] != ""):
                    #print(retToken[0] + " : " + retToken[1])
                    retTokens.append(retToken)

        # return list of tokens
        return retTokens

    def getToken(self):
        
        retToken = ""
        retTokenType = ""
        
        if self.inMultiLineComment:
            #print("in multiline comment")
            if "*/" in self.token:
                #print("end multiline comment")
                self.curString += self.token.split("*/", 1)[0]
                self.token = self.token.split("*/", 1)[1]
                self.inMultiLineComment = False
                retTokenType = "multi_line_comment"
                retToken = self.curString + "*/"
                self.tokenTup[3] = retToken
                #print(retToken)
                self.curString = ""
            elif self.token == self.eof:
                print("Syntax error " + str(inspect.currentframe().f_lineno) + " in file " + self.tokenTup[1] + " at " + str(self.tokenTup[2] - 1))
                print("Failed to close multi-line comment!")
                quit()
            else:
                self.curString += self.token
                self.token = ""
                
        elif self.inSingleLineComment[0]:
            if (self.tokenTup[2] != self.inSingleLineComment[1]) or (self.token == "\n"):
                self.inSingleLineComment[0] = False
                retTokenType = "single_line_comment"
                retToken = self.curString
                
                #self.tokenTup[2] -= 1
                #self.tokenTup[3] = self.source[self.tokenTup[2] - 1][0].rstrip()
                
                #print("Comment ended at file " + self.tokenTup[1] + " line " + str(self.tokenTup[2]) + ": '" + retToken + "'")
                self.curString = ""
                
                if (self.tokenTup[2] >= 2) and (len(self.origsource) > 2):
                    if retToken not in self.origsource[self.tokenTup[2] - 2][0]:
                        return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2] - 2), self.origsource[self.tokenTup[2] - 3][0].rstrip()]
                    else:
                        return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2] - 1), self.origsource[self.tokenTup[2] - 2][0].rstrip()]
                else:
                    return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2] - 1), self.tokenTup[3].rstrip()]
    
            else:
                self.curString += self.token
                self.token = ""
                
        elif self.inPreprocessorCommand[0]:
            if (self.tokenTup[2] != self.inPreprocessorCommand[2]) or (self.token == "\n") or ("//" in self.token) or ("/*" in self.token):
                    
                if ("//" in self.token) or ("/*" in self.token):
                    valBeforeComment = self.token.split("//", 1)[0].split("/*", 1)[0]
                    self.curString += valBeforeComment
                    if valBeforeComment != "":
                        self.token = self.token.split(valBeforeComment, 1)[1]
                    
                retTokenType = "preprocessor_command"
                retToken = self.curString.strip()

                #print(curString)
                self.curString = ""
                
                regexes_passed = True
                if retToken != self.inPreprocessorCommand[1]:
                    regex_against = retToken.split(self.inPreprocessorCommand[1], 1)[1]
                    #print(regex_against)
                    for regex in self.preprocessor_commands[self.inPreprocessorCommand[1]]:
                        if regex.match(regex_against) is None:
                            regexes_passed = False
                            break
                        else:
                            regex_against = regex_against[regex.match(regex_against).span()[1]:]
                            #print(regex_against)
                    if regex_against != "":
                        regexes_passed = False
                
                self.inPreprocessorCommand = [False, "", self.tokenTup[2] + 1]
                if not regexes_passed:
                    print("Syntax error " + str(inspect.currentframe().f_lineno) + " in file " + self.tokenTup[1] + " at line " + str(self.tokenTup[2] + 1) + ": '" + str(self.tokenTup[3]) + "'")
                    print("Attempted regex against preprocessor command '" + retToken + "'")
                    print("Current token is '" + self.token + "'")
                    quit()
                
                #self.tokenTup[2] -= 1
                #self.tokenTup[3] = self.source[self.tokenTup[2] - 1][0].rstrip()
                if self.tokenTup[2] >= 2:
                    if retToken not in self.source[self.tokenTup[2] - 2][0]:
                        return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2] - 2), self.source[self.tokenTup[2] - 3][0].rstrip()]
                    else:
                        return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2] - 1), self.source[self.tokenTup[2] - 2][0].rstrip()]
                else:
                    return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2] - 1), self.source[self.tokenTup[2] - 2][0].rstrip()]
    
            else:
                self.curString += self.token
                self.token = ""
                
        elif self.token[0:2] == "/*":
            #print("begin multiline comment")
            self.inMultiLineComment = True;
            self.curString = '/*'
            self.token = self.token.split("/*", 1)[1]
                
        # string with no spaces
        elif (not self.inString) and (self.token[0] == '"'):
                self.inString = True
                self.curString = '"'
                #print("Found string start in file " + self.tokenTup[1] + " at line " + str(self.tokenTup[2] + 1))
                #print("\tLine is '" + self.tokenTup[3] + "'")
                self.token = self.token[1:]
                
        elif self.inString:
            #print("\t\tIn string, current token is '" + token + "'")
            if("\\" in self.token):
                self.curString += self.token.split("\\", 1)[0] + "\\" + self.token.split("\\", 1)[1][0]
                self.token = self.token.split("\\", 1)[1][1:]
            else:
                if '"' in self.token:
                    self.curString += self.token.split('"', 1)[0] + '"'
                    self.token = self.token.split('"', 1)[1]
                    
                    self.inString = False
                    if self.regexes["string_literal"].match(self.curString) is not None:
                        retToken = self.curString
                        retTokenType = "string_literal"
                    else:
                        print("Syntax error " + str(inspect.currentframe().f_lineno) + " in file " + self.tokenTup[1] + " at line " + str(self.tokenTup[2] + 1) + ": '" + str(self.tokenTup[3]) + "'")
                        print("Attempted regex against string '" + self.curString + "'")
                        print("Current token is '" + self.token + "'")
                        quit()
                else:
                    self.curString += self.token
                    self.token = ""
            
            if self.inString:
                #print("\t\tCurrent string: '" + self.curString + "'")
                #print("\t\tRemainder of token: '" + self.token + "'")
                pass
            else:
                pass
                #print("\tFinal string: '" + self.curString + "'")
                
        elif self.token[0:2] == "//":
            self.inSingleLineComment = [True, self.tokenTup[2]]
            self.curString = '//'
            if len(self.token) > len("//"):
                self.curString += self.token.split("//", 1)[1]
            self.token = ""
            #print("Comment found at file " + self.tokenTup[1] + " line " + str(self.tokenTup[2]) + ": '" + self.tokenTup[0] + "'")
            
        else:
            
            found = False
            
            if not found:
                for punctuatorSubList in self.punctuators:
                    punctuatorLen = len(punctuatorSubList[0])
                    if self.token[0:punctuatorLen] in punctuatorSubList:
                        #print("%d char punctuator", punctuatorLen)
                        found = True
                        retToken = self.token[0:punctuatorLen]
                        retTokenType = "punctuator"
                        if len(self.token) > punctuatorLen:
                            self.token = self.token[punctuatorLen:]
                        else:
                            self.token = ""
                
            if not found:
                for regex in self.regexes:
                    if "preprocessor_rule_only" not in regex:
                        if ((self.regexes[regex].match(self.token) is not None) and 
                        (self.token[self.regexes[regex].match(self.token).span()[0]: self.regexes[regex].match(self.token).span()[1]] not in self.reserved_words)
                        ):
                            #print(regex[0])
                            val = self.token[self.regexes[regex].match(self.token).span()[0]: self.regexes[regex].match(self.token).span()[1]]
                            retToken = val
                            retTokenType = regex
                            self.token = self.token.split(val, 1)[1]
                            found = True
                            break
                
            if not found:
                for word in self.reserved_words:
                    if self.token.find(word) == 0:
                        #print("reserved word")
                        #reserved_word_found = True
                        retToken = word
                        retTokenType = "reserved_word"
                        self.token = self.token.split(word, 1)[1]
                        found = True
                        break
            
            if not found:
                for command in self.preprocessor_commands:
                    if self.token.strip() == command:
                        #print("preprocessor_command_start")
                        found = True
                        self.inPreprocessorCommand = [True, command, self.tokenTup[2]]
                        self.curString = self.token
                        if self.token != command:
                            self.token = self.token.split(command, 1)[1]
                        else:
                            self.token = ""
                        break
            
            if not found:
                if self.token == self.eof:
                    found = True
                    retToken = self.token
                    retTokenType = "end_of_file"
                    self.token = ""
                    
            if not found:    
                #if not reserved_word_found:
                print("Syntax error " + str(inspect.currentframe().f_lineno) + " in file " + self.tokenTup[1] + " at " + str(self.tokenTup[2] + 1) + ": '" + str(self.tokenTup[3]) + "'")
                print("Current token is '" + self.token + "'")
                quit()
            
        return [retToken, retTokenType, str(self.tokenTup[1]), str(self.tokenTup[2]), str(self.tokenTup[3])]