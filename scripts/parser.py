#!/usr/bin/env python3
"""
Lark-based parser that transforms parse trees directly into AST nodes.
Uses Lark's Transformer class for clean tree-to-AST conversion.
"""

from lark import Lark, Transformer, v_args
from ASTLib import *
from lexer import extract_cpp_blocks, clean_block
import re

# Updated grammar that produces parse trees instead of just tokens
PARSER_GRAMMAR = r"""
?start: statement*

?statement: var_statement
          | cpp_block
          | expression

var_statement: type identifier "=" literal  -> var_assign
            | type identifier               -> var_declare  
            | type identifier_list "=" literal -> multi_var_assign
            | type identifier_list          -> multi_var_declare

expression: binary_expr | unary_expr

identifier_list: identifier ("," identifier)+

binary_op: "+" | "-" | "*" | "/" | "%" | "==" | "!=" | "<" | "<=" | ">" | ">=" | "&&" | "||" | "&" | "|" | "^" | "<<" | ">>"
unary_op: "!" | "-" | "+" | "~"
binary_expr: expression binary_op expression
unary_expr: unary_op expression

type: TYPE | ID
identifier: ID
literal: LITERAL

cpp_block: CPP_BLOCK

// Lexer rules
CPP_BLOCK.10: /__CPP_BLOCK_\d+__/

LITERAL: RAW_STRING
       | INTERP_STRING  
       | STRING
       | CHAR
       | DECIMAL
       | BINARY
       | HEX
       | OCT
       | INTEGER
       | BOOLEAN

RAW_STRING: /R"([^"\\]|\\.)*"/
INTERP_STRING: /\$"(?:[^"\\]|\\.|"(?!\s)|\{[^}]*\})*"/
STRING: /"([^"\\]|\\.)*"/
CHAR: /'(?:\\.|[^'\\])'/

BINARY: /0[bB]_*[01][01_]*/
HEX: /0[xX]_*[0-9a-fA-F][0-9a-fA-F_]*/
OCT: /0[oO]_*[0-7][0-7_]*/
DECIMAL: /\d[\d_]*\.\d[\d_]*([eE][+-]?\d[\d_]*)?[A-Za-z0-9_]*/
       | /\d[\d_]*[eE][+-]?\d[\d_]*/
INTEGER: /\d[\d_]*/

BOOLEAN: "true" | "false"

TYPE: "byte" | "short" | "int" | "long" | "ubyte" | "ushort" | "ulong"
    | "float" | "double" | "fixed16_16" | "fixed32_32" | "char" | "string" 
    | "bool" | "void" | "any" | "list" | "collection" | "map" | "set"
    | "tuple" | "auto" | "union" | "lambda"

ID: /[A-Za-z_][A-Za-z0-9_]*/

%import common.WS
%ignore WS
"""

class ASTTransformer(Transformer):
    """Transforms Lark parse tree nodes into AST nodes."""
    
    def __init__(self, cpp_blocks=None):
        super().__init__()
        self.cpp_blocks = cpp_blocks or []
    
    # Leaf nodes
    def identifier(self, args):
        return Identifier(str(args[0]))
    
    def type(self, args):
        return Identifier(str(args[0]))
    
    def literal(self, args):
        val = str(args[0])
        
        # Boolean literals
        if val in ("true", "false"):
            return BoolLiteral(val == "true")
        
        # String literal detection
        if val.startswith('"') and val.endswith('"'):
            return NormalStringLiteral(val[1:-1])  # Remove quotes
        
        if val.startswith('R"') and val.endswith('"'):
            return RawStringLiteral(val[2:-1])  # Remove R" and "
        
        if val.startswith('$"') and val.endswith('"'):
            return InterpolatedStringLiteral(val)
        
        # Default to numeric literal
        return NumericLiteral(val)
    
    def cpp_block(self, args):
        # Extract block index from placeholder
        placeholder = str(args[0])
        match = re.match(r'__CPP_BLOCK_(\d+)__', placeholder)
        if match:
            block_idx = int(match.group(1))
            if 0 <= block_idx < len(self.cpp_blocks):
                return Comment(self.cpp_blocks[block_idx])
        return Comment("// Unknown C++ block")
    
    # Container nodes
    def identifier_list(self, args):
        return list(args)  # Just return the list of identifiers
    
    # Expression nodes
    @v_args(inline=True)
    def binary_expr(self, left, op, right):
        return BinaryExpression(left, str(op), right)

    @v_args(inline=True)
    def unary_expr(self, op, expr):
        return UnaryExpression(str(op), expr)
    
    # Statement nodes
    @v_args(inline=True)
    def var_assign(self, var_type, var_name, literal):
        return VarAssign(var_name, literal, var_type)
    
    @v_args(inline=True) 
    def var_declare(self, var_type, var_name):
        return VarDeclare(var_name, var_type)
    
    @v_args(inline=True)
    def multi_var_assign(self, var_type, var_names, literal):
        return MultiVarAssign(var_names, literal, var_type)
    
    @v_args(inline=True)
    def multi_var_declare(self, var_type, var_names):
        return MultiVarDeclare(var_names, var_type)
    
    # Program structure
    def start(self, args):
        statements = [stmt for stmt in args if stmt is not None]
        body = Body(statements)
        return Program(body)

class Parser:
    """Main parser class using Lark."""
    @staticmethod
    def parse_source(tokens, cpp_blocks) -> Program:
        """Parse a list of tokens into an AST Program node."""
        parser = Lark(PARSER_GRAMMAR, parser='lalr', lexer='standard', propagate_positions=True)
        tree = parser.parse(" ".join(token.value for token in tokens))
        transformer = ASTTransformer(cpp_blocks)
        ast = transformer.transform(tree)
        return ast
# Test function
def test_parser():
    """Test the parser with various examples."""
    
    parser = Parser()
    
    # Test cases
    test_cases = [
        "int x = 10",
        "string name = \"hello\"", 
        "bool flag = true",
        "int x",
        "int x, y = 42",
        "float a, b, c"
    ]
    
    for i, source in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {source} ===")
        try:
            ast = parser.parse_source(source)
            print("AST Generated Successfully!")
            print("C++ Output:")
            print(ast.To_CXX())
            
            # Print AST structure
            if ast.body.children:
                stmt = ast.body.children[0]
                print(f"AST Node: {type(stmt).__name__}")
                if hasattr(stmt, 'var_name'):
                    if isinstance(stmt.var_name, list):
                        names = [n.To_CXX() for n in stmt.var_name]
                        print(f"  var_names: {names}")
                    else:
                        print(f"  var_name: {stmt.var_name.To_CXX()}")
                if hasattr(stmt, 'var_type'):
                    print(f"  var_type: {stmt.var_type.To_CXX()}")
                if hasattr(stmt, 'value'):
                    print(f"  value: {stmt.value.To_CXX() if stmt.value else 'None'}")
        
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_parser()