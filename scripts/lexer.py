#! venv/bin/python
from lark import Lark, Token
GRAMMAR_CONTENT = r'''
start: (statement | NEWLINE)*

decorator: "@" decorator_name
decorator_name: "def" | "const" | "pre" | "post" | "checked" | "io" | "safe" | "unsafe" | "static" | "abstract"

decorated_stmt: decorator statement

statement: decorated_stmt | simple_statement | compound_statement | variable_decl | assignment

simple_statement: (expression | import_stmt) 

compound_statement: function_def | class_def | if_stmt | while_stmt | for_stmt | try_stmt

// Variable declaration with optional initialization
variable_decl: type_annotation ID ["=" expression] 

// Assignment to existing variables
assignment: target assign_op expression 

// Function definitions
function_def: decorator* visibility? "static"? "func" ID "(" parameter_list? ")" ["->" type_annotation] suite
parameter_list: parameter ("," parameter)*
parameter: [type_annotation] ID ["=" expression]

// Literals must come FIRST in order of priority
BINARY: /0[bB]_*[01][01_]*/
HEX: /0[xX]_*[0-9a-fA-F][0-9a-fA-F_]*/
OCT: /0[oO]_*[0-7][0-7_]*/
NUMBER: /[0-9][0-9_]*(?:\.[0-9_]+)?(?:[eE][+-]?[0-9_]+)?/
CHAR: /'(?:\\.|[^'\\])'/
STRING: /"(?:\\.|[^"\\])*"/
FSTRING: /f"(?:[^"\\]|\\.|\${(?:[^{}"\\]|\\.|{[^{}]*})*})*"/


// Class definitions

class_def: "class" ID class_suite

class_suite: "{" class_member* "}"

class_member: function_def | variable_decl | assignment
inheritance_list: ID ("," ID)*

// Control flow
if_stmt: "if" expression suite ("elif" expression suite)* ["else" suite]
while_stmt: "while" expression suite
for_stmt: "for" [type_annotation] ID ["," [type_annotation] ID]* "in" expression suite
         | "for" [type_annotation] ID "=" expression "," expression "," expression suite
// Try-catch
try_stmt: "try" suite ("catch" [ID] suite)* ["finally" suite]

// Import statements
import_stmt: "import" import_name ("," import_name)*
import_name: dotted_name ["as" ID]
dotted_name: ID ("." ID)*

// Assignments and expressions
target: ID | attribute_ref | subscription
attribute_ref: expression "." ID
subscription: expression "[" expression "]"

assign_op: "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "&=" | "|=" | "^=" | "<<=" | ">>="

// Expressions (with proper precedence)
expression: conditional_expr
conditional_expr: or_test ["if" or_test "else" expression]
or_test: and_test ("or" and_test)*
and_test: not_test ("and" not_test)*
not_test: "not" not_test | comparison
comparison: bitwise_or (comp_op bitwise_or)*
bitwise_or: bitwise_xor ("|" bitwise_xor)*
bitwise_xor: bitwise_and ("^" bitwise_and)*
bitwise_and: shift_expr ("&" shift_expr)*
shift_expr: arith_expr (("<<" | ">>") arith_expr)*
arith_expr: term (("+" | "-") term)*
term: factor (("*" | "/" | "%" ) factor)*
factor: ("+" | "-" | "~") factor | power
power: atom_expr ["**" factor]
atom_expr: atom trailer*
atom: ("(" [expression] ")"
     | "[" [expression_list] "]"   // List literal
     | "{" [dict_or_set_maker] "}"  // Dict/set literal
     | ID | NUMBER | CHAR | STRING | FSTRING | BINARY | HEX | OCT | "true" | "false" | constructor_call | lambda_expr)

trailer: "(" [argument_list] ")" | "[" expression "]" | "." ID

// Function calls and constructors
constructor_call: ID "(" [argument_list] ")"
argument_list: expression ("," expression)*

// Lambda expressions
lambda_expr: "lambda" "(" parameter_list? ")" ["->" type_annotation] "==>" expression

// Collections
expression_list: expression ("," expression)*
dict_or_set_maker: dict_maker | set_maker
dict_maker: dict_pair ("," dict_pair)*
dict_pair: expression ":" expression
set_maker: expression ("," expression)*

// Type annotations
type_annotation: basic_type | generic_type | function_type | inferred_type
basic_type: TYPE
generic_type: TYPE "[" type_annotation ("," type_annotation)* "]"
function_type: "func" "(" [type_annotation ("," type_annotation)*] ")" ["->" type_annotation]
inferred_type: "auto" | "var"

// Visibility and modifiers
visibility: "public" | "private" | "protected"

// Code blocks
suite: "{" statement* "}"


// Comparison operators
comp_op: "==" | "!=" | "<" | "<=" | ">" | ">=" | "is" | "in"

// Tokens section - CRITICAL CHANGES HERE:


// Container literals
COLON_COLON: "::"
LBRACE: "{"
RBRACE: "}"
LBRACK: "["
RBRACK: "]"
LPAR: "("
RPAR: ")"
COMMA: ","
COLON: ":"

// Keywords
RETURN: "return"
CONST: "const"
OVERRIDE: "override"
MATCH: "match"
FUNC: "func"
CLASS: "class"
IF: "if"
ELSE: "else"
ELIF: "elif"
WHILE: "while"
FOR: "for"
IN: "in"
AS: "as"
IS: "is"
NEW: "new"
STATIC: "static"
PUBLIC: "public"
PRIVATE: "private"
PROTECTED: "protected"
SUPER: "super"
SELF: "self"
DELETE: "delete"
PASS: "pass"
RAISE: "raise"
WITH: "with"
TRY: "try"
CATCH: "catch"
FINALLY: "finally"
THROW: "throw"
LAMBDA: "lambda"
TRUE: "true"
FALSE: "false"

// Types
TYPE.2: "int" | "i32" | "u32" | "u64" | "float" | "f64" | "decimal" | "string" | "str" | "char"
    | "list" | "map" | "set" | "tuple" | "range" | "any" | "void" | "auto" | "bool" | "var"
    | "bin" | "hex" | "oct" | "type"

// Operators - ADDED: Question mark for ternary operator
DOT: "."
PLUS: "+"
MINUS: "-"
STAR: "*"
SLASH: "/"
PERCENT: "%"
AMPERSAND: "&"
PIPE: "|"
CARET: "^"
TILDE: "~"
LESSTHAN: "<"
MORETHAN: ">"
EQUAL: "="
NOT: "!"

QUESTION: "?"
ARROW: "->"
PLUS_ASSIGN: "+="
MINUS_ASSIGN: "-="
STAR_ASSIGN: "*="
SLASH_ASSIGN: "/="
PERCENT_ASSIGN: "%="
AMPERSAND_ASSIGN: "&="
PIPE_ASSIGN: "|="
CARET_ASSIGN: "^="
LEFT_SHIFT_ASSIGN: "<<="
RIGHT_SHIFT_ASSIGN: ">>="
EQUAL_EQUAL: "=="
NOT_EQUAL: "!="
LESS_EQUAL: "<="
GREATER_EQUAL: ">="

// Structural
INDENT: "INDENT"
DEDENT: "DEDENT"
COMMENT: "//"(\n)*?             // Single-line: // comment
      | "/*"(.|\n)*?"*/"         // Multi-line: /* ... */
DECOR: /@[a-zA-Z_][a-zA-Z0-9_]*/
ID: /[a-zA-Z_][a-zA-Z0-9_]*/
NEWLINE: /\n/

%import common.WS
%ignore COMMENT
%ignore WS
'''

