import re

token_rules = [
    ('NUMBER', r'\d+'),
    ('STRING', r'\".*?\"'),
    ('VARKEY', r'\bbe\b'),
    ('IF', r'\bcheck\b'),
    ('ELSEIF', r'\balsocheck\b'),
    ('ELSE', r'\bother\b'),
    ('FUNCDEC', r'\bmake\b'),
    ('FUNCCALL', r'\bdeliver\b'),
    ('LOOP', r'\brepeat\b'),
    ('PRINT', r'\bshow\b'),
    ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('OP', r'\+|-|\*|/'),
    ("COMP_OP", r"(==|!=|<=|>=|<|>)"),
    ('LBRACE', r'\{'),
    ('RBRACE', r'\}'),
    ('LPAREN', r'\('),
    ('RPAREN', r'\)'),
    ('SEMICOLON', r';'),
    ('COMMA', r','),
    ('COMMENT', r'#.*'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
]

symbol_table = [{}]

def lexer(code):
    tokens_list = []
    cursor = 0
    line = 1

    while cursor < len(code):
        match = None
        for token_type, pattern in token_rules:
            reg = re.compile(pattern)
            match = reg.match(code, cursor)
            if match:
                if token_type == "NEWLINE":
                    line += 1
                if token_type != "COMMENT" and token_type != "SKIP" and token_type != "NEWLINE":
                    tokens_list.append((token_type, match.group(0), line))
                cursor = match.end()
                break
        if not match:
            raise ValueError(f"Unexpected Token At position {cursor}: {code[cursor]}")
    return tokens_list
                   
def count_unique_type(tokens):
    unique_type = set(token[0] for token in tokens)
    return len(unique_type), unique_type

def define_symbol(name, data, declaration_line):
    current_scope = symbol_table[-1]
    if name in current_scope:
        raise SyntaxError(f"Redefinition of '{name}' in the same scope.")
    current_scope[name] = {**data, "Declaration Line": declaration_line, "Usage Lines": []}

def resolve_symbol(name, usage_line):
    for scope in reversed(symbol_table):
        if name in scope:
            scope[name]["Usage Lines"].append(usage_line)
            return scope[name]
    raise SyntaxError(f"Undefined symbol '{name}' at line {usage_line}.")

def print_symbol_table():
    print("\nSymbol Table:")
    for i, scope in enumerate(symbol_table):
        for name, info in scope.items():
            print(f"  [{name}] -> {info}")

def parser(tokens_list):
    current_token = 0

    def program():
        nonlocal current_token

        ast = []
        while current_token < len(tokens_list):
            ast.append(statement())
        return {"Type": "Program", "Body": ast}
    
    def statement():
        nonlocal current_token
        print(f"Parsing statement at token {current_token}: {tokens_list[current_token]}")
        if current_token >= len(tokens_list):
            raise SyntaxError("Unexpected end of input.")
        
        token_type = tokens_list[current_token][0]
        if token_type == "IDENTIFIER" and peek() == "VARKEY":
            return variable_declaration()
        elif token_type == "IF":
            return if_statement()
        elif token_type == "FUNCDEC":
            return function_declaration()
        elif token_type == "FUNCCALL":
            return function_call()
        elif token_type == "LOOP":
            return while_loop()
        elif token_type == "PRINT":
            return print_statement()
        else:
            raise SyntaxError(f"Unexpected statement at token {tokens_list[current_token]}")
        

# Variable_Declaration -> Identifier "be" "(" Expression ")" ";"
    def variable_declaration():
        nonlocal current_token

        identifier = match("IDENTIFIER")
        line_of_declaration = tokens_list[current_token - 1][2]
        match("VARKEY")
        match("LPAREN")
        value = expression()
        match("RPAREN")
        match("SEMICOLON")
        define_symbol(identifier, {"Type": "Variable", "Value": value}, line_of_declaration)
        return {"Type": "VariableDeclaration", "Identifier": identifier, "Value": value}

#Expression           -> NumberExpression | StringExpression
    def expression():
        nonlocal current_token
        
        if tokens_list[current_token][0] == "IDENTIFIER":
            name = tokens_list[current_token][1]
            line_of_usage = tokens_list[current_token][2]
            resolve_symbol(name, line_of_usage)
            current_token += 1
            return {"Type": "Identifier", "Name": name}

        elif tokens_list[current_token][0] == "NUMBER":
            return number_expression()
        
        elif tokens_list[current_token][0] == "STRING":
            return string_expression()
        
        else:
            raise SyntaxError(f"Unexpected Token In Expression: {tokens_list[current_token]}")

#NumberExpression     -> Factor (Operator Factor)*
    def number_expression():
        nonlocal current_token

        if tokens_list[current_token][0] == "NUMBER":
            left = {"Type": "Number", "Value": match("NUMBER")}
        
        elif tokens_list[current_token][0] == "IDENTIFIER":
            left = {"Type": "Identifier", "Value": match("IDENTIFIER")}
        
        else:
            raise SyntaxError(f"Unexpected token in number expression: {tokens_list[current_token]}")
        
        while current_token < len(tokens_list) and tokens_list[current_token][0] == "OP":
            operator = match("OP")
            
            if tokens_list[current_token][0] == "NUMBER":
                right = {"Type": "Number", "Value": match("NUMBER")}
            
            elif tokens_list[current_token][0] == "IDENTIFIER":
                right = {"Type": "Identifier", "Value": match("IDENTIFIER")}
            
            else:
                raise SyntaxError(f"Unexpected token in number expression: {tokens_list[current_token]}")
        
            left = {"Type": "Number Expression", "Left": left, "Operator": operator, "Right": right}
        
        return left

#StringExpression     -> '"' Content '"'
    def string_expression():
        content = match("STRING")
        return {"Type": "String Expression", "Value": content}

#If_Statement         -> "check" "(" Condition ")" "{" (Statement ";")* "}" Elif_Statement Else_Statement
    def if_statement():
        nonlocal current_token

        match("IF")
        match("LPAREN")
        cond = condition()
        match("RPAREN")
        match("LBRACE")
        body = []
        while not tokens_list[current_token][0] == "RBRACE":
            body.append(statement())
            if peek() == "SEMICOLON":
                match("SEMICOLON")
        match("RBRACE")
        another_check = elif_statement()
        other = else_statement()
        return {"Type": "If Statement", "Condition": cond, "Body": body, "Elif Statement": another_check, "Else Statement": other}

#Condition            -> Expression Comp_op Expression
    def condition():
        nonlocal current_token

        left = expression()
        comp_op = match("COMP_OP")
        right = expression()
        return {"Type": "Condition", "Left": left, "Comparing Operator": comp_op, "Right": right}
        
#Elif_Statement       -> "alsocheck" "(" Condition ")" "{" (Statement ";")* "}" | ε
    def elif_statement():
        nonlocal current_token
        
        if tokens_list[current_token][0] == "ELSEIF":
            match("ELSEIF")
            match("LPAREN")
            con = condition()
            match("RPAREN")
            match("LBRACE")
            body = []
            while not tokens_list[current_token][0] == "RBRACE":
                body.append(statement())
                if peek() == "SEMICOLON":
                    match("SEMICOLON")
            match("RBRACE")
            return {"Type": "Elif Statement", "Condition": con, "Body": body}
        return None

#Else_Statement       -> "other" "{" (Statement ";")* "}" | ε
    def else_statement():
        nonlocal current_token
        
        if tokens_list[current_token][0] == "ELSE":
            match("ELSE")
            match("LBRACE")
            body = []
            while not tokens_list[current_token][0] == "RBRACE":
                body.append(statement())
                if peek() == "SEMICOLON":
                    match("SEMICOLON")
            match("RBRACE")
            return {"Type": "If Statement", "Body": body}
        return None

#Function_Declaration -> "make" Identifier "{" (Statement ";")* "}"
#                      | "make" Identifier "(" Parameter ")"{" (Statement ";")* "}"
    def function_declaration():
        nonlocal current_token
        
        match("FUNCDEC")
        identifier = match("IDENTIFIER")
        declaration_line = tokens_list[current_token - 1][2]

        if tokens_list[current_token][0] == "LBRACE":
            match("LBRACE")
            body = []
            while not tokens_list[current_token][0] == "RBRACE":
                body.append(statement())
                if peek() == "SEMICOLON":
                    match("SEMICOLON")
            match("RBRACE")
            define_symbol(identifier, {"Type": "Function", "Body": body}, declaration_line)
            return {"Type": "Function Declaration","Identifier": identifier, "Body": body}
        
        elif tokens_list[current_token][0] == "LPAREN":
            match("LPAREN")
            param = parameter()
            match("RPAREN")
            match("LBRACE")
            body = []
            while not tokens_list[current_token][0] == "RBRACE":
                body.append(statement())
                if peek() == "SEMICOLON":
                    match("SEMICOLON")
            match("RBRACE")
            define_symbol(identifier, {"Type": "Function", "Parameters": param, "Body": body}, declaration_line)
            return {"Type": "Function Declaration","Identifier": identifier, "Parameters": param, "Body": body}
        
        else:
            raise SyntaxError(f"Unexpected token in function declaration: {tokens_list[current_token]}")
    

#Parameter            -> Factor | Factor ("," Factor)*
    def parameter():
        nonlocal current_token
        
        parameters = []
        if tokens_list[current_token][0] == "RPAREN":
            return parameters
        
        parameters.append(match("IDENTIFIER"))
        while tokens_list[current_token][0] == "COMMA":
            match("COMMA")
            parameters.append(match("IDENTIFIER"))
        return parameters

#Function_Call        -> "deliver" Identifier ";" 
#                      | "deliver" Identifier "(" Argument ")" ";"
    def function_call():
        nonlocal current_token
        
        match("FUNCCALL")
        identifier = match("IDENTIFIER")
        usage_line = tokens_list[current_token - 1][2]
        resolve_symbol(identifier, usage_line)

        if tokens_list[current_token][0] == "LPAREN":
            match("LPAREN")
            arguments = argument()
            match("RPAREN")
            match("SEMICOLON")
            return {"Type": "Function Call","Identifier": identifier, "Arguments": arguments}
        else:
            match("SEMICOLON")
            return {"Type": "Function Call","Identifier": identifier}

#Argument             -> Factor | Factor ("," Factor)*
    def argument():
        nonlocal current_token
        
        arguments = []
        if tokens_list[current_token][0] == "RPAREN":
            return arguments
        
        arguments.append(expression())
        while tokens_list[current_token][0] == "COMMA":
            match("COMMA")
            arguments.append(expression())
        return arguments
    
#While_Loop           -> "repeat" "(" Condition ")" "{" (Statement ";")+ "}"
    def while_loop():
        nonlocal current_token
        
        match("LOOP")
        match("LPAREN")
        cond = condition()
        match("RPAREN")
        match("LBRACE")
        body = []
        while not tokens_list[current_token][0] == "RBRACE":
            body.append(statement())
            if peek() == "SEMICOLON":
                match("SEMICOLON")
        match("RBRACE")
        return {"Type": "While Loop", "Condition": cond, "Body": body}

#Print_Statement      -> "show" "(" Expression ")" ";"
#                      | "show" "(" Expression ("," Expression)* ")" ";"
    def print_statement():
        nonlocal current_token
        
        match("PRINT")
        match("LPAREN")
        expressions = []
        expressions.append(expression())
        while peek() == "COMMA":
            match("COMMA")
            expressions.append(expression())
        match("RPAREN")
        match("SEMICOLON")
        return {"Type": "Print Statement", "Expressions": expressions}
    

    def match(expected):
        nonlocal current_token
        print(f"Attempting to match {expected} at token {current_token}: {tokens_list[current_token]}")
        if current_token < len(tokens_list) and tokens_list[current_token][0] == expected:
            Value = tokens_list[current_token][1]
            current_token += 1
            return Value
        raise SyntaxError(
        f"Expected {expected}, but found {tokens_list[current_token][0]} "
        f"at position {current_token}: {tokens_list[current_token]}"
    )

    def peek():
        if current_token+1 < len(tokens_list):
            return tokens_list[current_token+1][0]
        return None


    return program()



def compile():
    try:
        # Open source code
        global parse_tree
        with open("source code.txt", "r") as file:
            code = file.read()
        # Lexing the code
        tokens = lexer(code)
        print("Tokens:")
        for token in tokens:
            print(token)

        # Count unique token types
        num_unique, uniques = count_unique_type(tokens)
        print(f"\nNumber of unique token types: {num_unique}")
        print(f"Unique token types: {uniques}\n")
        print("-"*160)
        print("\n")

        # Parsing
        parse_tree = parser(tokens)
        print("\nParse Tree:\n")
        print(parse_tree)
        print("\n")
        print("-"*160)
        print_symbol_table()
        print("\n")
        print("-"*160)

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except ValueError as e:
        print(f"Lexing Error: {e}")
    except Exception as e:
        print(f"Unexpected Error: {e}")


compile()

