#! venv/bin/python3
from __future__ import annotations
import stat
import sys
from typing import List, Tuple, Dict, Optional, Union, Any
from dataclasses import dataclass

from lexer import Lexer, Token
from ASTLib import *

class ParserError(Exception):
    """Custom exception for parser errors"""
    pass

class Parser:
    def __init__(self, tokens: List[Token], cpp_blocks: List[str]):
        self.tokens = tokens
        self.cpp_blocks = cpp_blocks
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
    
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def peek(self, n=1):
        pos = self.pos + n
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def expect(self, token_type: str, value: Optional[str] = None):
        if not self.current_token:
            raise ParserError(f"Expected {token_type}, but reached end of input")
        
        if self.current_token.type != token_type:
            raise ParserError(f"Expected {token_type}, got {self.current_token.type} at line {self.current_token.line}")
        
        if value is not None and self.current_token.val != value:
            raise ParserError(f"Expected {token_type} with value '{value}', got '{self.current_token.val}' at line {self.current_token.line}")
        
        result = self.current_token
        self.advance()
        return result
    
    def match(self, token_type: str, value: Optional[str] = None):
        if not self.current_token:
            return False
        
        if self.current_token.type != token_type:
            return False
        
        if value is not None and self.current_token.val != value:
            return False
        
        return True
    
    def consume(self, token_type: str, value: Optional[str] = None):
        if self.match(token_type, value):
            token = self.current_token
            self.advance()
            return token
        return None
    

    def parse(self) -> Program:
        """Parse the entire program"""
        statements = []
        while self.current_token:
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParserError as e:
                print(f"Parse error: {e}", file=sys.stderr)
                # Try to recover by skipping to next statement
                while self.current_token and not self.match("DELIM", ";"):
                    self.advance()
                if self.match("DELIM", ";"):
                    self.advance()
        
        body = Body(statements)
        program = Program(body)
        return program
    
    def parse_statement(self) -> Optional[ASTNode]:
        """Parse a single statement"""
        if not self.current_token:
            return None
        
        # Check for annotations
        if self.match("DECOR"):
            return self.parse_annotation()
        
        # Check for modifiers
        if self.current_token.type in ["PRIVATE_MODIFIER", "PUBLIC_MODIFIER", "PROTECTED_MODIFIER", 
                                     "CONST_MODIFIER", "CONSTEXPR_MODIFIER", "CONSTEVAL_MODIFIER",
                                     "STATIC_MODIFIER", "OVERRIDE_MODIFIER", "VIRTUAL_MODIFIER"]:
            return self.parse_declaration_with_modifiers()
        
        # Check for variable declarations
        if self.match("TYPE") or (self.match("ID") and self.peek() and self.peek().type in ["ID", "DELIM"]):
            # Look ahead to see if this is a variable declaration
            if self.is_likely_variable_declaration():
                return self.parse_variable_declaration()
        
        # Check for function definitions
        if self.match("ID") and self.peek() and self.peek().type == "DELIM" and self.peek().val == "(":
            # Could be a function call or function definition
            if self.is_likely_function_definition():
                return self.parse_function_definition()
            else:
                return self.parse_expression_statement()
        
        # Check for control flow
        if self.match("KEYW"):
            kw = self.current_token.val
            if kw == "if":
                return self.parse_if_statement()
            elif kw == "while":
                return self.parse_while_loop()
            elif kw == "for":
                return self.parse_for_loop()
            elif kw == "return":
                return self.parse_return_statement()
            elif kw == "break":
                self.advance()
                self.consume("DELIM", ";")
                return Break()
            elif kw == "continue":
                self.advance()
                self.consume("DELIM", ";")
                return Continue()
            elif kw == "try":
                return self.parse_try_catch()
            elif kw == "throw":
                return self.parse_throw_statement()
            elif kw == "class":
                return self.parse_class_definition()
        
        # Check for expressions
        if self.is_start_of_expression():
            return self.parse_expression_statement()
        
        # Skip unknown tokens
        self.advance()
        return None
    
    def is_likely_variable_declaration(self) -> bool:
        """Check if the current position is likely a variable declaration"""
        # Save current position
        save_pos = self.pos
        save_token = self.current_token
        
        try:
            # Try to parse a type
            if self.match("TYPE"):
                self.advance()
            elif self.match("ID"):
                self.advance()
            else:
                return False
            
            # Next should be an identifier
            if not self.match("ID"):
                return False
            self.advance()
            
            # Next could be =, ;, or comma for multiple declarations
            if (self.match("OP", "=") or self.match("DELIM", ";") or 
                self.match("DELIM", ",")):
                return True
                
            return False
        finally:
            # Restore position
            self.pos = save_pos
            self.current_token = save_token
    
    def is_likely_function_definition(self) -> bool:
        """Check if the current position is likely a function definition"""
        # Save current position
        save_pos = self.pos
        save_token = self.current_token
        
        try:
            # Skip identifier
            if not self.match("ID"):
                return False
            self.advance()
            
            # Check for parameters
            if not self.match("DELIM", "("):
                return False
            self.advance()
            
            # Parse parameters until we find a closing parenthesis
            while self.current_token and not self.match("DELIM", ")"):
                self.advance()
            
            if not self.match("DELIM", ")"):
                return False
            self.advance()
            
            # Check for return type
            if self.match("DELIM", ":"):
                self.advance()
                if self.match("TYPE") or self.match("ID"):
                    self.advance()
            
            # Next should be a body or arrow function
            if self.match("DELIM", "{"):
                return True
            elif self.match("OP", "=>"):
                return True
                
            return False
        finally:
            # Restore position
            self.pos = save_pos
            self.current_token = save_token
    
    def is_start_of_expression(self) -> bool:
        """Check if current token is the start of an expression"""
        if not self.current_token:
            return False
        
        return (self.current_token.type in ["ID", "LITERAL", "OP", "DELIM"] and
                self.current_token.val not in [";", "}", "{", ")", "]"])
    
    def parse_annotation(self) -> Optional[Annotation]:
        """Parse an annotation (@define, @assert, etc.)"""
        if not self.match("DECOR"):
            return None
        
        decor = self.current_token.val
        self.advance()
        
        if decor == "@define":
            return self.parse_define_annotation()
        elif decor == "@assert":
            return self.parse_assert_annotation()
        elif decor == "@panic":
            return self.parse_panic_annotation()
        elif decor == "@namespace":
            return self.parse_namespace_annotation()
        elif decor == "@cpp":
            return self.parse_cpp_block()
        # Add other annotations here
        
        # Skip unknown annotations
        while self.current_token and not self.match("DELIM", ";"):
            self.advance()
        return None
    
    def parse_define_annotation(self) -> AnnotationDefine:
        """Parse @define annotation"""
        name = self.expect("ID")
        value = self.parse_literal()
        self.consume("DELIM", ";")
        return AnnotationDefine(name.val, value)
    
    def parse_assert_annotation(self) -> AnnotationAssert:
        """Parse @assert annotation"""
        condition = self.parse_expression()
        self.consume("DELIM", ";")
        return AnnotationAssert(condition)
    
    def parse_panic_annotation(self) -> AnnotationPanic:
        """Parse @panic annotation"""
        value = self.parse_literal()
        self.consume("DELIM", ";")
        return AnnotationPanic(value)
    
    def parse_namespace_annotation(self) -> AnnotationNamespace:
        """Parse @namespace annotation"""
        ns_name = self.expect("ID")
        self.consume("DELIM", "{")
        
        statements = []
        while self.current_token and not self.match("DELIM", "}"):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.consume("DELIM", "}")
        return AnnotationNamespace(ns_name.val, statements)
    
    def parse_cpp_block(self) -> ASTNode:
        """Parse @cpp block"""
        # @cpp blocks are handled by the lexer, so we should just have a CPP_BLOCK token
        if self.match("CPP_BLOCK"):
            block_idx = int(self.current_token.val)
            self.advance()
            # Create a special node for C++ blocks
            return ASTNode(NodeType.CPP_BLOCK, value=self.cpp_blocks[block_idx])
        
        # Handle inline @cpp { ... } blocks (if not preprocessed)
        self.consume("DELIM", "{")
        
        # Find matching }
        depth = 1
        content = []
        while self.current_token and depth > 0:
            if self.match("DELIM", "{"):
                depth += 1
            elif self.match("DELIM", "}"):
                depth -= 1
                if depth == 0:
                    break
            
            content.append(self.current_token.val)
            self.advance()
        
        self.consume("DELIM", "}")
        return ASTNode(NodeType.CPP_BLOCK, value=" ".join(content))
    
    def parse_declaration_with_modifiers(self) -> Optional[ASTNode]:
        """Parse a declaration that might have modifiers"""
        modifiers = []
        
        # Collect all modifiers
        while self.current_token and self.current_token.type.endswith("_MODIFIER"):
            mod_type = self.current_token.type
            if mod_type == "PRIVATE_MODIFIER":
                modifiers.append(IsPrivateModifier())
            elif mod_type == "PUBLIC_MODIFIER":
                modifiers.append(IsPublicModifier())
            elif mod_type == "PROTECTED_MODIFIER":
                modifiers.append(IsProtectedModifier())
            elif mod_type == "CONST_MODIFIER":
                modifiers.append(IsConstModifier())
            elif mod_type == "CONSTEXPR_MODIFIER":
                modifiers.append(IsConstexprModifier())
            elif mod_type == "CONSTEVAL_MODIFIER":
                modifiers.append(IsConstevalModifier())
            elif mod_type == "STATIC_MODIFIER":
                modifiers.append(IsStaticModifier())
            elif mod_type == "OVERRIDE_MODIFIER":
                modifiers.append(IsOverrideModifier())
            elif mod_type == "VIRTUAL_MODIFIER":
                modifiers.append(IsVirtualModifier())
            
            self.advance()
        
        # Now parse the actual declaration
        if self.match("TYPE") or self.match("ID"):
            # Variable or function declaration
            if self.is_likely_function_definition():
                func = self.parse_function_definition()
                func.modifiers = modifiers
                return func
            else:
                var = self.parse_variable_declaration()
                var.modifiers = modifiers
                return var
        
        # Unknown declaration with modifiers
        return None
    
    def parse_variable_declaration(self) -> Union[VarDeclare, VarAssign, MultiVarDeclare, MultiVarAssign]:
        """Parse a variable declaration"""
        # Parse type
        if self.match("TYPE"):
            var_type = Identifier(self.current_token.val)
            self.advance()
        elif self.match("ID"):
            var_type = Identifier(self.current_token.val)
            self.advance()
        else:
            raise ParserError(f"Expected type, got {self.current_token.type}")
        
        # Parse variable names
        var_names = []
        while True:
            if self.match("ID"):
                var_names.append(Identifier(self.current_token.val))
                self.advance()
            else:
                raise ParserError(f"Expected identifier, got {self.current_token.type}")
            
            # Check for comma or assignment or end
            if self.match("DELIM", ","):
                self.advance()
                continue
            elif self.match("OP", "=") or self.match("DELIM", ";"):
                break
            else:
                raise ParserError(f"Unexpected token {self.current_token.type} in variable declaration")
        
        # Check for assignment
        if self.match("OP", "="):
            self.advance()
            value = self.parse_expression()
            self.consume("DELIM", ";")
            
            if len(var_names) == 1:
                return VarAssign(var_names[0], value, var_type)
            else:
                return MultiVarAssign(var_names, value, var_type)
        else:
            self.consume("DELIM", ";")
            
            if len(var_names) == 1:
                return VarDeclare(var_names[0], var_type)
            else:
                return MultiVarDeclare(var_names, var_type)
    
    def parse_function_definition(self) -> FunctionDecl:
        """Parse a function definition"""
        # Parse function name
        name = Identifier(self.expect("ID").val)
        
        # Parse generic parameters
        generic_params = []
        if self.match("DELIM", "<"):
            generic_params = self.parse_generic_parameters()
        
        # Parse parameters
        self.expect("DELIM", "(")
        params = self.parse_parameter_list()
        self.expect("DELIM", ")")
        
        # Parse return type
        return_type = None
        if self.match("DELIM", ":"):
            self.advance()
            if self.match("TYPE") or self.match("ID"):
                return_type = Identifier(self.current_token.val)
                self.advance()
        
        # Parse function body
        body = self.parse_block()
        
        return FunctionDecl(name, params, return_type, generic_params, body)
    
    def parse_generic_parameters(self) -> List[GenericParam]:
        """Parse generic/template parameters"""
        self.expect("DELIM", "<")
        
        params = []
        while self.current_token and not self.match("DELIM", ">"):
            if self.match("ID"):
                name = Identifier(self.current_token.val)
                self.advance()
                
                # Check for type constraint
                param_type = None
                if self.match("DELIM", ":"):
                    self.advance()
                    if self.match("TYPE") or self.match("ID"):
                        param_type = Identifier(self.current_token.val)
                        self.advance()
                
                # Check for default value
                default = None
                if self.match("OP", "="):
                    self.advance()
                    default = self.parse_expression()
                
                params.append(GenericParam(name, param_type, default))
                
                # Check for comma
                if self.match("DELIM", ","):
                    self.advance()
        
        self.expect("DELIM", ">")
        return params
    
    def parse_parameter_list(self) -> List[FuncDeclParam]:
        """Parse a parameter list"""
        params = []
        
        while self.current_token and not self.match("DELIM", ")"):
            # Parse parameter type
            if self.match("TYPE") or self.match("ID"):
                param_type = Identifier(self.current_token.val)
                self.advance()
            else:
                raise ParserError(f"Expected parameter type, got {self.current_token.type}")
            
            # Parse parameter name
            if self.match("ID"):
                name = Identifier(self.current_token.val)
                self.advance()
            else:
                raise ParserError(f"Expected parameter name, got {self.current_token.type}")
            
            # Parse default value (optional)
            default = None
            if self.match("OP", "="):
                self.advance()
                default = self.parse_expression()
            
            params.append(FuncDeclParam(name, param_type, default))
            
            # Check for comma
            if self.match("DELIM", ","):
                self.advance()
        
        return params
    
    def parse_block(self) -> Body:
        """Parse a block of statements enclosed in {}"""
        self.expect("DELIM", "{")
        
        statements = []
        while self.current_token and not self.match("DELIM", "}"):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect("DELIM", "}")
        return Body(statements)
    
    def parse_if_statement(self) -> IfExpr:
        """Parse an if statement"""
        self.expect("KEYW", "if")
        
        # Parse condition
        condition = self.parse_expression()
        
        # Parse if body
        if_body = self.parse_block()
        
        # Parse elif clauses
        elifs = []
        while self.match("KEYW", "elif"):
            self.advance()
            elif_condition = self.parse_expression()
            elif_body = self.parse_block()
            elifs.append((elif_condition, elif_body))
        
        # Parse else clause
        else_body = None
        if self.match("KEYW", "else"):
            self.advance()
            else_body = self.parse_block()
        
        return IfExpr(condition, if_body, elifs, else_body)
    
    def parse_while_loop(self) -> WhileLoop:
        """Parse a while loop"""
        self.expect("KEYW", "while")
        
        condition = self.parse_expression()
        body = self.parse_block()
        
        return WhileLoop(condition, body)
    
    def parse_for_loop(self) -> Union[ForInLoop, CStyleForLoop]:
        """Parse a for loop"""
        self.expect("KEYW", "for")
        
        # Check if it's a for-in loop or C-style for loop
        if self.match("ID") and self.peek() and self.peek().val == "in":
            # for-in loop
            var_name = Identifier(self.current_token.val)
            self.advance()
            self.expect("KEYW", "in")
            iterable = self.parse_expression()
            body = self.parse_block()
            return ForInLoop(var_name, iterable, body)
        else:
            # C-style for loop
            init = self.parse_expression()
            self.consume("DELIM", ";")
            condition = self.parse_expression()
            self.consume("DELIM", ";")
            update = self.parse_expression()
            body = self.parse_block()
            return CStyleForLoop(init, condition, update, body)
    
    def parse_return_statement(self) -> Return:
        """Parse a return statement"""
        self.expect("KEYW", "return")
        
        if self.match("DELIM", ";"):
            self.advance()
            return Return(None)
        
        value = self.parse_expression()
        self.consume("DELIM", ";")
        return Return(value)
    
    def parse_try_catch(self) -> TryCatch:
        """Parse a try-catch block"""
        self.expect("KEYW", "try")
        
        try_body = self.parse_block()
        
        catch_blocks = []
        while self.match("KEYW", "catch"):
            self.advance()
            
            # Parse exception type
            self.expect("DELIM", "(")
            if self.match("TYPE") or self.match("ID"):
                exception_type = Identifier(self.current_token.val)
                self.advance()
            else:
                raise ParserError(f"Expected exception type, got {self.current_token.type}")
            
            # Parse exception variable name
            if self.match("ID"):
                exception_var = Identifier(self.current_token.val)
                self.advance()
            else:
                raise ParserError(f"Expected exception variable name, got {self.current_token.type}")
            
            self.expect("DELIM", ")")
            
            # Parse catch body
            catch_body = self.parse_block()
            catch_blocks.append((exception_type, catch_body))
        
        # Parse finally clause (optional)
        finally_body = None
        if self.match("KEYW", "finally"):
            self.advance()
            finally_body = self.parse_block()
        
        return TryCatch(try_body, catch_blocks, finally_body)
    
    def parse_throw_statement(self) -> Throw:
        """Parse a throw statement"""
        self.expect("KEYW", "throw")
        
        exception = self.parse_expression()
        self.consume("DELIM", ";")
        return Throw(exception)
    
    def parse_class_definition(self) -> ClassNode:
        """Parse a class definition"""
        self.expect("KEYW", "class")
        
        # Parse class name
        name = Identifier(self.expect("ID").val)
        
        # Parse generic parameters
        generic_params = []
        if self.match("DELIM", "<"):
            generic_params = self.parse_generic_parameters()
        
        # Parse inheritance
        parents = []
        if self.match("DELIM", ":"):
            self.advance()
            while True:
                if self.match("TYPE") or self.match("ID"):
                    parents.append(Identifier(self.current_token.val))
                    self.advance()
                else:
                    raise ParserError(f"Expected parent class name, got {self.current_token.type}")
                
                if self.match("DELIM", ","):
                    self.advance()
                else:
                    break
        
        # Parse class body
        self.expect("DELIM", "{")
        
        statements = []
        while self.current_token and not self.match("DELIM", "}"):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.expect("DELIM", "}")
        
        body = Body(statements)
        return ClassNode(name, body, generic_params, parents)
    
    def parse_expression_statement(self) -> Optional[ASTNode]:
        """Parse an expression statement"""
        expr = self.parse_expression()
        if expr:
            self.consume("DELIM", ";")
            return expr
        return None
    
    def parse_expression(self) -> Optional[ASTNode]:
        """Parse an expression"""
        return self.parse_assignment()
    
    def parse_assignment(self) -> Optional[ASTNode]:
        """Parse assignment expressions"""
        left = self.parse_conditional()
        
        if self.match("OP", "=") or self.match("OP", "+=") or self.match("OP", "-=") or \
           self.match("OP", "*=") or self.match("OP", "/=") or self.match("OP", "%=") or \
           self.match("OP", "&=") or self.match("OP", "|=") or self.match("OP", "^=") or \
           self.match("OP", "<<=") or self.match("OP", ">>="):
            op = self.current_token.val
            self.advance()
            right = self.parse_assignment()
            
            # Create an assignment node
            if isinstance(left, Identifier):
                # Simple assignment
                if op == "=":
                    return BinaryExpression(left, op, right)
                else:
                    # Compound assignment (a += b -> a = a + b)
                    inner_op = op[:-1]  # Remove the '=' from '+=' etc.
                    inner_expr = BinaryExpression(left, inner_op, right)
                    return BinaryExpression(left, "=", inner_expr)
        
        return left
    
    def parse_conditional(self) -> Optional[ASTNode]:
        """Parse conditional (ternary) expressions"""
        expr = self.parse_logical_or()
        
        if self.match("OP", "?"):
            self.advance()
            true_expr = self.parse_expression()
            self.expect("OP", ":")
            false_expr = self.parse_conditional()
            return TernaryExpr(expr, true_expr, false_expr)
        
        return expr
    
    def parse_logical_or(self) -> Optional[ASTNode]:
        """Parse logical OR expressions"""
        expr = self.parse_logical_and()
        
        while self.match("OP", "||"):
            op = self.current_token.val
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryExpression(expr, op, right)
        
        return expr
    
    def parse_logical_and(self) -> Optional[ASTNode]:
        """Parse logical AND expressions"""
        expr = self.parse_equality()
        
        while self.match("OP", "&&"):
            op = self.current_token.val
            self.advance()
            right = self.parse_equality()
            expr = BinaryExpression(expr, op, right)
        
        return expr
    
    def parse_equality(self) -> Optional[ASTNode]:
        """Parse equality expressions (==, !=)"""
        expr = self.parse_relational()
        
        while self.match("OP", "==") or self.match("OP", "!="):
            op = self.current_token.val
            self.advance()
            right = self.parse_relational()
            expr = Comparison(expr, op, right)
        
        return expr
    
    def parse_relational(self) -> Optional[ASTNode]:
        """Parse relational expressions (<, <=, >, >=)"""
        expr = self.parse_additive()
        
        while self.match("OP", "<") or self.match("OP", "<=") or \
              self.match("OP", ">") or self.match("OP", ">="):
            op = self.current_token.val
            self.advance()
            right = self.parse_additive()
            expr = Comparison(expr, op, right)
        
        return expr
    
    def parse_additive(self) -> Optional[ASTNode]:
        """Parse additive expressions (+, -)"""
        expr = self.parse_multiplicative()
        
        while self.match("OP", "+") or self.match("OP", "-"):
            op = self.current_token.val
            self.advance()
            right = self.parse_multiplicative()
            expr = BinaryExpression(expr, op, right)
        
        return expr
    
    def parse_multiplicative(self) -> Optional[ASTNode]:
        """Parse multiplicative expressions (*, /, %)"""
        expr = self.parse_unary()
        
        while self.match("OP", "*") or self.match("OP", "/") or self.match("OP", "%"):
            op = self.current_token.val
            self.advance()
            right = self.parse_unary()
            expr = BinaryExpression(expr, op, right)
        
        return expr
    
    def parse_unary(self) -> Optional[ASTNode]:
        """Parse unary expressions (!, -, +, ~)"""
        if self.match("OP", "!") or self.match("OP", "-") or \
           self.match("OP", "+") or self.match("OP", "~"):
            op = self.current_token.val
            self.advance()
            operand = self.parse_unary()
            return UnaryExpression(op, operand)
        
        return self.parse_primary()
    
    def parse_primary(self) -> Optional[ASTNode]:
        """Parse primary expressions (literals, identifiers, function calls, etc.)"""
        if not self.current_token:
            return None
        
        # Literals
        if self.current_token.type == "LITERAL":
            return self.parse_literal()
        
        # Identifiers
        if self.match("ID"):
            identifier = Identifier(self.current_token.val)
            self.advance()
            
            # Check if this is a function call
            if self.match("DELIM", "("):
                return self.parse_function_call(identifier)
            
            # Check if this is a generic instantiation
            if self.match("DELIM", "<"):
                generic_args = self.parse_generic_arguments()
                
                # Check if this is followed by a function call
                if self.match("DELIM", "("):
                    return self.parse_function_call(identifier, generic_args)
                
                # Otherwise, it's a type with generic parameters
                return Identifier(f"{identifier.val}<{', '.join(str(arg) for arg in generic_args)}>")
            
            return identifier
        
        # Parenthesized expressions
        if self.match("DELIM", "("):
            self.advance()
            expr = self.parse_expression()
            self.expect("DELIM", ")")
            return expr
        
        # List/map literals
        if self.match("DELIM", "{"):
            return self.parse_collection_literal()
        
        # Lambda expressions
        if self.match("KEYW", "lambda"):
            return self.parse_lambda_expression()
        
        return None
    
    def parse_literal(self) -> Optional[Literal]:
        """Parse a literal value"""
        if not self.current_token or self.current_token.type != "LITERAL":
            return None
        
        token = self.current_token
        self.advance()
        
        # Determine the literal type based on the token value
        if token.val in ["true", "false"]:
            return BoolLiteral(token.val == "true")
        elif token.val.startswith('"'):
            if token.val.startswith('$"'):
                return InterpolatedStringLiteral(token.val)
            elif token.val.startswith('R"'):
                return RawStringLiteral(token.val[2:-1])  # Remove R" and "
            else:
                return NormalStringLiteral(token.val[1:-1])  # Remove quotes
        elif token.val.startswith("'"):
            return NormalStringLiteral(token.val[1:-1])  # Remove quotes
        elif token.val.replace('.', '').replace('-', '').isdigit():
            return NumericLiteral(token.val)
        
        # Default to string literal for unknown literals
        return NormalStringLiteral(token.val)
    
    def parse_function_call(self, target: Identifier, generic_args: List[str] = None) -> FunctionCall:
        """Parse a function call"""
        self.expect("DELIM", "(")
        
        params = []
        while self.current_token and not self.match("DELIM", ")"):
            # Check for named parameters
            if self.match("ID") and self.peek() and self.peek().val == "=":
                name = Identifier(self.current_token.val)
                self.advance()
                self.expect("OP", "=")
                value = self.parse_expression()
                params.append(FuncCallParam(value, name))
            else:
                value = self.parse_expression()
                params.append(FuncCallParam(value))
            
            # Check for comma
            if self.match("DELIM", ","):
                self.advance()
        
        self.expect("DELIM", ")")
        
        # Convert generic args to identifiers
        generic_params = []
        if generic_args:
            for arg in generic_args:
                generic_params.append(GenericParam(Identifier(arg)))
        
        return FunctionCall(target, params, generic_params)
    
    def parse_generic_arguments(self) -> List[str]:
        """Parse generic arguments"""
        self.expect("DELIM", "<")
        
        args = []
        while self.current_token and not self.match("DELIM", ">"):
            if self.match("TYPE") or self.match("ID"):
                args.append(self.current_token.val)
                self.advance()
            
            # Check for comma
            if self.match("DELIM", ","):
                self.advance()
        
        self.expect("DELIM", ">")
        return args
    
    def parse_collection_literal(self) -> Union[ItemContainerLiteral, KVContainerLiteral]:
        """Parse a collection literal (list, map, etc.)"""
        self.expect("DELIM", "{")
        
        # Check if this is a map (key-value pairs)
        elements = []
        is_map = False
        
        while self.current_token and not self.match("DELIM", "}"):
            # Parse key or element
            key_or_element = self.parse_expression()
            
            # Check for key-value pair
            if self.match("OP", ":"):
                self.advance()
                value = self.parse_expression()
                elements.append((key_or_element, value))
                is_map = True
            else:
                elements.append(key_or_element)
            
            # Check for comma
            if self.match("DELIM", ","):
                self.advance()
        
        self.expect("DELIM", "}")
        
        if is_map:
            return KVContainerLiteral(elements)
        else:
            return ItemContainerLiteral(elements)
    
    def parse_lambda_expression(self) -> LambdaExpr:
        """Parse a lambda expression"""
        self.expect("KEYW", "lambda")
        
        # Parse parameters
        self.expect("DELIM", "(")
        params = self.parse_parameter_list()
        self.expect("DELIM", ")")
        
        # Parse return type
        return_type = None
        if self.match("DELIM", ":"):
            self.advance()
            if self.match("TYPE") or self.match("ID"):
                return_type = Identifier(self.current_token.val)
                self.advance()
        
        # Parse body
        if self.match("OP", "=>"):
            # Single expression lambda
            self.advance()
            expr = self.parse_expression()
            body = Body([Return(expr)])
        else:
            # Block lambda
            body = self.parse_block()
        
        # Convert parameters to the format expected by LambdaExpr
        lambda_params = []
        for param in params:
            lambda_params.append((param.name, param.param_type))
        
        return LambdaExpr(lambda_params, body, return_type)

def parse_source(source: str) -> Program:
    """Convenience function to parse source code"""
    tokens, cpp_blocks = Lexer.lex_source(source, include_comments=False)
    parser = Parser(tokens, cpp_blocks)
    return parser.parse()

def parse_file(file_path: str) -> Program:
    """Convenience function to parse a file"""
    tokens, cpp_blocks = Lexer.lex_source_from_file(file_path, include_comments=False)
    parser = Parser(tokens, cpp_blocks)
    return parser.parse()

if __name__ == "__main__":
    # Test the parser with the sample code
    from lexer import SAMPLE
    
    try:
        program = parse_source(SAMPLE)
        print("Parsing successful!")
        print("Generated C++ code:")
        print(program.To_CXX())
    except Exception as e:
        print(f"Error during parsing: {e}")
        import traceback
        traceback.print_exc()