class IndentationLexer:
    def __init__(self, parser):
        self.parser = parser
        self.indent_stack = [0]
        self.in_block_comment = False
        self.block_comment_buffer = []
        self.block_comment_indent = 0
        
        # Define type keywords that should be recognized as TYPE tokens
        self.type_keywords = {
            'int', 'short', 'u32', 'u64', 'float', 'f64', 'decimal', 
            'string', 'str', 'char', 'list', 'map', 'set', 'tuple', 
            'any', 'void', 'auto', 'bool', 'union', 'bin', 'hex', 'oct', 'type'
        }
        
        # Define other keywords that should not be treated as identifiers
        self.keywords = {
            'return', 'const', 'override', 'match', 'assert', 'func', 'class',
            'if', 'else', 'elif', 'while', 'for', 'in', 'import', 'as', 'is',
            'new', 'static', 'public', 'private', 'protected', 'super', 'pass',
            'raise', 'with', 'try', 'catch', 'finally', 'throw', 'lambda',
            'true', 'false', 'and', 'or', 'not', 'if', 'else'  # Added if/else for conditional expressions
        }

    def _get_fstring_delimiters(self, line, pos):
        """Determine the opening and closing quotes for f-strings"""
        if line[pos:pos+4] == 'f"""':
            return 'f"""', '"""'
        elif line[pos:pos+4] == "f'''":
            return "f'''", "'''"
        elif line[pos:pos+2] == 'f"':
            return 'f"', '"'
        elif line[pos:pos+2] == "f'":
            return "f'", "'"
        return None, None

    def _tokenize_fstring(self, line, start_pos):
        """Tokenize any type of f-string with proper markers"""
        start_delim, end_delim = self._get_fstring_delimiters(line, start_pos)
        if not start_delim:
            return [], start_pos
            
        tokens = []
        tokens.append(Token('FSTRING_START', start_delim))
        i = start_pos + len(start_delim)
        current_text = []
        
        while i < len(line) and not line.startswith(end_delim, i):
            if line[i:i+2] == '${':
                # Add any accumulated text
                if current_text:
                    tokens.append(Token('STRING_CONTENT', ''.join(current_text)))
                    current_text = []
                
                # Add interpolation markers
                tokens.append(Token('INTERPOLATION_START', '${'))
                i += 2
                
                # Tokenize the expression content
                expr_start = i
                brace_depth = 1
                while i < len(line) and brace_depth > 0:
                    if line[i] == '{':
                        brace_depth += 1
                    elif line[i] == '}':
                        brace_depth -= 1
                    i += 1
                
                expr_content = line[expr_start:i-1]
                expr_tokens = self._tokenize_line(expr_content)
                tokens.extend(expr_tokens)
                tokens.append(Token('INTERPOLATION_END', '}'))
            else:
                # Regular string content
                if line[i] == '\\':
                    # Handle escape sequences
                    if i + 1 < len(line):
                        esc_char = line[i+1]
                        current_text.append(f'\\{esc_char}')
                        i += 2
                    else:
                        current_text.append('\\')
                        i += 1
                else:
                    current_text.append(line[i])
                    i += 1
        
        # Add any remaining text
        if current_text:
            tokens.append(Token('STRING_CONTENT', ''.join(current_text)))
        
        # Add closing quote
        if i + len(end_delim) <= len(line):
            tokens.append(Token('FSTRING_END', end_delim))
            i += len(end_delim)
        else:
            raise SyntaxError("Unclosed f-string")
            
        return tokens, i

    def _tokenize_line(self, line):
        """Tokenize a single line of code"""
        tokens = []
        i = 0
        
        while i < len(line):
            # Skip whitespace
            if line[i].isspace():
                i += 1
                continue
                
            # Handle f-strings
            if line[i:i+2] == 'f"':
                fstring_tokens, new_i = self._tokenize_fstring(line, i)
                tokens.extend(fstring_tokens)
                i = new_i
                continue
                
            # Handle regular strings
            if line[i] in ('"', "'"):
                token, new_i = self._tokenize_string(line, i)
                tokens.append(token)
                i = new_i
                continue
                
            # Handle numbers
            if line[i].isdigit():
                token, new_i = self._tokenize_number(line, i)
                tokens.append(token)
                i = new_i
                continue
                
            # Check for multi-character operators
            if i + 1 < len(line):
                two_char = line[i:i+2]
                if two_char in ['==', '!=', '<=', '>=', '<<', '>>', '->', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=']:
                    tokens.append(Token(self._get_operator_type(two_char), two_char))
                    i += 2
                    continue
                
                # Check for three-character operators
                if i + 2 < len(line):
                    three_char = line[i:i+3]
                    if three_char in ['<<=', '>>=']:
                        tokens.append(Token(self._get_operator_type(three_char), three_char))
                        i += 3
                        continue
            
            # Handle single character tokens
            char = line[i]
            if char in '()[]{}':
                token_type = {'(': 'LPAR', ')': 'RPAR', '[': 'LBRACK', ']': 'RBRACK', 
                             '{': 'LBRACE', '}': 'RBRACE'}[char]
                tokens.append(Token(token_type, char))
                i += 1
            elif char in '.,:':
                token_type = {'.': 'DOT', ',': 'COMMA', '': 'SEMICOLON', ':': 'COLON'}[char]
                tokens.append(Token(token_type, char))
                i += 1
            elif char in '+-*/%&|^~<>=!?':
                token_type = self._get_operator_type(char)
                tokens.append(Token(token_type, char))
                i += 1
            else:
                # Handle identifiers and keywords
                start = i
                if char.isalpha() or char == '_':
                    while i < len(line) and (line[i].isalnum() or line[i] == '_'):
                        i += 1
                    value = line[start:i]
                    
                    if value in self.type_keywords:
                        tokens.append(Token('TYPE', value))
                    elif value in self.keywords:
                        token_type = value.upper()
                        tokens.append(Token(token_type, value))
                    else:
                        tokens.append(Token('ID', value))
                else:
                    i += 1
        
        return tokens

    def _tokenize_string(self, line, start_pos):
        """Tokenize a regular string literal"""
        quote_char = line[start_pos]
        i = start_pos + 1
        value = [quote_char]
        
        while i < len(line):
            if line[i] == '\\':
                # Handle escape sequence
                if i + 1 < len(line):
                    value.append(line[i:i+2])
                    i += 2
                else:
                    value.append(line[i])
                    i += 1
            elif line[i] == quote_char:
                value.append(quote_char)
                i += 1
                break
            else:
                value.append(line[i])
                i += 1
                
        return Token('STRING', ''.join(value)), i

    def _tokenize_number(self, line, start_pos):
        """Tokenize numeric literals"""
        i = start_pos
        if line[i:i+2].lower() == '0x':
            i += 2
            while i < len(line) and (line[i].isdigit() or line[i].lower() in 'abcdef' or line[i] == '_'):
                i += 1
            value = line[start_pos:i]
            return Token('HEX', value), i
        elif line[i:i+2].lower() == '0b':
            i += 2
            while i < len(line) and (line[i] in '01' or line[i] == '_'):
                i += 1
            value = line[start_pos:i]
            return Token('BINARY', value), i
        elif line[i:i+2].lower() == '0o':
            i += 2
            while i < len(line) and (line[i] in '01234567' or line[i] == '_'):
                i += 1
            value = line[start_pos:i]
            return Token('OCT', value), i
        else:
            while i < len(line) and (line[i].isdigit() or line[i] in '._eE+-'):
                i += 1
            value = line[start_pos:i]
            return Token('NUMBER', value), i

    def _get_operator_type(self, op):
        """Get the token type for operators"""
        op_map = {
            '==': 'EQUAL_EQUAL', '!=': 'NOT_EQUAL', '<=': 'LESS_EQUAL', '>=': 'GREATER_EQUAL',
            '<<': 'LEFT_SHIFT', '>>': 'RIGHT_SHIFT', '->': 'ARROW',
            '+=': 'PLUS_ASSIGN', '-=': 'MINUS_ASSIGN', '*=': 'STAR_ASSIGN', '/=': 'SLASH_ASSIGN',
            '%=': 'PERCENT_ASSIGN', '&=': 'AMPERSAND_ASSIGN', '|=': 'PIPE_ASSIGN', '^=': 'CARET_ASSIGN',
            '<<=': 'LEFT_SHIFT_ASSIGN', '>>=': 'RIGHT_SHIFT_ASSIGN',
            '+': 'PLUS', '-': 'MINUS', '*': 'STAR', '/': 'SLASH', '%': 'PERCENT',
            '&': 'AMPERSAND', '|': 'PIPE', '^': 'CARET', '~': 'TILDE',
            '<': 'LESSTHAN', '>': 'MORETHAN', '=': 'EQUAL', '!': 'NOT', '?': 'QUESTION'
        }
        return op_map.get(op, 'UNKNOWN')

    def lex_with_indentation(self, source_code):
        lines = source_code.split('\n')
        all_tokens = []
        in_block_comment = False

        line_num = 0
        while line_num < len(lines):
            line = lines[line_num]
            stripped = line.lstrip()

            # Handle multi-line comments (## ... ##)
            if in_block_comment:
                if "##" in stripped:
                    in_block_comment = False
                    # Remove up to and including the closing ##
                    idx = stripped.find("##") + 2
                    stripped = stripped[idx:]
                    if not stripped.strip():
                        line_num += 1
                        continue
                else:
                    line_num += 1
                    continue

            if stripped.startswith("##"):
                in_block_comment = True
                # Remove after opening ##
                idx = stripped.find("##") + 2
                stripped = stripped[idx:]
                if not stripped.strip():
                    line_num += 1
                    continue

            # Remove single-line comments (but not inside strings)
            if "#" in stripped:
                in_string = False
                result = []
                i = 0
                while i < len(stripped):
                    if stripped[i] in ('"', "'"):
                        quote = stripped[i]
                        result.append(stripped[i])
                        i += 1
                        while i < len(stripped) and stripped[i] != quote:
                            # Handle escaped quotes
                            if stripped[i] == '\\' and i + 1 < len(stripped):
                                result.append(stripped[i])
                                result.append(stripped[i+1])
                                i += 2
                            else:
                                result.append(stripped[i])
                                i += 1
                        if i < len(stripped):
                            result.append(stripped[i])
                            i += 1
                    elif stripped[i] == "#" and (i == 0 or stripped[i-1] != "#"):
                        break  # Start of comment
                    else:
                        result.append(stripped[i])
                        i += 1
                stripped = ''.join(result)
                if not stripped.strip():
                    line_num += 1
                    continue

            if not stripped.strip():
                line_num += 1
                continue

            indent_level = len(line) - len(line.lstrip())
            indent_tokens = self._handle_indentation(indent_level, line_num + 1)
            all_tokens.extend(indent_tokens)

            try:
                line_tokens = self._tokenize_line(stripped.strip())
                all_tokens.extend(line_tokens)
            except Exception as e:
                print(f"Error lexing line {line_num + 1}: {e}")
                line_num += 1
                continue

            all_tokens.append(Token('NEWLINE', '\\n'))
            line_num += 1

        final_dedents = self._handle_indentation(0, len(lines) + 1)
        all_tokens.extend(final_dedents)

        return all_tokens

    def _handle_indentation(self, current_indent, line_num):
        tokens = []
        last_indent = self.indent_stack[-1]

        if current_indent > last_indent:
            self.indent_stack.append(current_indent)
            tokens.append(Token('INDENT', f'INDENT({current_indent})'))
        elif current_indent < last_indent:
            while self.indent_stack and self.indent_stack[-1] > current_indent:
                dedent_level = self.indent_stack.pop()
                tokens.append(Token('DEDENT', f'DEDENT({dedent_level})'))
            if not self.indent_stack or self.indent_stack[-1] != current_indent:
                raise IndentationError(f"Inconsistent indentation at line {line_num}")
        return tokens


def main():
    parser = Lark(GRAMMAR_CONTENT, parser="lalr", lexer="basic", start="start")
    lexer = IndentationLexer(parser)
    source_code = r"""
func main() -> int {
    io::Output("Hello, world!")

    // Input example
    string name = io::Input("Enter your name: ")
    io::Output($"Hello, {name}!")

    // Write to file
    string data = "Sample data\nSecond line"
    io::File file = Open("output.text", "rw")

    // Read from file
    string content = file.Read()
    io::Output("File content:")
    io::Output(content)
    return 0
}
"""

    try:
        tokens = lexer.lex_with_indentation(source_code)
        for token in tokens:
            print(f"{token.type}: {token.value}")

    except IndentationError as e:
        print(f"Indentation Error: {e}")

if __name__ == "__main__":
    main()