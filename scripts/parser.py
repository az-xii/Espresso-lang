from lexer import Token, split_tokens
from ASTLib import *
from abc import ABC, abstractmethod
from typing import List, Tuple, Union, Optional
from dataclasses import dataclass

@dataclass
class PatternElement:
    """A dataclass representing an element in a pattern."""
    expected_type: str = None
    expected_value: str = None
    optional: bool = False
    handler: str = None  # Name of handler method for this element

    def match_type(self, token_type: str) -> bool:
        return self.expected_type is None or token_type == self.expected_type

    def match_value(self, token_value: str) -> bool:
        return self.expected_value is None or token_value == self.expected_value

    def matches(self, token: Token) -> bool:
        """Check if this pattern element matches the given token."""
        return self.match_type(token.type) and self.match_value(token.val)

class PatternType(ABC):
    """An abstract base class for pattern types."""
    def __init__(self, pattern: List[PatternElement], name: str):
        self.pattern = pattern
        self.name = name
        self.required_length = len([p for p in pattern if not p.optional])
    
    @abstractmethod
    def build_ast(self, matched_tokens: List[Token], parser: 'PatternParser') -> ASTNode:
        """Build an AST node from matched tokens."""
        pass
    
    def matches_at_index(self, token: Token, pattern_index: int) -> bool:
        """Check if the token matches the pattern element at the given index."""
        if pattern_index >= len(self.pattern):
            return False
        return self.pattern[pattern_index].matches(token)

class VarDeclarePattern(PatternType):
    """TYPE IDENTIFIER ["=" EXPRESSION] [;]"""
    def __init__(self):
        pattern = [
            PatternElement(expected_type="TYPE", handler="parse_type"),
            PatternElement(expected_type="ID", handler="parse_identifier"),
            PatternElement(expected_value="=", optional=True, handler="consume_operator"),
            PatternElement(expected_type="EXPRESSION", optional=True, handler="parse_expression"),
            PatternElement(expected_value=";", optional=True, handler="consume_delimiter")
        ]
        super().__init__(pattern, "var_declare")
    
    def build_ast(self, matched_tokens: List[Token], parser: 'PatternParser') -> VarDeclare:
        # TYPE ID = EXPR
        var_type = Identifier(matched_tokens[0].val)
        var_name = Identifier(matched_tokens[1].val)
        
        if len(matched_tokens) > 2 and matched_tokens[2].val == "=":
            value = parser._parse_expression_value(matched_tokens[3]) if len(matched_tokens) > 3 else None
            return VarAssign(var_name, value, var_type)
        else:
            return VarDeclare(var_name, var_type)

class VarAssignPattern(PatternType):
    """IDENTIFIER OP EXPRESSION [;]"""
    def __init__(self):
        pattern = [
            PatternElement(expected_type="ID", handler="parse_identifier"),
            PatternElement(expected_type="OP", handler="parse_operator"),
            PatternElement(expected_type="EXPRESSION", handler="parse_expression"),
            PatternElement(expected_value=";", optional=True, handler="consume_delimiter")
        ]
        super().__init__(pattern, "var_assign")
    
    def build_ast(self, matched_tokens: List[Token], parser: 'PatternParser') -> VarAssign:
        # ID OP EXPR
        var_name = Identifier(matched_tokens[0].val)
        operator = matched_tokens[1].val
        value = parser._parse_expression_value(matched_tokens[2])
        
        # Handle compound assignments (+=, -=, etc.)
        if operator.endswith("=") and len(operator) > 1:
            base_op = operator[:-1]
            current_value = Identifier(var_name.To_CXX())
            value = BinaryExpression(current_value, base_op, value)
            
        return VarAssign(var_name, value, None)

class FunctionDeclPattern(PatternType):
    """func ID [GENERICS] (PARAMS) [-> TYPE] { BODY }"""
    def __init__(self):
        pattern = [
            PatternElement(expected_value="func", handler="consume_keyword"),
            PatternElement(expected_type="ID", handler="parse_identifier"),
            PatternElement(expected_value="<", optional=True, handler="parse_generics_start"),
            PatternElement(expected_type="GENERICS", optional=True, handler="parse_generics"),
            PatternElement(expected_value=">", optional=True, handler="parse_generics_end"),
            PatternElement(expected_value="(", handler="consume_delimiter"),
            PatternElement(expected_type="PARAMS", handler="parse_params"),
            PatternElement(expected_value=")", handler="consume_delimiter"),
            PatternElement(expected_value="->", optional=True, handler="consume_operator"),
            PatternElement(expected_type="TYPE", optional=True, handler="parse_type"),
            PatternElement(expected_value="{", handler="consume_delimiter"),
            PatternElement(expected_type="BODY", handler="parse_body"),
            PatternElement(expected_value="}", handler="consume_delimiter")
        ]
        super().__init__(pattern, "func_decl")
    
    def build_ast(self, matched_tokens: List[Token], parser: 'PatternParser') -> FunctionDecl:
        # Extract components from matched tokens
        name = Identifier(matched_tokens[1].val)  # token[0] is "func"
        
        # Find positions of key elements
        paren_start = next(i for i, t in enumerate(matched_tokens) if t.val == "(")
        paren_end = next(i for i, t in enumerate(matched_tokens) if t.val == ")")
        brace_start = next(i for i, t in enumerate(matched_tokens) if t.val == "{")
        
        # Extract parameters (between parentheses)
        params = parser._extract_params(matched_tokens[paren_start+1:paren_end])
        
        # Extract return type (after -> if present)
        return_type = None
        if "->" in [t.val for t in matched_tokens]:
            arrow_idx = next(i for i, t in enumerate(matched_tokens) if t.val == "->")
            return_type = Identifier(matched_tokens[arrow_idx + 1].val)
        
        # Extract body (between braces)
        body_tokens = matched_tokens[brace_start+1:-1]  # Exclude closing brace
        body = parser._parse_body_tokens(body_tokens)
        
        return FunctionDecl(name, params, return_type, [], body)

