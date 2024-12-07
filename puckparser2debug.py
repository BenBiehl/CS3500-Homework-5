# Name: Benjamin Biehl
import sys

# Shorthands and Definitions
integers = '0123456789'
relations =  ['<', '>', '=', '#']
add_operators = ['+', '-', 'OR', '&']
mul_operators = ['*', '/', 'AND', 'DIV', 'MOD']
keywords = ["DEF", "RETURN", "DO", "LOOP","POOL", "ELSE", "IF", "THEN", "FI"]
tokens = []
symbol_table = {}
token = ''
current_position = 0

# Token and Symbol Table Functions
def initializeTokens(start_string):
    global tokens, current_position
    print("Initializing tokens...")
    tokens = start_string.split()
    current_position = 0
    getToken()

def getToken():
    global token, current_position
    if current_position < len(tokens):
        token = tokens[current_position]
        current_position += 1
    print(f"getToken() -> token: {token}")

def updateSymbolTable(name, value):
    if name not in symbol_table:
        symbol_table[name] = {"type": value}
        print(f"Updated symbol table: {name} -> {value}")

def printSymbolTable():
    print(f"Symbol Table : size {len(symbol_table)}")
    for key, value in symbol_table.items():
        print(f"{key} {value['type']}")

# Bool Functions
def isInteger(word):
    state = 1
    i = 0
    acc = False
    while i < len(word):
        c = word[i]
        if state == 1:
            if c == '+' or c == '-':
                state = 2
                i += 1
            elif c in integers:
                state = 2
                i += 1
                acc = True
            else:
                return False
        elif state == 2:
            if c in integers:
                state = 2
                i += 1
                acc = True
            else:
                return False
    return acc

def isDecimal(word):
    state = 1
    i = 0
    acc = False
    while i < len(word):
        c = word[i]
        if state == 1:
            if c == '+' or c == '-' or c in integers:
                state = 2
                i += 1
            else:
                return False
        elif state == 2:
            if c in integers:
                state = 2
                i += 1
            elif c == '.':
                state = 3
                i += 1
            else:
               return False
        # State after '.' is detected
        elif state == 3:
            if c in integers:
                state = 3
                i += 1
                acc = True
            else:
                return False
    return acc

def isString(word):
    state = 1
    i = 0
    acc = False

    while i < len(word):
        c = word[i]
        if state == 1:
            if c == '\"':
                state = 2
                i += 1
            else:
                return False
        elif state == 2:
            if c != ' ' and c != '\"':
                state = 3
                i += 1
            else:
                return False
        elif state == 3:
            if c != ' ' and c != '\"':
                state = 3
                i += 1
            elif c == '\"':
                state = 4
                i += 1
                acc = True
            else:
                return False
        # If there's a closing parenthesis, then if there are any more characters afterward it's invalid
        elif state == 4:
            return False
    return acc

def isIdentifier(word):
    #if word in keywords:
        #return False
    state = 1
    i = 0
    acc = False

    while i < len(word):
        c = word[i]
        if state == 1:
            if c.isalpha():
                state = 2
                i += 1
                acc = True
            else:
                return False
        elif state == 2:
            if c.isalpha() or c in integers or c == '_':
                state = 2
                i += 1
            else:
                return False
    return acc

def isRelation(word):
    if word in relations:
        return True
    else:
        return False
    
def isAddOperator(word):
    if word in add_operators:
        return True
    else:
        return False
    
def isMulOperator(word):
    if word in mul_operators:
        return True
    else:
        return False

# Parse Functions
def parseExpression():
    print(f"Parsing expression: {token}")
    parseSimpleExpression()
    if isRelation(token):
        print(f"Found relation: {token}")
        getToken()
        parseSimpleExpression()

def parseSimpleExpression():
    print(f"Parsing simple expression: {token}")
    parseTerm()
    while isAddOperator(token):
        print(f"Found add operator: {token}")
        getToken()
        parseTerm()

def parseTerm():
    print(f"Parsing term: {token}")
    parseFactor()
    while isMulOperator(token):
        print(f"Found mul operator: {token}")
        getToken()
        parseFactor()

def parseFactor():
    print(f"Entering parseFactor()")
    if isInteger(token) or isDecimal(token) or isString(token):
        print(f"Parsed literal: {token}")
        getToken()
    elif token == "(":
        print("Found '('")
        getToken()
        parseExpression()
        if token == ")":
            print("Found ')'")
            getToken()
        else:
            raise TypeError("')' expected")
    elif token == "~":
        print("Found '~'")
        getToken()
        parseFactor()
    elif isIdentifier(token):
        print(f"Parsed identifier: {token}")
        if token in symbol_table:
            entry = symbol_table[token]
            print(f"Token {token} found in symbol_table: {entry}")
            if entry["type"] == "function":
                parseFunctionCall()
            else:
                parseDesignator()
        else:
            parseDesignator()
    else:
        raise TypeError("Identifier or literal expected")

