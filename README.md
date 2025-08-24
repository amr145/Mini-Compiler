# Mini Compiler

## Overview
This project is a **mini compiler** built using **Python**, featuring lexical analysis, parsing, error handling, symbol table management, and Abstract Syntax Tree (AST) generation.

## Features
- Lexer using regex for tokenization
- Recursive-descent parser (variables, expressions, conditionals, loops, functions)
- Symbol table for scope & declarations
- Error detection (undefined/redeclared symbols, syntax errors)
- AST generator

## Tech Stack
- Python
- Regex
- PLY (Lex-Yacc)
- Custom AST structures

## How to Run
```bash
git clone https://github.com/amr145/Mini-Compiler.git
cd Mini-Compiler
python main.py examples/test.txt
