class handParser:
    
    def __init__(self, tokens):
        
        self.tokens = tokens
        self.currTokenNum = 0
        
    def empty(self):
        return (self.currTokenNum == len(self.tokens))
        
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
        return self.parse_program()
    
    def parse_program(self):
        #print("parse_program")
        if not self.parse_type():
            #print("Error at parse_program " + str(self.currToken())) 
            return False
        token = self.getToken()
        if not (token[0] == "main"):
            #print("Error at parse_program " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[0] == "("):
            #print("Error at parse_program " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[0] == ")"):
            #print("Error at parse_program " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[0] == "{"):
            #print("Error at parse_program " + str(self.currToken()))
            self.putToken(token) 
            return False
        if not self.parse_statement_group():
            #print("Error at parse_program " + str(self.currToken())) 
            return False
        if not self.parse_return_statement():
            #print("Error at parse_program " + str(self.currToken())) 
            return False
        token = self.getToken()
        if not (token[0] == "}"):
            #print("Error at parse_program " + str(self.currToken())) 
            self.putToken(token)
            return False
        return True
    
    def parse_type(self):
        #print("parse_type")
        token = self.getToken()
        if not ((token[1] == "INT") or (token[1] == "CHAR")):
            #print("Error at parse_type " + str(self.currToken())) 
            self.putToken(token)
            return False
        return True
    
    def parse_statement_group(self):
        #print("parse_statement_group")
        if not self.parse_statement():
            #print("Error at parse_statement_group " + str(self.currToken())) 
            return False
        if not self.parse_statement_group_prime():
            #print("Error at parse_statement_group " + str(self.currToken())) 
            return False
        return True
    
    def parse_statement_group_prime(self):
        #print("parse_statement_group_prime")
        #print(self.currToken())
        if not self.parse_statement():
            #print("statement_group_prime is using empty production")
            #print(self.currToken())
            return True
        if not self.parse_statement_group_prime():
            #print("Error at parse_statement_group_prime " + str(self.currToken()))
            return False
        return True
        
    def parse_statement(self):
        #print("parse_statement")
        if not self.parse_assignment():
            #print("Error at parse_statement " + str(self.currToken())) 
            return False
        token = self.getToken()
        if not (token[0] == ";"):
            #print("Error at parse_statement " + str(self.currToken())) 
            self.putToken(token)
            return False
        return True
    
    def parse_return_statement(self):
        #print("parse_return_statement")
        token = self.getToken()
        if not (token[1] == "RETURN"):
            #print("Error at parse_return_statement " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[1] == "IDENTIFIER"):
            #print("Error at parse_return_statement " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[0] == ";"):
            #print("Error at parse_return_statement " + str(self.currToken())) 
            self.putToken(token)
            return False
        return True
        
    def parse_assignment(self):
        #print("parse_assignment")
        if not self.parse_type():
            #print("Error at parse_assignment " + str(self.currToken())) 
            return False
        token = self.getToken()
        if not (token[1] == "IDENTIFIER"):
            #print("Error at parse_assignment " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[0] == "="):
            #print("Error at parse_assignment " + str(self.currToken())) 
            self.putToken(token)
            return False
        token = self.getToken()
        if not (token[1] == "CONSTANT"):
            #print("Error at parse_assignment " + str(self.currToken())) 
            self.putToken(token)
            return False
        return True
    
    def parse_type(self):
        #print("parse_type")
        token = self.getToken()
        if not ((token[1] == "INT") or (token[1] == "CHAR")):
            #print("Error at parse_type " + str(self.currToken())) 
            self.putToken(token)
            return False
        return True