class FunctionCallPattern(PatternType):
    """ID [GENERICS] (ARGS) [;]"""
    def __init__(self):
        pattern = [
            PatternElement(expected_type="ID", handler="parse_identifier"),
            PatternElement(expected_value="<", optional=True, handler="parse_generics_start"),
            PatternElement(expected_type="GENERICS", optional=True, handler="parse_generics"),
            PatternElement(expected_value=">", optional=True, handler="parse_generics_end"),
            PatternElement(expected_value="(", handler="consume_delimiter"),
            PatternElement(expected_type="ARGS", handler="parse_args"),
            PatternElement(expected_value=")", handler="consume_delimiter"),
            PatternElement(expected_value=";", optional=True, handler="consume_delimiter")
        ]
        super().__init__(pattern, "func_call")
    
    def build_ast(self, matched_tokens: List[Token], parser: 'PatternParser') -> FunctionCall:
        target = Identifier(matched_tokens[0].val)
        
        # Find parentheses positions
        paren_start = next(i for i, t in enumerate(matched_tokens) if t.val == "(")
        paren_end = next(i for i, t in enumerate(matched_tokens) if t.val == ")")
        
        # Extract arguments
        args = parser._extract_args(matched_tokens[paren_start+1:paren_end])
        
        return FunctionCall(target, args)

# Registry of all patterns
PATTERN_REGISTRY: List[PatternType] = [
    FunctionDeclPattern(),
    FunctionCallPattern(),
    VarDeclarePattern(),
    VarAssignPattern()
]

def lookup_patterns(token: Token, patterns: List[PatternType], pattern_index: int = 0) -> List[PatternType]:
    """
    Filter patterns to only those that match the current token at the given pattern index.
    
    Args:
        token: Current token to match
        patterns: List of candidate patterns
        pattern_index: Which position in the pattern to check
    
    Returns:
        List of patterns that match at this position
    """
    matching_patterns = []
    
    for pattern in patterns:
        if pattern_index < len(pattern.pattern):
            pattern_element = pattern.pattern[pattern_index]
            if pattern_element.matches(token):
                matching_patterns.append(pattern)
    
    return matching_patterns

