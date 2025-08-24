# Grammar definition
grammar = {
    "<program>": ["<statement>*"],
    "<statement>": [
        "<variable_declaration>",
        "<if_statement>",
        "<function_declaration>",
        "<function_call>",
        "<while_loop>",
        "<comment>",
        "<print_statement>",
        "epilson",
    ],
    "<variable_declaration>": ["<identifier> be ( <expression> ) ;"],
    "<identifier>": ["[a-zA-Z][a-zA-Z0-9_]*"],  
    "<expression>": ["<number_expression>", "<string_expression>"],
    "<number_expression>": ["<factor> (<operator> <factor>)*"],
    "<factor>": ["<number>", "<identifier>"],
    "<number>": ["[0-9]*"],
    "<operator>": ["+", "-", "*", "/"],
    "<string_expression>": ['"<content>"'],
    "<content>": ["[a-zA-Z0-9\\-\\+/*=:\\(\\)]*"],
    "<if_statement>": [
        "check ( <condition> ) { (<statement> ;)* } <elif_statement> <else_statement>"
    ],
    "<condition>": ["<expression> <comp_op> <expression>"],
    "<comp_op>": ["<", ">", "==", "!=", "<=", ">="],
    "<elif_statement>": ["alsocheck ( <condition> ) { (<statement> ;)* }", "epilson"],
    "<else_statement>": ["other { (<statement> ;)* }", "epilson"],
    "<function_declaration>": [
        "make <identifier> { (<statement> ;)* }",
        "make <identifier> ( <parameter> ) { (<statement> ;)* }",
    ],
    "<parameter>": ["<factor>", "<factor> , <factor>*"],
    "<function_call>": [
        "deliver <identifier> ;",
        "deliver <identifier> ( <argument> ) ;",
    ],
    "<argument>": ["<factor>", "<factor> , <factor>*"],
    "<while_loop>": ["repeat ( <condition> ) { (<statement> ;)+ }"],
    "<comment>": ["# <content>"],
    "<print_statement>": [
        "show ( <expression> ) ;",
        "show ( <expression> , <expression>* ) ;",
    ],
}

# Function to compute FIRST sets
def compute_first(grammar):
    first = {}

    # Initialize FIRST sets for all non-terminals
    for non_terminal in grammar:
        first[non_terminal] = set()

    def compute_first_for_symbol(symbol):
        if symbol in first and first[symbol]:  # FIRST set already computed
            return first[symbol]
        if symbol not in grammar:  # Terminal or epsilon
            return {symbol}

        result = set()
        for production in grammar[symbol]:
            production_symbols = production.split()
            for prod_symbol in production_symbols:
                first_set = compute_first_for_symbol(prod_symbol)
                result.update(first_set - {"epilson"})
                if "epilson" not in first_set:
                    break
            else:
                result.add("epilson")
        first[symbol] = result
        return result

    # Compute FIRST sets for all non-terminals
    for non_terminal in grammar:
        compute_first_for_symbol(non_terminal)

    return first

# Function to compute FOLLOW sets
def compute_follow(grammar, first_sets):
    follow = {non_terminal: set() for non_terminal in grammar}

    # Start symbol's FOLLOW set should contain the end-of-input marker
    start_symbol = "<program>"
    follow[start_symbol].add("$")  # Assuming $ is the end-of-input marker

    def compute_follow_for_symbol(symbol):
        if symbol not in grammar:
            return  # Terminal, do nothing

        for non_terminal, productions in grammar.items():
            for production in productions:
                symbols = production.split()
                for i, symbol_in_production in enumerate(symbols):
                    if symbol_in_production == symbol:
                        if i + 1 < len(symbols):
                            next_symbol = symbols[i + 1]
                            if next_symbol in grammar:
                                follow[symbol].update(first_sets[next_symbol] - {"epilson"})
                                if "epilson" in first_sets[next_symbol]:
                                    follow[symbol].update(follow[non_terminal])
                            else:
                                follow[symbol].add(next_symbol)
                        else:
                            follow[symbol].update(follow[non_terminal])

    # Compute FOLLOW sets until no changes occur
    changed = True
    while changed:
        changed = False
        for non_terminal in grammar:
            old_follow = follow[non_terminal].copy()
            compute_follow_for_symbol(non_terminal)
            if follow[non_terminal] != old_follow:
                changed = True

    return follow

# Compute FIRST sets
first_sets = compute_first(grammar)

# Compute FOLLOW sets
follow_sets = compute_follow(grammar, first_sets)

# Display FIRST and FOLLOW sets
print("FIRST sets:")
for non_terminal, first_set in first_sets.items():
    print(f"FIRST({non_terminal}) = {first_set}")

print("\nFOLLOW sets:")
for non_terminal, follow_set in follow_sets.items():
    print(f"FOLLOW({non_terminal}) = {follow_set}")
