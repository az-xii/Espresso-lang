#!/usr/bin/env python3
"""
Pattern-based parser for the Espresso language.
Converts tokens from lexer.py into AST nodes from ASTLib.py.
"""

from typing import List, Optional, Tuple, Union, Any, Dict, Callable
from lexer import Token, Lexer, split_tokens
from ASTLib import *
import re

# ===================================
# Parser Class
# ===================================

class Parser:
    def __init__(self, tokens: List[Token], cpp_blocks: List[str]):
        self.tokens = tokens
        self.cpp_blocks = cpp_blocks
        self.lines = split_tokens(tokens)
        self.current_line = 0
        self.current_token = 0
        self.modifiers: List[Modifier] = []
    
    def error(self, message: str) -> SyntaxError:
        """Create a detailed syntax error with context"""
        tok = self.peek()
        if not tok:
            return SyntaxError(f"{message} at EOF")
        
        # Show context: previous 3 tokens, current, next 3 tokens
        context_tokens = []
        for i in range(-3, 4):
            ctx_tok = self.peek(i)
            if ctx_tok:
                marker = " >>> " if i == 0 else " "
                context_tokens.append(f"{marker}{ctx_tok.type}('{ctx_tok.val}')")
        
        context = "\n    ".join(context_tokens)
        return SyntaxError(
            f"{message}\n"
            f"  At line {tok.line}, column {tok.col}\n"
            f"  Context:\n    {context}"
        )
        
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Peek at token with offset"""
        idx = self.current_token + offset
        if 0 <= idx < len(self.tokens):
            return self.tokens[idx]
        return None
    
    def add_modifier(self, modifier: str):
        """Add a modifier to the current list"""
        match modifier:
            case "const":
                self.modifiers.append(IsConstModifier())
            case "constexpr":
                self.modifiers.append(IsConstexprModifier())
            case "consteval":
                self.modifiers.append(IsConstevalModifier())
            case "static":
                self.modifiers.append(IsStaticModifier())
            case "private":
                self.modifiers.append(IsPrivateModifier())
            case "public":
                self.modifiers.append(IsPublicModifier())
            case "protected":
                self.modifiers.append(IsProtectedModifier())
            case "virtual":
                self.modifiers.append(IsVirtualModifier())
            case "override":
                self.modifiers.append(IsOverrideModifier())
            case "abstract":
                self.modifiers.append(IsAbstractModifier())
            case _:
                raise self.error(f"Unknown modifier: {modifier}")

    def advance(self, count: int = 1) -> Optional[Token]:
        """Advance and return current token"""
        if self.current_token < len(self.tokens):
            tok = self.tokens[self.current_token]
            self.current_token += count
            return tok
        return None
    
    def expect(self, value: str) -> Token:
        """Expect specific token value"""
        tok = self.peek()
        if not tok or tok.val != value:
            raise self.error(f"Expected '{value}', got '{tok.val if tok else 'EOF'}'")
        return self.advance()
    
    def expect_type(self, token_type: str) -> Token:
        """Expect specific token type"""
        tok = self.peek()
        if not tok or tok.type != token_type:
            raise self.error(f"Expected token type '{token_type}', got '{tok.type if tok else 'EOF'}'")
        return self.advance()
    
    # ===================================
    # Pattern Matching Helpers
    # ===================================
    
    def match_delimited(self, open_delim: str, close_delim: str, 
                       separator: str = ",") -> List[List[Token]]:
        """Match delimited token groups (e.g., function parameters)"""
        self.expect(open_delim)
        groups = []
        current_group = []
        depth = 1
        
        while depth > 0 and self.peek():
            tok = self.peek()
            
            if tok.val == open_delim:
                depth += 1
                current_group.append(self.advance())
            elif tok.val == close_delim:
                depth -= 1
                if depth == 0:
                    if current_group:
                        groups.append(current_group)
                    self.advance()
                    break
                else:
                    current_group.append(self.advance())
            elif tok.val == separator and depth == 1:
                if current_group:
                    groups.append(current_group)
                    current_group = []
                self.advance()
            else:
                current_group.append(self.advance())
        
        return groups
    
    def parse_type(self) -> Identifier:
        """Parse a type (handles generics like list<int>)"""
        tok = self.peek()
        if tok and tok.type in ("TYPE", "PATH"):
            self.advance()
            return Identifier(tok.val)
        raise self.error(f"Expected type, got '{tok.type if tok else 'EOF'}'")
    
    def parse_identifier(self) -> Identifier:
        """Parse an identifier (PATH tokens)"""
        tok = self.peek()
        if tok and tok.type in ("PATH", "TYPE"):
            self.advance()
            c_pointers, c_referneces = tok.val.count('*'), tok.val.count('&')

            return Identifier(tok.val + ''.join(['*' for _ in range(c_pointers)]) + ''.join(['&' for _ in range(c_referneces)]))
        raise self.error(f"Expected identifier, got '{tok.type if tok else 'EOF'}'")
    

    # ===================================
    # Expression Parsing
    # ===================================
    
    def parse_literal(self) -> Literal:
        """Parse a literal value"""
        tok = self.expect_type("LITERAL")
        val = tok.val
        
        # String literals
        if val.startswith('R"'):
            return RawStringLiteral(val[2:-1])
        elif val.startswith('$"'):
            return InterpolatedStringLiteral(val)
        elif val.startswith('"'):
            return NormalStringLiteral(val[1:-1])
        elif val.startswith("'"):
            return NormalStringLiteral(val[1:-1])
        
        # Boolean
        elif val in ("true", "false"):
            return BoolLiteral(val == "true")
        
        # Numeric
        else:
            return NumericLiteral(val)
    
    def parse_primary_expr(self) -> Value:
        """Parse primary expression (literal, identifier, or parenthesized)"""
        tok = self.peek()
        
        if not tok:
            raise SyntaxError("Unexpected end of tokens")
        
        # Literals
        if tok.type == "LITERAL":
            return self.parse_literal()
        
        # Parenthesized expression
        if tok.val == "(":
            self.advance()
            expr = self.parse_expression()
            self.expect(")")
            return expr
        
        # Collection literals
        if tok.val == "{":
            return self.parse_collection_literal()
        
        # Identifiers or function calls
        if tok.type in ("PATH", "TYPE"):
            ident = self.parse_identifier()
            
            # Check for function call
            next_tok = self.peek()
            if next_tok and next_tok.val == "(":
                return self.parse_function_call(ident)
            
            return ident
        
        raise SyntaxError(f"Unexpected token in expression: {tok}")
    
    def parse_collection_literal(self) -> Literal:
        """Parse {1, 2, 3} or {{"key", val}}"""
        self.expect("{")
        
        items = []
        is_map = False
        
        while self.peek() and self.peek().val != "}":
            # Check if this is a map entry {{key, val}}
            if self.peek().val == "{":
                is_map = True
                self.advance()
                key = self.parse_expression()
                self.expect(",")
                val = self.parse_expression()
                self.expect("}")
                items.append((key, val))
            else:
                items.append(self.parse_expression())
            
            if self.peek() and self.peek().val == ",":
                self.advance()
        
        self.expect("}")
        
        if is_map:
            return MapLiteral(items)
        else:
            return VectorLiteral(items)
    
    def parse_unary_increment(self) -> Value:
        """Parse unary increment/decrement expressions (++, --)"""
        tok = self.peek()
        
        if tok and tok.type == "OP" and tok.val in ("++", "--"):
            op = self.advance().val
            operand = self.parse_unary_expr()
            return UnaryIncrementExpression(op, operand, is_prefix=True)
        elif tok and tok.type == "PATH":
            # Check for postfix increment/decrement
            saved_pos = self.current_token
            operand = self.parse_primary_expr()
            next_tok = self.peek()
            if next_tok and next_tok.type == "OP" and next_tok.val in ("++", "--"):
                op = self.advance().val
                return UnaryIncrementExpression(op, operand, is_prefix=False)
            else:
                # Restore position if no postfix operator
                self.current_token = saved_pos
        return self.parse_primary_expr()

    def parse_unary_expr(self) -> Value:
        """Parse unary expression (!x, -x, etc.)"""
        tok = self.peek()
        
        if tok and tok.type == "OP" and tok.val in UnaryOperators:
            op = self.advance().val
            operand = self.parse_unary_expr()
            return UnaryExpression(op, operand)
        elif tok and tok.type == "OP" and tok.val in ("++", "--"):
            return self.parse_unary_increment()
        
        return self.parse_primary_expr()
    
    def parse_binary_expr(self, min_prec: int = 0) -> Value:
        """Parse binary expression with precedence climbing"""
        left = self.parse_unary_expr()
        
        while True:
            tok = self.peek()
            if not tok or tok.type != "OP":
                break
            
            op = tok.val
            prec = self.get_precedence(op)
            
            if prec < min_prec:
                break
            
            self.advance()
            right = self.parse_binary_expr(prec + 1)
            
            if op in ConditionOperators:
                # For now, treat as binary (could wrap in Comparison node)
                left = BinaryExpression(left, op, right)
            elif op in BinaryOperators:
                left = BinaryExpression(left, op, right)
            else:
                raise SyntaxError(f"Unknown operator: {op}")
        
        return left
    
    def parse_expression(self) -> Value:
        """Parse any expression"""
        # Check for ternary
        expr = self.parse_binary_expr()
        
        # Check for ternary operator
        if self.peek() and self.peek().val == "?":
            self.advance()
            true_expr = self.parse_expression()
            self.expect(":")
            false_expr = self.parse_expression()
            return TernaryExpr(expr, true_expr, false_expr)
        
        return expr
    
    def get_precedence(self, op: str) -> int:
        """Get operator precedence"""
        precedence = {
            "||": 1,
            "&&": 2,
            "|": 3,
            "^": 4,
            "&": 5,
            "==": 6, "!=": 6,
            "<": 7, "<=": 7, ">": 7, ">=": 7,
            "<<": 8, ">>": 8,
            "+": 9, "-": 9,
            "*": 10, "/": 10, "%": 10,
        }
        return precedence.get(op, 0)
    
    # ===================================
    # Statement Parsing
    # ===================================
    
    def parse_function_call(self, target: Identifier = None) -> FunctionCall:
        """Parse function call"""
        if target is None:
            target = self.parse_identifier()
        
        # Parse generic parameters if present
        generic_params = []
        # Note: generics are already part of the TYPE token
        
        # Parse parameters
        param_groups = self.match_delimited("(", ")")
        params = []
        
        for group in param_groups:
            # Save state and parse parameter
            saved_pos = self.current_token
            
            # Check for named parameter (name=value)
            has_name = False
            for i, tok in enumerate(group):
                if tok.val == "=":
                    has_name = True
                    break
            
            if has_name:
                # Named parameter
                name = Identifier(group[0].val)
                # Skip to after '='
                for tok in group:
                    if tok.val == "=":
                        break
                    self.advance()
                self.advance()  # Skip '='
                value = self.parse_expression()
                params.append(FuncCallParam(value, name))
            else:
                # Positional parameter
                # Temporarily set tokens to this group
                old_tokens = self.tokens
                self.tokens = group
                self.current_token = 0
                value = self.parse_expression()
                self.tokens = old_tokens
                self.current_token = saved_pos
                params.append(FuncCallParam(value))
        
        return FunctionCall(target, params, generic_params)
    
    def parse_var_declare(self, mods: List[Modifier] = []) -> VarDeclareAssign:
        """Parse variable declaration: type name [= value]"""
        modifiers = mods.copy()
        self.modifiers = []  # Clear current modifiers after use
        var_type = self.parse_type()
        var_name = self.parse_identifier()
        
        # Check for assignment
        if self.peek() and self.peek().val == "=":
            self.advance()
            value = self.parse_expression()
            return VarDeclareAssign(var_name=var_name, value=value, var_type=var_type, modifiers=modifiers)
        
        return VarDeclareAssign(var_name=var_name, var_type=var_type, modifiers=modifiers)
    
    def parse_return(self) -> Return:
        """Parse return statement"""
        self.expect("return")
        
        # Check for void return
        if self.peek() and self.peek().val == ";":
            self.advance()
            return Return(None)
        
        value = self.parse_expression()
        if self.peek() and self.peek().val == ";":
            self.advance()
        
        return Return(value)
    
    def parse_if_statement(self) -> IfExpr:
        """Parse if/elif/else statement"""
        self.expect("if")
        self.expect("(")
        condition = self.parse_expression()
        self.expect(")")
        
        body = self.parse_block()
        
        elifs = []
        else_body = None
        
        # Parse elif clauses
        while self.peek() and self.peek().val == "elif":
            self.advance()
            self.expect("(")
            elif_cond = self.parse_expression()
            self.expect(")")
            elif_body = self.parse_block()
            elifs.append((elif_cond, elif_body))
        
        # Parse else clause
        if self.peek() and self.peek().val == "else":
            self.advance()
            else_body = self.parse_block()
        
        return IfExpr(condition, body, elifs, else_body)
    
    def parse_while_loop(self) -> WhileLoop:
        """Parse while loop"""
        self.expect("while")
        self.expect("(")
        condition = self.parse_expression()
        self.expect(")")
        body = self.parse_block()
        return WhileLoop(condition, body)
    
    def parse_for_loop(self) -> Union[ForInLoop, CStyleForLoop]:
        """Parse for loop (both for-in and C-style)"""
        self.expect("for")
        self.expect("(")
        
        # Check if it's a for-in loop by looking ahead
        saved_pos = self.current_token
        is_for_in = False
        
        # Scan ahead to see if we find 'in'
        depth = 1
        while self.peek():
            tok = self.peek()
            if tok.val == "(":
                depth += 1
            elif tok.val == ")":
                depth -= 1
                if depth == 0:
                    break
            elif tok.val == "in" and depth == 1:
                is_for_in = True
                break
            self.advance()
        
        # Restore position
        self.current_token = saved_pos
        
        if is_for_in:
            # For-in loop: for (var in iterable)
            var_name = self.parse_identifier()
            self.expect("in")
            iterable = self.parse_expression()
            self.expect(")")
            body = self.parse_block()
            return ForInLoop(var_name, iterable, body)
        else:
            # C-style loop: for (init; cond; update)
            init = self.parse_statement() 
            self.expect(";")
            cond = self.parse_expression()
            self.expect(";")
            update = self.parse_expression()
            self.expect(")")
            body = self.parse_block()
            return CStyleForLoop(init, cond, update, body)
    
    def parse_block(self) -> Body:
        """Parse a block of statements {...}"""
        self.expect("{")
        statements = []
        
        while self.peek() and self.peek().val != "}":
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect("}")
        return Body(statements)
    
    def parse_function_decl(self, mods: List[Modifier] = []) -> FunctionDecl:
        """Parse function declaration"""
        self.expect("func")
        modifiers = mods.copy()
        self.modifiers = []  # Clear current modifiers after use
        # Parse name (may include generics like "linearSearch<T>" or just "linearSearch")
        name_tok = self.peek()
        if not name_tok or name_tok.type not in ("TYPE", "PATH"):
            raise self.error(f"Expected function name")
        
        self.advance()
        full_name = name_tok.val
        
        # Extract generic parameters from name if present
        generic_params = []
        if "<" in full_name:
            base_name = full_name[:full_name.index("<")]
            generic_str = full_name[full_name.index("<")+1:full_name.rindex(">")]
            for g in generic_str.split(","):
                g = g.strip()
                generic_params.append(GenericParam(Identifier(g)))
            name = Identifier(base_name)
        else:
            name = Identifier(full_name)
        
        # Parse parameters
        param_groups = self.match_delimited("(", ")")
        params = []
        
        for group in param_groups:
            if not group:
                continue
                
            # Parse parameter: [const] type [&] name [= default]
            # Save current state
            saved_tokens = self.tokens
            saved_pos = self.current_token
            
            # Switch to parameter group tokens
            self.tokens = group
            self.current_token = 0
            
            try:
                # Skip 'const' if present
                if self.peek() and self.peek().val == "const":
                    self.advance()
                \
                param_type = self.parse_type()
                
                # Skip '&' if present
                if self.peek() and self.peek().val == "&":
                    self.advance()
                
                param_name = self.parse_identifier()
                
                # Check for default value
                default = None
                if self.peek() and self.peek().val == "=":
                    self.advance()
                    default = self.parse_expression()
                
                params.append(FuncDeclParam(param_name, param_type, default))
            finally:
                # Restore state
                self.tokens = saved_tokens
                self.current_token = saved_pos
        
        # Parse return type if present
        return_type = Identifier("void")
        if self.peek() and self.peek().val == "->":
            self.advance()
            return_type = self.parse_type()
        
        # Parse body
        body = self.parse_block()
        
        return FunctionDecl(name, params, return_type, generic_params, body, modifiers)
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        tok = self.peek()
        
        if not tok:
            return None
        
        # Skip semicolons
        if tok.val == ";":
            self.advance()
            return None
        
        # Keywords
        if tok.type == "KEYW":
            if tok.val == "func":
                return self.parse_function_decl(self.modifiers)
            elif tok.val == "return":
                return self.parse_return()
            elif tok.val == "if":
                return self.parse_if_statement()
            elif tok.val == "while":
                return self.parse_while_loop()
            elif tok.val == "for":
                return self.parse_for_loop()
            elif tok.val == "break":
                self.advance()
                return Break()
            elif tok.val == "continue":
                self.advance()
                return Continue()
            elif tok.val in ("const", "static", "private", "public"):
                # Modifier followed by declaration
                self.add_modifier(tok.val)
                self.advance()
                return self.parse_statement()
        
        # Type declaration
        if tok.type == "TYPE":
            return self.parse_var_declare(self.modifiers)
        
        # CPP Block
        if tok.type == "CPP_BLOCK":
            idx = int(tok.val)
            self.advance()
            return CPPBlock(self.cpp_blocks[idx])
        
        # Expression statement
        expr = self.parse_expression()
        if self.peek() and self.peek().val == ";":
            self.advance()
        return expr
    
    def parse(self) -> Program:
        """Parse the entire program"""
        statements = []
        
        while self.peek():
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        return Program(Body(statements))


# ===================================
# Main Entry Point
# ===================================

def main():
    sample = r"""
static public func linearSearch<T>(const list<T>& nums, const T& target) -> int {
    for (int i = 0; i < nums.size(); ++i) {
        if (nums[i] == target) { return i; }
    }
    return -1;
}
"""
    
    try:
        tokens, cpp_blocks = Lexer.lex_source(sample)
        for t in tokens:
            if t.type == "TYPE":
                t.val = t.val  = ConvertType(t.val)
        Lexer.print_tokens(tokens, cpp_blocks)

        parser = Parser(tokens, cpp_blocks)
        ast = parser.parse()
        
        print("=== Generated C++ Code ===")
        print(ast.To_CXX())
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()