def parseDesignator():
    print("Entering parseDesignator()")
    if isIdentifier(token):
        print(f"Identifier found: {token}")
        updateSymbolTable(token, "variable")
        getToken()
        while token == "^" or token == "[":
            print(f"Parsing selector with token: {token}")
            parseSelector()
    else:
        raise TypeError("identifier expected")
    print("Exiting parseDesignator()")

def parseSelector():
    print("Entering parseSelector()")
    if token == "^":
        print(f"Found ^ with token: {token}")
        getToken()
        if isIdentifier(token):
            print(f"Identifier after ^: {token}")
            updateSymbolTable(token, "variable")
            getToken()
        else:
            raise TypeError("Identifier expected")
    elif token == "[":
        print(f"Found [ with token: {token}")
        getToken()
        parseExpression()
        if token == "]":
            print(f"Found ] with token: {token}")
            getToken()
        else:
            raise TypeError("] expected")
    else:
        raise TypeError("^ or [ expected")
    print("Exiting parseSelector()")

def parseParamSequence():
    print("Entering parseParamSequence()")
    if isIdentifier(token) and token not in keywords:
        print(f"Found parameter identifier: {token}")
        updateSymbolTable(token, "variable")
        getToken()
        while token == ",":
            print(f"Found , with token: {token}")
            getToken()
            if isIdentifier(token):
                print(f"Found parameter identifier after comma: {token}")
                updateSymbolTable(token, "variable")
                getToken()
            else:
                raise TypeError("Identifier expected")
    else:
        raise TypeError("Identifier expected")
    print("Exiting parseParamSequence()")


def parseFunctionCall():
    print("Entering parseFunctionCall()")

    # Ensure the token is a valid identifier for the function
    if isIdentifier(token):
        print(f"Function identifier found: {token}")
        function_name = token
        getToken()  # Move past the function name

        # Expect an opening parenthesis after the function name
        if token == "(":
            print(f"Found ( with token: {token}")
            getToken()  # Consume the '(' token

            # Check if there is a parameter sequence
            if token != ")":
                # If there's something other than ')' after '(', handle parameters
                parseParamSequence()
                # After parsing parameters, check for closing ')'
                if token != ")":
                    raise TypeError(") expected after parameter sequence")

            print(f"Found ) with token: {token}")
            getToken()  # Consume the ')'
        else:
            raise TypeError("( expected after function identifier")
    else:
        raise TypeError("Identifier expected")

    print("Exiting parseFunctionCall()")


def parseAssignment():
    print("Entering parseAssignment()")
    parseDesignator()
    if token == ":-":
        print(f"Found :- with token: {token}")
        getToken()
        parseExpression()
        if token == ".":
            print(f"Found . with token: {token}")
            getToken()
        elif token == "(":
            raise TypeError(f"Variable {token} used as a function")
        else:
            raise TypeError(". expected")
    elif token == "(":
        raise TypeError(f"Undefined function {token}")
    else:
        raise TypeError(":- expected")
    print("Exiting parseAssignment()")

def parsePrintStatement():
    print("Entering parsePrintStatement()")
    if token == "PRINT":
        print(f"Found PRINT with token: {token}")
        getToken()
        if token == "(":
            print(f"Found ( with token: {token}")
            getToken()
            parseExpression()
            if token == ")":
                print(f"Found ) with token: {token}")
                getToken()
                if token == ".":
                    print(f"Found . with token: {token}")
                    getToken()
                else:
                    raise TypeError(". expected")
            else:
                raise TypeError(") expected")
        else:
            raise TypeError("( expected")
    else:
        raise TypeError("PRINT expected")
    print("Exiting parsePrintStatement()")

def parseIfStatement():
    print("Entering parseIfStatement()")
    if token == "IF":
        print(f"Found IF with token: {token}")
        getToken()
        parseExpression()  # Parse the Expression after IF
        if token == "THEN":
            print(f"Found THEN with token: {token}")
            getToken()
            parseStatementSequence()  # Parse the first StatementSequence
            while token == "ELIF":  # Handle zero or more ELIF sections
                print(f"Found ELIF with token: {token}")
                getToken()
                parseExpression()
                if token == "THEN":
                    print(f"Found THEN with token: {token}")
                    getToken()
                    parseStatementSequence()
                else:
                    raise TypeError("THEN expected after ELIF Expression")
            if token == "ELSE":  # Handle the optional ELSE section
                print(f"Found ELSE with token: {token}")
                getToken()
                parseStatementSequence()
            if token == "FI":  # Ensure the IF statement ends with FI
                print(f"Found FI with token: {token}")
                getToken()
            else:
                raise TypeError("FI expected to close IF statement")
        else:
            raise TypeError("THEN expected after IF Expression")
    else:
        raise TypeError("IF expected")
    print("Exiting parseIfStatement()")


