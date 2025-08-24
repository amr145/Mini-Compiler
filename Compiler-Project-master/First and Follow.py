from compiler import parse_tree


def extract_symbols(grammar):
    """
    Recursively extract terminals and non-terminals from the grammar.
    """
    terminals = set()
    non_terminals = set()

    def traverse(node):
        if isinstance(node, dict):
            if "Type" in node:
                non_terminals.add(node["Type"])
            for key, value in node.items():
                traverse(value)
        elif isinstance(node, list):
            for item in node:
                traverse(item)
        elif isinstance(node, str):  # Terminal symbol
            terminals.add(node)

    traverse(grammar)
    return terminals, non_terminals


def compute_first(grammar):
    """
    Compute FIRST sets for the provided nested grammar structure.
    """
    first = {}

    # Extract symbols
    terminals, non_terminals = extract_symbols(grammar)

    # Initialize FIRST sets for all non-terminals
    for symbol in non_terminals:
        first[symbol] = set()

    def traverse_for_first(node):
        if isinstance(node, dict):
            if "Type" in node:
                current_type = node["Type"]
                for key, value in node.items():
                    if key != "Type":
                        child_first = traverse_for_first(value)
                        if isinstance(child_first, set):
                            first[current_type].update(child_first)
            return set()
        elif isinstance(node, list):
            result = set()
            for item in node:
                result.update(traverse_for_first(item))
            return result
        elif isinstance(node, str):  # Terminal symbol
            return {node}

    # Compute FIRST sets by traversing the grammar
    traverse_for_first(grammar)
    return first


def compute_follow(grammar, first_sets):
    """
    Compute FOLLOW sets for the provided nested grammar structure.
    """
    follow = {}

    # Extract symbols
    _, non_terminals = extract_symbols(grammar)

    # Initialize FOLLOW sets
    for symbol in non_terminals:
        follow[symbol] = set()

    # Assuming "Program" is the start symbol
    follow["Program"].add("$")

    def traverse_for_follow(node, parent_follow):
        if isinstance(node, dict):
            if "Type" in node:
                current_type = node["Type"]
                for key, value in node.items():
                    if key != "Type":
                        traverse_for_follow(value, follow[current_type])
        elif isinstance(node, list):
            for item in node:
                traverse_for_follow(item, parent_follow)

    # Traverse the grammar to compute FOLLOW sets
    traverse_for_follow(grammar, set())
    return follow


# Example JSON-like grammar structure
grammar = parse_tree 

# Compute FIRST and FOLLOW sets
first_sets = compute_first(grammar)
follow_sets = compute_follow(grammar, first_sets)

# Display the results
print("FIRST sets:")
for non_terminal, first_set in first_sets.items():
    print(f"FIRST({non_terminal}) = {first_set}")

print("\nFOLLOW sets:")
for non_terminal, follow_set in follow_sets.items():
    print(f"FOLLOW({non_terminal}) = {follow_set}")
