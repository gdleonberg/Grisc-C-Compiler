import os

def generateFromBnf(outFilename, inFilename, debugPrintsInParser):
    
    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    with open((dir_path + "\\" + inFilename).replace("\\", "/"), "r") as enbfFile:
        with open((dir_path + "\\" + outFilename).replace("\\", "/"), "w") as rulesFile:
            
            rulesFile.write(
"""class parser:
    
    def __init__(self, tokens):
        
        self.tokens = tokens
        self.currTokenNum = 0
        
    def empty(self):
        return (self.currTokenNum == len(self.tokens))
        
    def getCurrTokenNum(self):
        return self.currTokenNum
        
    def setCurrTokenNum(self, num):
        self.currTokenNum = num
    
    def prevToken(self):
        if self.currTokenNum > 0:
            return self.tokens[self.currTokenNum - 1]
        else:
            return [None, None, None, None, None]
            
    def currToken(self):
        if self.currTokenNum < len(self.tokens):
            return self.tokens[self.currTokenNum]
        else:
            return [None, None, None, None, None]
        
    def getToken(self):
        if self.currTokenNum < len(self.tokens):
            retVal = self.tokens[self.currTokenNum]
            self.currTokenNum += 1
            return retVal
        else:
            return [None, None, None, None, None]
        
    def putToken(self, token):
        self.currTokenNum -= 1
        
    def parse(self):
         """)
            
            # collect all production rules from grammar file
            prod_rules = []
            token_rules = []
            lines = [line for line in enbfFile]
            i = 0
            firstParse = ""
            while i != len(lines):
                if lines[i].strip() == '"""':
                    i += 1
                    while lines[i].strip() != '"""':
                        i += 1
                    i += 1
                elif (lines[i].strip() != "") and (lines[i].strip()[0] != "%"):
                    prod_rule = [lines[i].strip()]
                    rule_expansions = []
                    i += 1
                    while[lines[i].strip() != ";"]:
                        if (lines[i].strip()[0] == ":") or (lines[i].strip()[0] == "|"):
                            rule_expansions.append(lines[i].strip()[1:].strip().split())
                        elif lines[i].strip() == ";":
                            i += 1
                            break
                        else:
                            print("Error in generating rules from bnf at line: " + str(i))
                            quit()
                        i += 1
                    prod_rule.append(rule_expansions)
                    prod_rules.append(prod_rule)
                    
                elif (lines[i].strip() != "") and (lines[i].strip().find("%token") == 0):
                    tokens = lines[i].strip().split("%token", 1)[1].strip().split()
                    for token in tokens:
                        token_rules.append(token)
                    i += 1
                elif (lines[i].strip() != "") and (lines[i].strip().find("%start") == 0):
                    firstParse = "parse_" + lines[i].strip().split("%start", 1)[1].strip()
                    i += 1
                else:
                    i += 1
             
            # write entry point parse
            if firstParse == "":
                print("Unspecified first production rule!")
                quit()
            rulesFile.write("return self." + firstParse + "(0)\n\n")
            
            # use production rules to write recursive-descent functions in rules file
            for prod_rule in prod_rules: 
            
                rulesFile.write("    def parse_" + prod_rule[0] + "(self, nestLevel):\n\n")
                if debugPrintsInParser:
                    rulesFile.write("        print((nestLevel * \"--\") + \"parse_" + prod_rule[0] + " at token \" + str(self.currToken()))\n")
                rulesFile.write("        retFlag = False\n\n")
                for rule in prod_rule[1]:
                    rulesFile.write("        # trying rule: " + " ".join(rule) + "\n")
                    if debugPrintsInParser:
                        rulesFile.write("        if not retFlag:\n")
                        rulesFile.write("            print(((nestLevel + 1) * \"--\") + \"Trying rule: " + " ".join(rule) + "\")\n\n")
                    rulesFile.write("        oldTokenNum = self.getCurrTokenNum()\n\n")
                    for expectedTokenNum in range(0, len(rule)):
                        expectedToken = rule[expectedTokenNum]
                        
                        if expectedTokenNum == 0:
                            rulesFile.write("        if not retFlag:\n")
                        else:
                            rulesFile.write("        if retFlag:\n")
                            
                        if expectedToken == "epsilon":
                            rulesFile.write("            retFlag = True\n\n")
                        elif expectedToken.isupper() and ("'" not in expectedToken):
                            if expectedToken in token_rules:
                                rulesFile.write("            token = self.getToken()\n")
                                rulesFile.write("            if token[1] != \"" + expectedToken + "\":\n")
                                rulesFile.write("                self.putToken(token)\n")
                                rulesFile.write("                retFlag = False\n")
                                rulesFile.write("            else:\n")
                                if debugPrintsInParser:
                                    rulesFile.write("                print(((nestLevel + 2) * \"--\") + \"Matched expected type '" + expectedToken + "' with token\" + str(self.prevToken()))\n")
                                rulesFile.write("                retFlag = True\n\n")
                            else:
                                print("Undefined token type " + expectedToken + " used in production rule " + str(prod_rule))
                                quit()
                        elif "'" not in expectedToken:
                            rulesFile.write("            backupTokenNum = self.getCurrTokenNum()\n")
                            if debugPrintsInParser:
                                rulesFile.write("            print(((nestLevel + 2) * \"--\") + \"Calling parse_" + expectedToken + "\")\n")
                            rulesFile.write("            if not self.parse_" + expectedToken + "(nestLevel + 3):\n")
                            rulesFile.write("                self.setCurrTokenNum(backupTokenNum)\n")
                            #if debugPrintsInParser:
                            #    rulesFile.write("                print(((nestLevel + 2) * \"--\") + \"Failed. Re-winding and trying next production rule\")\n")
                            rulesFile.write("                retFlag = False\n")
                            rulesFile.write("            else:\n")
                            if debugPrintsInParser:
                                    rulesFile.write("                print(((nestLevel + 2) * \"--\") + \"Matched grammar rule '" + expectedToken + "' with token\" + str(self.prevToken()))\n")
                            rulesFile.write("                retFlag = True\n\n")
                        else:
                            rulesFile.write("            token = self.getToken()\n")
                            rulesFile.write("            if token[0] != " + expectedToken + ":\n")
                            rulesFile.write("                self.putToken(token)\n")
                            rulesFile.write("                retFlag = False\n")
                            rulesFile.write("            else:\n")
                            if debugPrintsInParser:
                                    rulesFile.write("                print(((nestLevel + 2) * \"--\") + \"Matched expected value " + expectedToken + " with token\" + str(self.prevToken()))\n")
                            rulesFile.write("                retFlag = True\n\n")
                            
                    rulesFile.write("        if not retFlag:\n")
                    rulesFile.write("            self.setCurrTokenNum(oldTokenNum)\n")
                    if debugPrintsInParser:
                        rulesFile.write("            print(((nestLevel + 2) * \"--\") + \"Failed. Re-winding and trying next production rule\")\n")
                    rulesFile.write("        else:\n")
                    rulesFile.write("            return retFlag\n")
                    rulesFile.write("\n")