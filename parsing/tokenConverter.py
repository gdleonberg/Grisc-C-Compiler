class tokenConverter:
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.conversions = [
            ["IDENTIFIER", ["__WILDCARD__", ["identifier"]]],
            ["CONSTANT", ["__WILDCARD__", ["char_literal", "float_literal", "integer_literal_hex", "integer_literal_oct", "integer_literal_dec", "integer_literal_bool"]]],
            ["STRING_LITERAL", ["__WILDCARD__", ["string_literal"]]], 
            ["SIZEOF", ["sizeof", ["reserved_word"]]],
            ["PTR_OP", ["->", ["punctuator"]]], 
            ["INC_OP", ["++", ["punctuator"]]], 
            ["DEC_OP", ["--", ["punctuator"]]], 
            ["LEFT_OP", ["<<", ["punctuator"]]], 
            ["RIGHT_OP", [">>", ["punctuator"]]], 
            ["LE_OP", ["<=", ["punctuator"]]], 
            ["GE_OP", [">=", ["punctuator"]]], 
            ["EQ_OP", ["==", ["punctuator"]]], 
            ["NE_OP", ["!=", ["punctuator"]]],
            ["AND_OP", ["&&", ["punctuator"]]], 
            ["OR_OP", ["||", ["punctuator"]]], 
            ["MUL_ASSIGN", ["*=", ["punctuator"]]],
            ["DIV_ASSIGN", ["/=", ["punctuator"]]], 
            ["MOD_ASSIGN", ["%=", ["punctuator"]]], 
            ["ADD_ASSIGN", ["+=", ["punctuator"]]],
            ["SUB_ASSIGN", ["-=", ["punctuator"]]], 
            ["LEFT_ASSIGN", ["<<=", ["punctuator"]]], 
            ["RIGHT_ASSIGN", [">>=", ["punctuator"]]], 
            ["AND_ASSIGN", ["&=", ["punctuator"]]],
            ["XOR_ASSIGN", ["^=", ["punctuator"]]], 
            ["OR_ASSIGN", ["|=", ["punctuator"]]],
            ["CHAR", ["char", ["reserved_word"]]],
            ["SHORT", ["short", ["reserved_word"]]],
            ["INT", ["int", ["reserved_word"]]],
            ["LONG", ["long", ["reserved_word"]]], 
            ["SIGNED", ["signed", ["reserved_word"]]], 
            ["UNSIGNED", ["unsigned", ["reserved_word"]]], 
            ["FLOAT", ["float", ["reserved_word"]]], 
            ["DOUBLE", ["double", ["reserved_word"]]],
            ["VOID", ["void", ["reserved_word"]]],
            ["BOOL", ["bool", ["reserved_word"]]],
            ["STRUCT", ["struct", ["reserved_word"]]],
            ["CASE", ["case", ["reserved_word"]]], 
            ["DEFAULT", ["default", ["reserved_word"]]], 
            ["IF", ["if", ["reserved_word"]]], 
            ["ELSE", ["else", ["reserved_word"]]], 
            ["SWITCH", ["switch", ["reserved_word"]]], 
            ["WHILE", ["while", ["reserved_word"]]],
            ["FOR", ["for", ["reserved_word"]]], 
            ["GOTO", ["goto", ["reserved_word"]]], 
            ["CONTINUE", ["continue", ["reserved_word"]]], 
            ["BREAK", ["break", ["reserved_word"]]], 
            ["RETURN", ["return", ["reserved_word"]]]
        ]
        
        self.escapeSequences = {
            "'\\a'":	str(int("07", 16)),
            "'\\b'":	str(int("08", 16)),
            "'\\e'":	str(int("1B", 16)),
            "'\\f'":	str(int("0C", 16)),
            "'\\n'":	str(int("0A", 16)),
            "'\\r'":	str(int("0D", 16)),
            "'\\t'":	str(int("09", 16)),
            "'\\v'":	str(int("0B", 16)),
            "'\\\\'":   str(int("5C", 16)),
            "'\\\''":	str(int("27", 16)),
            "'\\\"'":	str(int("22", 16)),
            "'\\?'":    str(int("3F", 16))
        }
        
    def applyConversion(self, token, conversion):
        retToken = None
        
        if (conversion[1][0] == "__WILDCARD__") or (token[0] == conversion[1][0]):
            matches = False
            for allowed_type in conversion[1][1]:
                if (conversion[1][1] == "__WILDCARD__") or (token[1] == allowed_type):
                    matches = True
            if matches:
                
                # change all integer constants to base10
                if conversion[0] == "CONSTANT":
                    if "_hex" in token[1]:
                        token[0] = str(int(str(token[0]), 16))
                    elif "_oct" in token[1]:
                        token[0] = str(int(str(token[0])[2:], 8))
                    elif "_bool" in token[1]:
                        if token[0] == "true":
                            token[0] = "1"
                        else:
                            token[0] = "0"
                    elif "char_literal" in token[1]:
                        if token[0] in self.escapeSequences:
                            token[0] = self.escapeSequences[token[0]]
                        else:
                            token[0] = str(ord(token[0].split("'")[1]))
                        
                retToken = token
                retToken[1] = conversion[0]
                
        return retToken
    
    def convert(self):
        retTokens = []
        for token in self.tokens:
            retToken = None
            for conversion in self.conversions:
                retToken = self.applyConversion(token, conversion)
                if retToken != None:
                    retTokens.append(retToken)
                    break
            if retToken == None:
                retTokens.append(token)
        retTokens.append(["", "EOF", token[2], token[3], token[4]])
        return retTokens