class PatternParser:
    """A parser that uses pattern matching to build an AST."""
    
    @staticmethod
    def parse(tokens: List[Token], cpp_blocks: List[str]) -> Program:
        """Static method to parse tokens into a Program."""
        parser = PatternParser(tokens, cpp_blocks)
        return parser._parse()
    
    def __init__(self, tokens: List[Token], cpp_blocks: List[str]):
        self.tokens = tokens
        self.cpp_blocks = cpp_blocks
        self.current_line = 0
        self.current_token_idx = 0
        self.lines = split_tokens(tokens)
        
    def _get_current_token(self) -> Optional[Token]:
        """Get the current token, or None if at end."""
        if (self.current_line < len(self.lines) and 
            self.current_token_idx < len(self.lines[self.current_line])):
            return self.lines[self.current_line][self.current_token_idx]
        return None
    
    def _consume_token(self) -> Optional[Token]:
        """Consume the current token and advance to the next."""
        token = self._get_current_token()
        if token:
            self.current_token_idx += 1
            # Move to next line if at end of current line
            if self.current_token_idx >= len(self.lines[self.current_line]):
                self.current_line += 1
                self.current_token_idx = 0
        return token
    
    def _parse(self) -> Program:
        """Main parsing method following your exact flow."""
        statements = []
        
        while self.current_line < len(self.lines):
            current_patterns = PATTERN_REGISTRY.copy()
            pattern_index = 0
            matched_tokens = []
            
            while current_patterns and self._get_current_token():
                token = self._get_current_token()
                
                # Step 2: Lookup matching patterns based on token type/value
                current_patterns = lookup_patterns(token, current_patterns, pattern_index)
                
                # Step 3: Remove non-matches (already done by lookup_patterns)
                if not current_patterns:
                    break
                
                # Step 1: Consume token
                consumed_token = self._consume_token()
                matched_tokens.append(consumed_token)
                pattern_index += 1
                
                # Check if any pattern is fully matched
                for pattern in current_patterns:
                    if len(matched_tokens) >= pattern.required_length:
                        # Try to build AST with this pattern
                        try:
                            ast_node = pattern.build_ast(matched_tokens, self)
                            statements.append(ast_node)
                            matched_tokens = []  # Reset for next pattern
                            current_patterns = PATTERN_REGISTRY.copy()
                            pattern_index = 0
                            break
                        except Exception as e:
                            # Pattern didn't work, continue with others
                            continue
            
            # Step 4: If EOL, go to next line unless no next, then raise error
            if self._get_current_token() is None and self.current_line < len(self.lines) - 1:
                self.current_line += 1
                self.current_token_idx = 0
            elif not self._get_current_token() and self.current_line >= len(self.lines) - 1:
                break
        
        return Program(Body(statements))
    
    # Handler methods for pattern elements
    def parse_type(self, token: Token) -> Identifier:
        return Identifier(token.val)
    
    def parse_identifier(self, token: Token) -> Identifier:
        return Identifier(token.val)
    
    def parse_expression(self, token: Token) -> Value:
        return self._parse_expression_value(token)
    
    def consume_keyword(self, token: Token) -> None:
        pass  # Just consume, no AST node needed
    
    def consume_operator(self, token: Token) -> None:
        pass  # Just consume
    
    def consume_delimiter(self, token: Token) -> None:
        pass  # Just consume
    
    def parse_generics_start(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    def parse_generics(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    def parse_generics_end(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    def parse_params(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    def parse_body(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    def parse_args(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    def parse_operator(self, token: Token) -> None:
        pass  # Handled in build_ast method
    
    # Helper methods for AST construction
    def _parse_expression_value(self, token: Token) -> Value:
        """Convert a token to an expression value."""
        if token.type == "LITERAL":
            if token.val in ["true", "false"]:
                return BoolLiteral(token.val == "true")
            elif token.val.startswith('"'):
                return NormalStringLiteral(token.val.strip('"'))
            else:
                return NumericLiteral(token.val)
        elif token.type == "ID":
            return Identifier(token.val)
        else:
            return Identifier(token.val)  # Fallback
    
    def _extract_params(self, param_tokens: List[Token]) -> List[FuncDeclParam]:
        """Extract function parameters from tokens between parentheses."""
        params = []
        current_param = []
        
        for token in param_tokens:
            if token.val == ",":
                if current_param:
                    params.append(self._build_param(current_param))
                    current_param = []
            else:
                current_param.append(token)
        
        if current_param:
            params.append(self._build_param(current_param))
        
        return params
    
    def _build_param(self, param_tokens: List[Token]) -> FuncDeclParam:
        """Build a parameter from tokens."""
        if len(param_tokens) >= 2:
            param_type = Identifier(param_tokens[0].val)
            param_name = Identifier(param_tokens[1].val)
            default = None
            if len(param_tokens) > 2 and param_tokens[2].val == "=":
                default = self._parse_expression_value(param_tokens[3])
            return FuncDeclParam(param_name, param_type, default)
        raise SyntaxError(f"Invalid parameter tokens: {param_tokens}")
    
    def _extract_args(self, arg_tokens: List[Token]) -> List[FuncCallParam]:
        """Extract function arguments from tokens between parentheses."""
        args = []
        current_arg = []
        
        for token in arg_tokens:
            if token.val == ",":
                if current_arg:
                    args.append(self._build_arg(current_arg))
                    current_arg = []
            else:
                current_arg.append(token)
        
        if current_arg:
            args.append(self._build_arg(current_arg))
        
        return args
    
    def _build_arg(self, arg_tokens: List[Token]) -> FuncCallParam:
        """Build an argument from tokens."""
        if len(arg_tokens) == 1:
            return FuncCallParam(self._parse_expression_value(arg_tokens[0]))
        elif len(arg_tokens) > 2 and arg_tokens[1].val == "=":
            # Named argument: name=value
            arg_name = Identifier(arg_tokens[0].val)
            arg_value = self._parse_expression_value(arg_tokens[2])
            return FuncCallParam(arg_value, arg_name)
        else:
            # Positional argument sequence
            value = self._parse_expression_value(arg_tokens[0])
            return FuncCallParam(value)
    
    def _parse_body_tokens(self, body_tokens: List[Token]) -> Body:
        """Parse body tokens into a Body AST node."""
        # For now, return empty body - this would need recursive parsing
        return Body([])

# Example usage
if __name__ == "__main__":
    # Test with sample tokens
    test_tokens = [
        Token("KEYW", 1, 1, "func"),
        Token("ID", 1, 6, "main"),
        Token("DELIM", 1, 10, "("),
        Token("DELIM", 1, 11, ")"),
        Token("OP", 1, 13, "->"),
        Token("TYPE", 1, 16, "int"),
        Token("DELIM", 1, 19, "{"),
        Token("TYPE", 2, 5, "int"),
        Token("ID", 2, 9, "x"),
        Token("OP", 2, 11, "="),
        Token("LITERAL", 2, 13, "42"),
        Token("DELIM", 2, 15, ";"),
        Token("DELIM", 3, 1, "}")
    ]
    
    program = PatternParser.parse(test_tokens, [])
    print("Parsed successfully!")
    print(program.To_CXX())
