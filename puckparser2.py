# Name: Benjamin Biehl
import sys
# Shorthands and Definitions
integers = '0123456789'
relations = ['<', '>', '=', '#']
add_operators = ['+', '-', 'OR', '&']
mul_operators = ['*', '/', 'AND', 'DIV', 'MOD']
tokens = []
symbol_table = {}
token = ''
current_position = 0

# Token and Symbol Table Functions
def initializeTokens(start_string):
    global tokens, current_position
    tokens = start_string.split()
    current_position = 0
    getToken()


def getToken():
    global token, current_position
    if current_position < len(tokens):
        token = tokens[current_position]
        current_position += 1
    else:
        token = "$"


def updateSymbolTable(name, value):
    if name not in symbol_table:
        symbol_table[name] = {"type": value}


def printSymbolTable():
    for key, value in symbol_table.items():
        print(f"{key}      {str(value)}")

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
    parseSimpleExpression()
    if isRelation(token):
        getToken()
        parseSimpleExpression()


def parseSimpleExpression():
    parseTerm()
    while isAddOperator(token):
        getToken()
        parseTerm()


def parseTerm():
    parseFactor()
    while isMulOperator(token):
        getToken()
        parseFactor()


def parseFactor():
    if isInteger(token) or isDecimal(token) or isString(token):
        getToken()
    elif token == "(":
        getToken()
        parseExpression()
        if token == ")":
            getToken()
        else:
            raise TypeError("')' expected")
    elif token == "~":
        print("Found '~'")
        getToken()
        parseFactor()
    elif isIdentifier(token):
        getToken()
    else:
        raise TypeError("Identifier or literal expected")


def parseDesignator():
    if isIdentifier(token):
        updateSymbolTable(token, "variable")
        getToken()
        while token == "^" or token == "[":
            parseSelector()
    else:
        raise TypeError("identifier expected")


def parseSelector():
    if token == "^":
        getToken()
        if isIdentifier(token):
            updateSymbolTable(token, "variable")
            getToken()
        else:
            raise TypeError("Identifier expected")
    elif token == "[":
        getToken()
        parseExpression()
        if token == "]":
            getToken()
        else:
            raise TypeError("] expected")
    else:
        raise TypeError("^ or [ expected")


def parseParamSequence():
    if isIdentifier(token):
        updateSymbolTable(token, "variable")
        getToken()
        while token == ",":
            if isIdentifier(token):
                updateSymbolTable(token, "variable")
                getToken()
            else:
                raise TypeError("Identifier expected")
    else:
        raise TypeError("Identifier expected")


def parseFunctionCall():
    if isIdentifier(token):
        getToken()
        if token == "(":
            if token == ")":
                getToken()
            elif isIdentifier(token):
                parseParamSequence()
            else:
                raise TypeError(") or Identifier expected")
        else:
            raise TypeError("( expected")
    else:
        raise TypeError("Identifier expected")


def parseAssignment():
    parseDesignator()
    if token == ":-":
        getToken()
        parseExpression()
        if token == ".":
            getToken()
        else:
            raise TypeError(". expected")
    else:
        raise TypeError(":- expected")


def parsePrintStatement():
    if token == "PRINT":
        getToken()
        if token == "(":
            getToken()
            parseExpression()
            if token == ")":
                getToken()
                if token == ".":
                    getToken()
                else:
                    raise TypeError(". expected")
            else:
                raise TypeError(") expected")
        else:
            raise TypeError("( expected")
    else:
        raise TypeError("PRINT expected")


def parseIfStatement():
    if token == "IF":
        getToken()
        parseExpression()
        if token == "THEN":
            getToken()
            parseStatementSequence()
            while token == "ELIF":
                getToken()
                parseExpression()
                if token == "THEN":
                    getToken()
                    parseStatementSequence()
                else:
                    raise TypeError("THEN expected")
        else:
            raise TypeError("THEN expected")
        if token == "ELSE":
            getToken()
            parseStatementSequence()
        elif token == ".":
            getToken()
        else:
            raise TypeError("FI expected")
    else:
        raise TypeError("IF expected")


def parseLoopStatement():
    if token == "LOOP":
        getToken()
        parseExpression()
        if token == "DO":
            getToken()
            parseStatementSequence()
            while token == "ELIF":
                getToken()
                parseExpression()
                if token == "DO":
                    getToken()
                    parseStatementSequence()
                else:
                    raise TypeError("DO expected")
        else:
            raise TypeError("DO expected")
        if token == "POOL":
            getToken()
        else:
            raise TypeError("POOL expected")
    else:
        raise TypeError("LOOP expected")


def parseStatement():
    if token == "PRINT":
        parsePrintStatement()
    elif token == "IF":
        parseIfStatement()
    elif token == "LOOP":
        parseLoopStatement()
    elif isIdentifier(token):
        if token in symbol_table and symbol_table[token] == "function":
            parseFunctionCall()
        else:
            parseAssignment()
    else:
        return TypeError("Identifier expected")


def parseStatementSequence():
    parseStatement()
    while token != "END.":
        parseStatement()


def parseFunctionDeclaration():
    if token == "DEF":
        getToken()
        if isIdentifier(token):
            updateSymbolTable(token, "function")
            getToken()
            if token == "(":
                getToken()
                if token == ")":
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
        raise TypeError("DEF expected")


def parseFunctionBody():
    if token == ";":
        getToken()
    else:
        parseStatementSequence()
        if token == "RETURN":
            parseReturnStatement()
        elif token == "END.":
            getToken()
        else:
            raise TypeError("END. or RETURN expected")


def parseReturnStatement():
    if token == "RETURN":
        getToken()
        if token == "(":
            getToken()
            if isIdentifier(token):
                getToken()
                if token == ")":
                    getToken()
                    if token == ".":
                        getToken()
                    else:
                        raise TypeError(". expected")
                else:
                    raise TypeError(") expected")
            else:
                raise TypeError("Identifier expected")
        else:
            raise TypeError("( expected")
    else:
        raise TypeError("RETURN expected")


def parseDeclarationSequence():
    parseFunctionDeclaration()
    while token == "DEF":
        parseFunctionDeclaration()

# Main Loop
input_string = " ".join(line.strip() for line in sys.stdin)
initializeTokens(input_string)
print(tokens)

while token != "$":
    try:
        parseDeclarationSequence()
        print("VALID")
        printSymbolTable()

    except TypeError as e:
        print("INVALID!")
        print(e)
        break