def parseLoopStatement():
    print("Entering parseLoopStatement()")
    if token == "LOOP":
        print(f"Found LOOP with token: {token}")
        getToken()
        parseExpression()
        if token == "DO":
            print(f"Found DO with token: {token}")
            getToken()
            parseStatementSequence()
            while token == "ELIF":
                print(f"Found ELIF with token: {token}")
                getToken()
                parseExpression()
                if token == "DO":
                    print(f"Found DO with token: {token}")
                    getToken()
                    parseStatementSequence()
                else:
                    raise TypeError("DO expected")
        else:
            raise TypeError("DO expected")
        if token == "POOL":
            print(f"Found POOL with token: {token}")
            getToken()
        else:
            raise TypeError("POOL expected")
    else:
        raise TypeError("LOOP expected")
    print("Exiting parseLoopStatement()")

def parseStatement():
    print(f"Entering parseStatement()  {token}")
    if token == "PRINT":
        parsePrintStatement()
    elif token == "IF":
        parseIfStatement()
    elif token == "LOOP":
        parseLoopStatement()
    elif isIdentifier(token) and token != "POOL" and token != "FI":
        if token in symbol_table:
            entry = symbol_table[token]
            print(f"Token {token} found in symbol_table: {entry}")
            if entry["type"] == "function":
                parseFunctionCall()
            else:
                parseAssignment()
        else:
            parseAssignment()
    else:
        raise TypeError("Identifier expected")
    print("Exiting parseStatement()")

def parseStatementSequence():
    print("Entering parseStatementSequence()")
    parseStatement()
    while token != "END.":
        if token in keywords and token != "LOOP" and token != "IF" and token != "PRINT":
            break
        parseStatement()
    print("Exiting parseStatementSequence()")

def parseFunctionDeclaration():
    print("Entering parseFunctionDeclaration()")
    if token == "DEF":
        print(f"Found DEF with token: {token}")
        getToken()
        if isIdentifier(token):
            print(f"Function identifier found: {token}")
            updateSymbolTable(token, "function")
            getToken()
            if token == "(":
                print(f"Found ( with token: {token}")
                getToken()
                if token == ")":
                    print(f"Found ) with token: {token}")
                    getToken()
                elif isIdentifier(token):
                    parseParamSequence()
                    getToken()
                else:
                    raise TypeError(") or Identifier expected")
                parseFunctionBody()
            else:
                raise TypeError("( expected")
        else:
            raise TypeError("Identifier expected")
    else:
        raise TypeError(f'Error: Function declaration expected, got "{token}".')
    print("Exiting parseFunctionDeclaration()")

def parseFunctionBody():
    print("Entering parseFunctionBody()")
    if token == ";":
        print(f"Found ; with token: {token}")
    else:
        parseStatementSequence()
        if token == "RETURN":
            parseReturnStatement()
        elif token == "END.":
            print(f"Found END. with token: {token}")
        else:
            raise TypeError("END. or RETURN expected")
    print("Exiting parseFunctionBody()")

def parseReturnStatement():
    print("Entering parseReturnStatement()")
    if token == "RETURN":
        print(f"Found RETURN with token: {token}")
        getToken()
        if token == "(":
            print(f"Found ( with token: {token}")
            getToken()
            if isIdentifier(token):
                print(f"Identifier found: {token}")
                getToken()
                if token == ")":
                    print(f"Found ) with token: {token}")
                    getToken()
                else:
                    raise TypeError(") expected")
            else:
                raise TypeError("Identifier expected")
        else:
            raise TypeError("( expected")
    else:
        raise TypeError("RETURN expected")
    print("Exiting parseReturnStatement()")

def parseDeclarationSequence():
    print("Entering parseDeclarationSequence()")
    parseFunctionDeclaration()
    getToken()
    while token == "DEF":
        parseFunctionDeclaration()
    print("Exiting parseDeclarationSequence()")

# Main Loop
input_string = " ".join(line.strip() for line in sys.stdin)
initializeTokens(input_string)
print(tokens)

try:
    parseDeclarationSequence()
    print("VALID")
    printSymbolTable()
        
except TypeError as e:
    print("INVALID!")
    print(e)
