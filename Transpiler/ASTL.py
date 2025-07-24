from abc import ABC
from enum import Enum
from typing import List, Optional, Union, Tuple, Any, Literal, Dict, Set

# ==============================================
# Global Types
# ==============================================

# Enums
class NodeType(Enum):
    """Comprehensive node types for the Espresso language AST."""

    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    IDENTIFIER = "IDENTIFIER"
    BODY = "BODY"

    ANNOTATION_DEFINE = "ANNOTATION_DEFINE"
    ANNOTATION_ASSERT = "ANNOTATION_ASSERT"
    ANNOTATION_IO = "ANNOTATION_IO"
    ANNOTATION_SAFE = "ANNOTATION_SAFE"
    ANNOTATION_UNSAFE = "ANNOTATION_UNSAFE"
    ANNOTATION_PANIC = "ANNOTATION_PANIC"
    ANNOTATION_NAMESPACE = "ANNOTATION_NAMESPACE"


    PRIVATE_MODIFIER = "PRIVATE_MODIFIER"
    PUBLIC_MODIFIER = "PUBLIC_MODIFIER"
    PROTECTED_MODIFIER = "PROTECTED_MODIFIER"
    CONST_MODIFIER = "CONST_MODIFIER"
    CONSTEXPR_MODIFIER = "CONSTEXPR_MODIFIER"
    CONSTEVAL_MODIFIER = "CONSTEVAL_MODIFIER"
    STATIC_MODIFIER = "STATIC_MODIFIER"
    ABSTRACT_MODIFIER = "ABSTRACT_MODIFIER"
    OVERRIDE_MODIFIER = "OVERRIDE_MODIFIER"
    VIRTUAL_MODIFIER = "VIRTUAL_MODIFIER"

    VAR_DECLARE = "VAR_DECLARE"
    VAR_ASSIGN = "VAR_ASSIGN"
    MULTI_VAR_DECLARE = "MULTI_VAR_DECLARE"
    MULTI_VAR_ASSIGN = "MULTI_VAR_ASSIGN"

    COMPARISON = "COMPARISON"
    CONDITION = "CONDITION"
    EXPRESSION_BINARY = "EXPRESSION_BINARY"
    EXPRESSION_UNARY = "EXPRESSION_UNARY"

    NUMERIC_LITERAL = "NUMERIC_LITERAL"
    LIST_LITERAL = "LIST_LITERAL"
    MAP_LITERAL = "MAP_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    RAW_STRING_LITERAL = "RAW_STRING_LITERAL"
    F_STRING_LITERAL = "F_STRING_LITERAL"
    BOOL_LITERAL = "BOOL_LITERAL"
    NONE_LITERAL = "NONE_LITERAL"

    FUNC_PARAM = "FUNC_PARAM"
    FUNC_CALL_PARAM = "FUNC_CALL_PARAM"
    FUNCTION_DECL = "FUNCTION_DECL"
    FUNCTION_CALL = "FUNCTION_CALL"
    LAMBDA_EXPR = "LAMBDA_EXPR"
    RETURN = "RETURN"

    GENERIC_PARAM = "GENERIC_PARAM"
    CLASS_DEFINE = "CLASS_DEFINE"
    CLASS_INSTANTIATION = "CLASS_INSTANTIATION"
    CLASS_DIVIDER = "CLASS_DIVIDER"

    IF_EXPR = "IF_EXPR"
    TERNARY_EXPR = "TERNARY_EXPR"
    MATCH_EXPR = "MATCH_EXPR"

    WHILE_LOOP = "WHILE_LOOP"
    FOR_IN_LOOP = "FOR_IN_LOOP"
    C_STYLE_FOR_LOOP = "C_STYLE_FOR_LOOP"
    CONTINUE = "CONTINUE"
    BREAK = "BREAK"

    TRY_CATCH = "TRY_CATCH"
    THROW = "THROW"

# ==, <=, >=, !=, >, < operators
ConditionOperators: Set = {
    "==",   # Equal
    "<=",   # Less or Equal
    ">=",   # More or Equal
    "!=",   # Not Equal
    ">",    # Greater
    "<"     # Less
}

# Binary operators for arithmetic and bitwise operations
BinaryOperators: Set = {
    "+",    # Addition
    "-",    # Subtraction
    "*",    # Multiplication
    "/",    # Division
    "%",    # Modulus
    "**",   # Exponentiation
    "&",    # Bitwise AND
    "|",    # Bitwise OR
    "^",    # Bitwise XOR
    "<<",   # Left Shift
    ">>",    # Right Shift
    "&&",   # Logical AND
    "||",    # Logical OR
    "+=",  # Addition Assignment
    "-=",  # Subtraction Assignment
    "*=",  # Multiplication Assignment
    "/=",  # Division Assignment
    "%=",  # Modulus Assignment
    "**=",  # Exponentiation Assignment
    "&=",  # Bitwise AND Assignment
    "|=",  # Bitwise OR Assignment
    "^=",  # Bitwise XOR Assignment
    "<<=", # Left Shift Assignment
    ">>="  # Right Shift Assignment
}

UnaryOperators: Set = {
    "!",     # Logical NOT
    "-",     # Negation
    "+",     # Unary Plus
    "~"      # Bitwise NOT
}


# list[int] -> EspressoList<EspressoInt>
TYPE_MAP : Dict = {
    # Espresso | C++
    "byte": "EspressoByte", # 8-bit signed integer
    "short" : "EspressoShort", # 16-bit signed integer
    "int": "EspressoInt", # 32-bit signed integer
    "long": "EspressoLong", # 64-bit signed integer
    "dlong": "EspressoLongLong", # 128-bit signed integer

    "ubyte": "EspressoByte", # 8-bit unsigned integer
    "ushort" : "EspressoShort", # 16-bit unsigned integer
    "uint": "EspressoUInt", # 32-bit unsigned integer
    "ulong": "EspressoULong", # 64-bit unsigned integer
    "dulong": "EspressoULongLong", # 128-bit unsigned integer

    "float8": "EspressoFloat8", # 8-bit floating point
    "float16": "EspressoFloat16", # 16-bit floating point
    "float": "EspressoFloat", # 32-bit floating point
    "double": "EspressoDouble", # 64-bit floating point
    "decimal": "EspressoDecimal", # 128-bit floating point

    "bin" : "EspressoBits", # 32-bit binary
    "hex" : "EspressoBits", # 32-bit hexadecimal
    "oct" : "EspressoBits", # 32-bit octal

    "string": "EspressoString", # String type
    "bool": "bool", # Boolean type
    "void": "void", # Void type
    "any": "EspressoAny", # Any type
    "list": "EspressoList", # List type
    "collection": "EspressoCollection", # Collection type
    "map": "EspressoDict", # Dictionary type
    "set": "EspressoSet", # Set type
    "tuple": "EspressoTuple", # Tuple type
    "auto": "auto", # Auto type
    "union": "EspressoUnion" # Variant type
}

def ConvertType(espresso_type: str) -> str:
    s = espresso_type.strip()
    out = []
    word = ''
    stack = []

    def dump_word():
        nonlocal word
        if word:
            # Map base types, otherwise treat as custom class
            mapped = TYPE_MAP.get(word.strip(), word.strip())
            out.append(mapped)
            word = ''

    for c in s:
        if c == '[':
            dump_word()
            out.append('<')
            stack.append('[')
        elif c == ']':
            dump_word()
            out.append('>')
            if not stack or stack.pop() != '[':
                raise ValueError("Unmatched brackets")
        elif c == ',':
            dump_word()
            out.append(', ')
        elif c.isspace():
            dump_word()
        else:
            word += c

    dump_word()
    if stack:
        raise ValueError("Unmatched brackets")
    return ''.join(out)


# ==============================================
# Abstract Syntax Tree
# ==============================================

# Base AST Node
class _ASTNode(ABC):
    """Base class for all AST nodes.
    Attributes:
        node_type (NodeType): The type of the AST node.
        value (Optional[Any]): The value associated with the node, if any.
        body (Optional["Body"]): The body of the node, if applicable.
        modifiers (Optional[List[_Modifier]]): List of modifiers associated with the node.
    """
    def __init__(self, node_type: NodeType,
                value: Optional[Any] = None,
                body: Optional["Body"] = None,
                modifiers: Optional[List["_Modifier"]] = None):
    
        self.node_type: NodeType = node_type
        self.value: Optional[Any] = value
        self.body: Optional["Body"] = body
        self.modifiers: Optional[List["_Modifier"]] = modifiers if modifiers is not None else []

    def __hash__(self):
        return hash((self.node_type, self.value, tuple(self.modifiers), self.body))
    
    def __repr__(self):
        return f"{self.__class__.__name__}(type={self.node_type}, value={self.value}, body={self.body}, modifiers={self.modifiers})"
    
    def To_CXX(self) -> str:
        """Convert the AST node to its C++ code representation."""
        raise NotImplementedError("To_CXX method must be implemented in subclasses")

# Base class for all value-producing expressions (literals, variables, operations, etc.)
class _Value(_ASTNode, ABC):
    """Base class for all value-producing expressions (literals, variables, operations, etc.)"""
    pass

# Base class for all annotations (@namespace, @define, etc.)
class Annotation(_ASTNode):
    """Base class for annotations"""
    pass

# Base class for all modifiers (private, static, etc.)
class _Modifier(_ASTNode):
    """Base class for all `@` modifiers"""
    pass

# Base class for all condition types (comparisons, boolean operations, etc.)
class _Condition(_Value, _ASTNode):
    """Base class for all condition types"""
    pass

# Base class for all expression types (binary, unary, etc.)
class _Expression(_Value, _ASTNode):
    """Base class for all expression types"""
    pass

# Base class for all literal types (numeric, string, etc.)
class _Literal(_Value, _ASTNode):
    """Base class for all literal types (numeric, string, etc.)"""
    pass


# Blocks
class Body():
    def __init__(self, statements: List[_ASTNode], indent_level: int = 1):
        self.indent_level = indent_level
        self.children = statements if isinstance(statements, List) else statements.children if isinstance(statements, Body) else [] 

    def add_statement(self, statement: _ASTNode) -> None:
        """Add a statement to the body."""
        self.children.append(statement)

    def To_CXX(self) -> str:
        indent = "    " * self.indent_level
        lines = []
        for stmt in self.children:
            if hasattr(stmt, 'To_CXX'):
                content = stmt.To_CXX()
                # Add semicolon for expression statements
                if isinstance(stmt, (_Value, FunctionCall)) and not content.endswith(';'):
                    content += ';'
            else:
                content = str(stmt)
            stmt_lines = content.split('\n')
            lines.extend(f"{indent}{line}" for line in stmt_lines)
        return '\n'.join(lines)

# Newline Node
class NewLine(_ASTNode):
    """Represents a newline in the source code."""
    def __init__(self):
        super().__init__(NodeType.NEWLINE, value="\n")

    def To_CXX(self) -> str:
        return "\n"


# ==============================================
# Meta Modifier Classes
# ==============================================


class IsPrivateModifier(_Modifier):
    """Private Modifier"""
    def __init__(self):
        super().__init__(NodeType.PRIVATE_MODIFIER)

class IsPublicModifier(_Modifier):
    """Private Modifier"""
    def __init__(self):
        super().__init__(NodeType.PUBLIC_MODIFIER)

class IsProtectedModifier(_Modifier):
    """Private Modifier"""
    def __init__(self):
        super().__init__(NodeType.PROTECTED_MODIFIER)

class IsConstModifier(_Modifier):
    """Const/immutable modifier"""
    def __init__(self):
        super().__init__(NodeType.CONST_MODIFIER)

class IsConstexprModifier(_Modifier):
    """Const/immutable modifier"""
    def __init__(self):
        super().__init__(NodeType.CONSTEXPR_MODIFIER)

class IsConstevalModifier(_Modifier):
    """Const/immutable modifier"""
    def __init__(self):
        super().__init__(NodeType.CONSTEVAL_MODIFIER)

class IsStaticModifier(_Modifier):
    """Static/class-level modifier"""
    def __init__(self):
        super().__init__(NodeType.STATIC_MODIFIER)

class IsAbstractModifier(_Modifier):
    """Abstract class/method modifier"""
    def __init__(self):
        super().__init__(NodeType.ABSTRACT_MODIFIER)

class IsOverrideModifier(_Modifier):
    """Override class/method modifier"""
    def __init__(self):
        super().__init__(NodeType.OVERRIDE_MODIFIER)

class IsVirtualModifier(_Modifier):
    """Virtual class/method modifier"""
    def __init__(self):
        super().__init__(NodeType.VIRTUAL_MODIFIER)


MOD_MAP: Dict = {
    IsPrivateModifier: "private",
    IsPublicModifier: "public",
    IsProtectedModifier: "protected",
    IsConstModifier: "const",
    IsStaticModifier: "static",
    IsAbstractModifier: "abstract",
    IsOverrideModifier: "override",
    IsVirtualModifier: "virtual"
}

def ConvertModifier(modifier: _Modifier) -> str:
    """Convert a modifier to its C++ string representation."""
    if type(modifier) in MOD_MAP:
        return MOD_MAP[type(modifier)]
    raise ValueError(f"Unknown modifier type: {type(modifier)}")

# ==============================================
# Basic Syntax Nodes
# ==============================================

# Variable name
class Identifier(_Value, _ASTNode):
    """Represents an identifier in the source code."""
    def __init__(self, value: str):
        super().__init__(NodeType.IDENTIFIER, value=value)

    def To_CXX(self) -> str:
        return str(self.value).strip()

# Condition Nodes (==, <=, >=, !=, >, <)
class Comparison(_Condition):
    """Represents comparison operations (==, <=, >=, etc.)"""
    def __init__(self, left: _ASTNode, op: str, right: _ASTNode):
        if op not in ConditionOperators:
            raise ValueError(f"Invalid comparison operator: {op}")
        super().__init__(NodeType.COMPARISON)
        self.left = left
        self.op = op
        self.right = right

    def To_CXX(self) -> str:
        return f"{self.left.To_CXX()} {self.op} {self.right.To_CXX()}".strip()

# Boolean Condition Nodes (and, or, not)
class BooleanCondition(_Condition):
    """Represents boolean operations (and, or, not)"""
    def __init__(self, op: str, operands: List[_ASTNode]):
        super().__init__(NodeType.CONDITION)
        self.op = op.lower()  # 'and', 'or', 'not'
        self.operands = operands

    def To_CXX(self) -> str:
        if self.op == 'not':
            if len(self.operands) != 1:
                raise ValueError("'not' operator requires exactly one operand")
            return f"!({self.operands[0].To_CXX()})"
        
        cxx_op = '&&' if self.op == 'and' else '||'
        return f" {cxx_op} ".join(op.To_CXX() for op in self.operands).strip()

# Binary Expression Nodes (arithmetic, bitwise)
class BinaryExpression(_Expression):
    """Represents binary operations (+, -, *, /, %, **, &, |, ^, <<, >>)"""
    def __init__(self, left: _ASTNode, op: str, right: _ASTNode):
        if op not in BinaryOperators:
            raise ValueError(f"Invalid binary operator: {op}")
        super().__init__(NodeType.EXPRESSION_BINARY)
        self.left = left
        self.op = op
        self.right = right

    def To_CXX(self) -> str:
        return f"{self.left.To_CXX()} {self.op} {self.right.To_CXX()}".strip()

# Unary Expression Nodes (unary operations like !, -, +, ~)
class UnaryExpression(_Expression):
    """Represents unary operations (!, -, +, ~)"""
    def __init__(self, op: str, operand: _ASTNode):
        super().__init__(NodeType.EXPRESSION_UNARY)
        self.op = op
        self.operand = operand

    def To_CXX(self) -> str:
        # Handle special case for 'not' which we map to '!'
        op = '!' if self.op == 'not' else self.op
        return f"{op}{self.operand.To_CXX()}".strip()

# `int x` -> `EspressoInt x;`
class VarDeclare(_ASTNode):
    def __init__(self, 
                 var_name: Identifier,
                 var_type: Identifier,
                 modifiers: List[_Modifier] = []):
        super().__init__(NodeType.VAR_DECLARE, modifiers=modifiers)
        self.var_name = var_name
        self.var_type = var_type

    def To_CXX(self) -> str:
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) if self.modifiers else ""
        type_str = ConvertType(self.var_type.To_CXX())
        return f"{mods} {type_str} {self.var_name.To_CXX()};".strip()

# `int x = 5` -> `EspressoInt x = 5;`
class VarAssign(_ASTNode):
    def __init__(self, 
                 var_name: Identifier,
                 value: _Value,  # Now explicitly requires a Value node
                 var_type: Identifier,
                 modifiers: List[_Modifier] = []):
        super().__init__(NodeType.VAR_ASSIGN, modifiers=modifiers)
        self.var_name = var_name
        self.value = value  # Guaranteed to be a Value node
        self.var_type = var_type

    def To_CXX(self) -> str:
        type_str = f"{ConvertType(self.var_type.To_CXX())} " if self.var_type else ""
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) if self.modifiers else ""
        return f"{mods}{type_str} {self.var_name.To_CXX()} = {self.value.To_CXX()};".strip()

# `float xpos, ypos` -> `EspressoFloat xpos, ypos;`
class MultiVarDeclare(_ASTNode):
    """Represents multiple variable declarations in a single statement."""
    def __init__(self,
                var_names: List[Identifier], 
                var_type: Identifier, 
                modifiers: List[_Modifier] = []):
        super().__init__(NodeType.MULTI_VAR_DECLARE, modifiers=modifiers)
        self.var_names = [var_name for var_name in var_names]
        self.var_type = var_type 

    def To_CXX(self) -> str:
        mods = ' '.join(ConvertModifier(m) for m in self.modifiers) if self.modifiers else ""
        type_str = ConvertType(self.var_type.To_CXX())
        names_str = ', '.join(var.To_CXX() for var in self.var_names)
        return f"{mods}{type_str} {names_str};".strip()
    
# `float xpos, ypos = 0.0` -> `EspressoFloat xpos = 0.0, ypos = 0.0;`
class MultiVarAssign(_ASTNode):
    """Represents multiple variable declarations in a single statement."""
    def __init__(self,
                var_names: List[Identifier],
                value: _Value,  # Now explicitly requires a Value node
                var_type: Identifier, 
                modifiers: List[_Modifier] = []):
        super().__init__(NodeType.MULTI_VAR_DECLARE, modifiers=modifiers)
        self.var_names = [var_name if isinstance(var_name, Identifier) else Identifier(var_name) for var_name in var_names]
        self.var_type = var_type if isinstance(var_type, Identifier) else Identifier(var_type)
        self.value = value

    def To_CXX(self) -> str:
        mods = ' '.join(ConvertModifier(m) for m in self.modifiers) if self.modifiers else ""
        type_str = ConvertType(self.var_type.To_CXX())
        names_str = ', '.join(var.To_CXX() for var in self.var_names)
        return f"{mods}{type_str} {names_str} = {self.value};".strip()


# ==============================================
# Literals
# ==============================================

class NumericLiteral(_Literal):
    """Minimal numeric literal that passes through with C++ suffixes"""
    def __init__(self, value: str):
        super().__init__(NodeType.NUMERIC_LITERAL)
        self.raw_value = value.strip()

    def To_CXX(self) -> str:
        """Pass through with underscores removed"""
        return self.raw_value.replace('_', '')

class ItemContainerLiteral(_Literal):
    """Base class for list/set/tuple literals using uniform {} syntax"""
    def __init__(self, items: List[_ASTNode], delims : str = "{}"):
        assert delims in ["()", "{}"], f"Unknown demlimiter {delims}"
        super().__init__(NodeType.LIST_LITERAL)  # We'll reuse this node type
        self.items = items
        self.delims = delims

    def To_CXX(self) -> str:
        items_str = ", ".join(item.To_CXX() for item in self.items)
        return f"{self.delims[0]}{items_str}{self.delims[1]}"

class KVContainerLiteral(_Literal):
    """Base class for map literals using {{key, value}} syntax"""
    def __init__(self, pairs: List[Tuple[_ASTNode, _ASTNode]]):
        super().__init__(NodeType.MAP_LITERAL)  # We'll reuse this node type
        self.pairs = pairs

    def To_CXX(self) -> str:
        pairs_str = ", ".join(
            f"{{{key.To_CXX()}, {value.To_CXX()}}}"
            for key, value in self.pairs
        )
        return f"{{{pairs_str}}}"

class NormalStringLiteral(_Literal):
    """Regular string literal with escape sequences"""
    def __init__(self, value: str):
        super().__init__(NodeType.STRING_LITERAL, value)

    def To_CXX(self) -> str:
        # Remove the repr() and just escape the string
        escaped = (self.value
                .replace('\\', '\\\\')
                .replace('"', '\\"')
                .replace('\n', '\\n')
                .replace('\t', '\\t'))
        return f'"{escaped}"'  # Keep as C++ string literal

class RawStringLiteral(_Literal):
    """Raw string literal (no escape processing)"""
    def __init__(self, value: str):
        super().__init__(NodeType.RAW_STRING_LITERAL, value)

    def To_CXX(self) -> str:
        return f'R"({self.value})"'

class InterpolatedStringLiteral(_Literal):
    """F-string style interpolated string with ${var} or {expr} syntax"""
    def __init__(self, template: Union[str, List[Union[str, _ASTNode]]]):
        super().__init__(NodeType.F_STRING_LITERAL, value=template if isinstance(template, str) else "")
        
        if isinstance(template, str):
            self.parts = self._parse_template(template)
        else:
            self.parts = template

    def _parse_template(self, template: str) -> List[Union[str, _ASTNode]]:
        parts = []
        current = ""
        i = 0
        while i < len(template):
            if template[i] == '$' and i + 1 < len(template) and template[i + 1] == '{':
                if current:
                    parts.append(current)
                    current = ""
                # Find matching }
                start = i + 2
                count = 1
                j = start
                while j < len(template) and count > 0:
                    if template[j] == '{': count += 1
                    if template[j] == '}': count -= 1
                    j += 1
                if count == 0:
                    expr = template[start:j-1]
                    parts.append(Identifier(expr))
                i = j
            elif template[i] == '{':
                if current:
                    parts.append(current)
                    current = ""
                # Find matching }
                start = i + 1
                count = 1
                j = start
                while j < len(template) and count > 0:
                    if template[j] == '{': count += 1
                    if template[j] == '}': count -= 1
                    j += 1
                if count == 0:
                    expr = template[start:j-1]
                    parts.append(Identifier(expr))
                i = j
            else:
                current += template[i]
                i += 1
        if current:
            parts.append(current)
        return parts

    def To_CXX(self) -> str:
        format_parts = []
        args = []
        for i, part in enumerate(self.parts):
            if isinstance(part, str):
                # Escape curly braces in literal parts
                format_parts.append(part.replace('{', '{{').replace('}', '}}'))
            else:
                format_parts.append(f'{{{i}}}')
                args.append(part.To_CXX())
        return f'fmt::format("{"".join(format_parts)}", {", ".join(args)})'

class BoolLiteral(_Literal):
    """Boolean literal (true/false)"""
    def __init__(self, value: bool):
        super().__init__(NodeType.BOOL_LITERAL)
        self.value = value

    def To_CXX(self) -> str:
        return "true" if self.value else "false"

class VoidLiteral(_Literal):
    """Void literal (no value)"""
    def __init__(self):
        super().__init__(NodeType.NONE_LITERAL)

    def To_CXX(self) -> str:
        return "void"

# ==============================================
# POP
# ==============================================



class FuncDeclParam(_ASTNode):
    """Represents a single parameter in function declaration with default value"""
    def __init__(self, 
                 name: Identifier,
                 param_type: Identifier,
                 default: Optional[_ASTNode] = None):
        super().__init__(NodeType.FUNC_PARAM)
        self.name = name if isinstance(name, Identifier) else Identifier(name)
        self.param_type = param_type if isinstance(param_type, Identifier) else Identifier(param_type)
        self.default = default

    def To_CXX(self) -> str:
        type_str = ConvertType(self.param_type.To_CXX())
        default_str = f" = {self.default.To_CXX()}" if self.default else ""
        return f"{type_str} {self.name.To_CXX()}{default_str}"

class FuncCallParam(_ASTNode):
    """Represents a function call parameter (both named and positional)"""
    def __init__(self, 
                 value: _ASTNode,
                 name: Optional[Identifier] = None):
        super().__init__(NodeType.FUNC_CALL_PARAM)
        self.value = value
        self.name = name if isinstance(name, Identifier) else Identifier(name) if name else None

    def To_CXX(self) -> str:
        if self.name:
            return f".{self.name.To_CXX()}={self.value.To_CXX()}"
        return self.value.To_CXX()

class FunctionCall(_Value, _ASTNode):
    def __init__(self, 
                 target: Identifier,
                 params: List[FuncCallParam]):
        super().__init__(NodeType.FUNCTION_CALL)
        self.target = target if isinstance(target, _ASTNode) else Identifier(target)
        self.params = params

    def To_CXX(self) -> str:
        # All function calls use the parameter struct
        args = []
        for i, param in enumerate(self.params):
            if param.name:
                args.append(f"_{param.name.To_CXX()}={param.value.To_CXX()}")
            else:
                args.append(f"{param.value.To_CXX()}")
        
        return f"{self.target.To_CXX()}({{{', '.join(args)}}})"

class FunctionDecl(_ASTNode):
    def __init__(self, 
                 name: Identifier,
                 return_type: Identifier,
                 params: List[FuncDeclParam],
                 body: Body = Body([]),
                 modifiers: List[_Modifier] = []):
        super().__init__(NodeType.FUNCTION_DECL, body=body)
        self.name = name if isinstance(name, Identifier) else Identifier(name)
        self.return_type = return_type if isinstance(return_type, Identifier) else Identifier(return_type)
        self.params = params
        self.modifiers = modifiers or []

    def To_CXX(self) -> str:
        # Always generate both traditional and named versions
        traditional = self._generate_traditional()
        named = self._generate_named()
        # Add this check to skip empty parameter structs
        if not self.params:
            return traditional  # Skip named version for parameter-less functions
        return f"{traditional}\n\n{named}"

    def _generate_traditional(self) -> str:
        """Generate traditional C++ function"""
        param_list = ', '.join(p.To_CXX() for p in self.params)
        mods = ' '.join(ConvertModifier(m) for m in self.modifiers) if self.modifiers else ""
        body = self.body.To_CXX()
        return f"{mods}{ConvertType(self.return_type.To_CXX())} {self.name.To_CXX()}({param_list}) {{\n{body}\n}}"

    def _generate_named(self) -> str:
        # 1. Generate parameter struct
        struct_name = f"{self.name.To_CXX()}_Params"
        struct_members = []
        for param in self.params:
            member = f"{ConvertType(param.param_type.To_CXX())} _{param.name.To_CXX()};"
            struct_members.append(member)
        
        struct_def = f"struct {struct_name} {{'\n' + Body(struct_members, 1).To_CXX() + '\n'}};\n\n"

        # 2. Generate function with struct parameter
        mods = ' '.join(ConvertModifier(m) for m in self.modifiers) if self.modifiers else ""
        fn_def = f"{mods}{ConvertType(self.return_type.To_CXX())} {self.name.To_CXX()}({struct_name} params) {{\n"
        
        # 3. Unpack parameters at start of function
        param_unpacking = [
            f"{ConvertType(p.param_type.To_CXX())} {p.name.To_CXX()} = params._{p.name.To_CXX()};"
            for p in self.params
        ]
        
        # 4. Add function body with proper indentation
        # Ensure all elements are _ASTNode instances
        full_body = []
        for stmt in param_unpacking:
            if isinstance(stmt, _ASTNode):
                full_body.append(stmt)
            else:
                # Wrap string statements in a dummy node
                class _RawStatement(_ASTNode):
                    def __init__(self, code: str):
                        super().__init__(NodeType.BODY)
                        self.code = code
                    def To_CXX(self) -> str:
                        return self.code
                full_body.append(_RawStatement(stmt))
        full_body.extend(self.body.children)
        fn_def += Body(full_body, 1).To_CXX() + "\n}"
        
        return struct_def + fn_def   

class LambdaExpr(_Value, _ASTNode):
    def __init__(self, 
                 params: List[Tuple[Identifier, 
                                   Identifier]],
                 body: Body,
                 return_type: Identifier = "",
                 capture: str = "[]"):
        super().__init__(NodeType.LAMBDA_EXPR, body=body)
        self.params = [(name if isinstance(name, Identifier) else Identifier(str(name)),
                        type_ if isinstance(type_, Identifier) else Identifier(str(type_))) for name, type_ in params]
        self.return_type = return_type if isinstance(return_type, Identifier) else Identifier(return_type)
        self.capture = capture 

    def To_CXX(self) -> str:
        params_str = ', '.join(
            f"{ConvertType(type_.To_CXX())} {name.To_CXX()}"
            for name, type_ in self.params
        )
        return_str = f" -> {ConvertType(self.return_type.To_CXX())}" if self.return_type else ""
        body_str = self.body.To_CXX()
        return f"[{self.capture}]({params_str}){return_str} {{\n{body_str}\n}}"

class Return(_ASTNode):
    def __init__(self, value: Optional["_Value"]):  # None for void returns
        super().__init__(NodeType.RETURN, value=value if value else None)

    def To_CXX(self):
        return f"return {self.value.To_CXX()};" if self.value else "return;"

# ==============================================
# OOP
# ==============================================

class GenericParam(_ASTNode):
    """Represents a template parameter (type or non-type)"""
    def __init__(self, 
                 name: Identifier, 
                 param_type: Optional[Identifier] = None,
                 default: Optional[_ASTNode] = None,
                 is_type: bool = True):
        super().__init__(NodeType.GENERIC_PARAM)
        self.name = name if isinstance(name, Identifier) else Identifier(name)
        self.param_type = param_type
        self.default = default
        self.is_type = is_type

    def To_CXX(self) -> str:
        if self.is_type:
            decl = f"typename {self.name.To_CXX()}"
        else:
            type_str = self.param_type.To_CXX() if isinstance(self.param_type, _ASTNode) else self.param_type
            decl = f"{type_str} {self.name.To_CXX()}"
        
        if self.default:
            decl += f" = {self.default.To_CXX()}"
        return decl

class ClassNode(_ASTNode):
    def __init__(self,
                name: Identifier,
                body: Body = Body([]),
                generic_params: List["GenericParam"] = [],
                parents: List[Union[str, "Identifier"]] = [], 
                modifiers: List["_Modifier"] = []):
        super().__init__(NodeType.CLASS_DEFINE, body=body)
        self.name = name if isinstance(name, Identifier) else Identifier(name)
        self.generic_params = generic_params or []
        self.parents = [p if isinstance(p, (Identifier, _ASTNode)) else Identifier(p) for p in (parents or [])]
        self.modifiers = modifiers or []

        names = [p.name.To_CXX() for p in generic_params]
        assert len(names) == len(set(names)), "Duplicate generic parameter names"

    def To_CXX(self) -> str:
        body_content = self.body.To_CXX()
        return (
            self._template() +
            " ".join(ConvertModifier(m) for m in self.modifiers) if self.modifiers else "" +
            f"class {self.name.To_CXX()}{self._parents()} {{\n{body_content}\n}};"
        )

    def _template(self):
        return f"template<{', '.join(p.To_CXX() for p in self.generic_params)}>\n" if self.generic_params else ""

    def _parents(self):
        if not self.parents: return ""
        return " : public " + ", ".join(p.To_CXX() if isinstance(p, _ASTNode) else str(p) for p in self.parents)

class ClassInstantiation(_Value, _ASTNode):
    """Represents creating a new class instance (constructor call)"""
    def __init__(self,
                 class_name: Identifier,
                 generic_args: List[Union[str, Identifier, _ASTNode]] = [],
                 constructor_args: List[Union[_ASTNode, FuncCallParam]] = []):
        super().__init__(NodeType.CLASS_INSTANTIATION)
        self.class_name = class_name if isinstance(class_name, Identifier) else Identifier(class_name)
        self.generic_args = generic_args or []
        self.constructor_args = constructor_args or []

    def To_CXX(self) -> str:
        generic_str = ''
        if self.generic_args:
            generic_str = f"<{', '.join(a.To_CXX() if isinstance(a, _ASTNode) else str(a) for a in self.generic_args)}>"
        
        args_str = ''
        if self.constructor_args:
            if any(isinstance(a, FuncCallParam) for a in self.constructor_args):
                args_str = "{" + ", ".join(a.To_CXX() for a in self.constructor_args) + "}"
            else:
                args_str = ", ".join(a.To_CXX() for a in self.constructor_args)
        
        return f"{self.class_name.To_CXX()}{generic_str}({args_str})"

class ClassDivider(_ASTNode):
    """Divides class body into sections based on access modifiers"""
    def __init__(self, 
                 access: Literal["public", "protected", "private"],
                 body: Body):
        super().__init__(NodeType.CLASS_DIVIDER, body=body)
        self.access = access.lower()  # Normalize to lowercase
        self.body.indent_level = 0 # Ensure body has no extra indentation

    def To_CXX(self) -> str:
        return f"{self.access.lower()}:\n{self.body.To_CXX()}" if self.body else ""

# ==============================================
# Control Flow Structures
# ==============================================

class IfExpr(_ASTNode):
    def __init__(self, condition: _ASTNode, 
                 body: Body,
                 elifs: List[Tuple[_ASTNode, Body]] = [],
                 else_body: Body = []):
        super().__init__(NodeType.IF_EXPR, body=body)
        self.condition = condition
        self.elifs = [(pattern, elseif if isinstance(elseif, list) else Body(elseif.children, 1)) for pattern, elseif in elifs]
        self.else_body = else_body if isinstance(else_body, Body) else Body(else_body or [], 1)

    def To_CXX(self) -> str:
        result = f"if ({self.condition.To_CXX()}) {{\n{self.body.To_CXX()}\n}}"
        
        for cond, body in self.elifs:
            if isinstance(body, Body):
                body_cxx = body.To_CXX()
            else:
                body_cxx = Body(body if isinstance(body, list) else body.children, 1).To_CXX()
            result += f" else if ({cond.To_CXX()}) {{\n{body_cxx}\n}}"
            
        if self.else_body:
            result += f" else {{\n{self.else_body.To_CXX()}\n}}"
            
        return result

class TernaryExpr(_Value, _ASTNode):
    def __init__(self, condition: _ASTNode, 
                 true_expr: _ASTNode, 
                 false_expr: _ASTNode):
        super().__init__(NodeType.TERNARY_EXPR)
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr

    def To_CXX(self) -> str:
        return f"{self.condition.To_CXX()} ? {self.true_expr.To_CXX()} : {self.false_expr.To_CXX()}"

class MatchExpr(_ASTNode):
    def __init__(self, value: _ASTNode, arms: List[Tuple[_ASTNode, Body]], else_body: Body = []):
        super().__init__(NodeType.MATCH_EXPR)
        self.value = value
        self.arms = [(pattern if isinstance(pattern, _ASTNode) else Identifier(str(pattern)),
                     body if isinstance(body, Body) else Body(body or [], 1)) for pattern, body in arms]
        self.else_body = else_body if isinstance(else_body, Body) else Body(else_body or [], 1) if else_body else None

    def To_CXX(self) -> str:
        val = self.value.To_CXX()
        code = ""
        for i, (pattern, body) in enumerate(self.arms):
            cond = f"{val} == {pattern.To_CXX()}"
            if i == 0:
                code += f"if ({cond}) {{\n{body.To_CXX()}\n}}"
            else:
                code += f" else if ({cond}) {{\n{body.To_CXX()}\n}}"
        if self.else_body:
            code += f" else {{\n{self.else_body.To_CXX()}\n}}"
        return code


# ==============================================
# Loops
# ==============================================

class WhileLoop(_ASTNode):
    def __init__(self, condition: _ASTNode, body: Body):
        super().__init__(NodeType.WHILE_LOOP, body=body)
        self.condition = condition

    def To_CXX(self) -> str:
        return f"while ({self.condition.To_CXX()}) {{\n{self.body.To_CXX()}\n}}"

class ForInLoop(_ASTNode):
    def __init__(self, var_name: Identifier,
                 iterable: _ASTNode,
                 body: Body):
        super().__init__(NodeType.FOR_IN_LOOP, body=body)
        self.var_name = var_name if isinstance(var_name, Identifier) else Identifier(var_name)
        self.iterable = iterable

    def To_CXX(self) -> str:
        return f"for (auto&& {self.var_name.To_CXX()} : {self.iterable.To_CXX()}) {{\n{self.body.To_CXX()}\n}}"

class CStyleForLoop(_ASTNode):
    def __init__(self, init: _ASTNode,
                 condition: _ASTNode,
                 update: _ASTNode,
                 body: Body):
        super().__init__(NodeType.C_STYLE_FOR_LOOP, body=body)
        self.init = init
        self.condition = condition
        self.update = update

    def To_CXX(self) -> str:
        return (f"for ({self.init.To_CXX()}; {self.condition.To_CXX()}; {self.update.To_CXX()}) "
                f"{{\n{self.body.To_CXX()}\n}}")

class Break(_ASTNode):
    def __init__(self):
        super().__init__(NodeType.BREAK)

    def To_CXX(self) -> str:
        return "break;"

class Continue(_ASTNode):
    def __init__(self):
        super().__init__(NodeType.CONTINUE)

    def To_CXX(self) -> str:
        return "continue;"

# ==============================================
# Exception Handling
# ==============================================

class TryCatch(_ASTNode):
    def __init__(self, try_body: Body, 
                 catch_blocks: List[Tuple[Identifier, Body]],
                 finally_body: Optional[Body] = []):
        super().__init__(NodeType.TRY_CATCH, body=try_body)
        self.try_body = try_body
        self.catch_blocks = [(exception_type if isinstance(exception_type, Identifier) else Identifier(str(exception_type)), body if isinstance(body, Body) else Body(body or [], 1)) 
                            for exception_type, body in catch_blocks]
        self.finally_body = finally_body if isinstance(finally_body, Body) else Body(finally_body or [], 1) if finally_body else None

    def To_CXX(self) -> str:
        try_block = f"try {{\n{self.body.To_CXX()}\n}}"
        
        catch_blocks_str = ""
        for exc_type, body in self.catch_blocks:
            catch_blocks_str += f" catch ({ConvertType(exc_type.To_CXX())} e) {{\n{body.To_CXX()}\n}}"
        
        finally_block = ""
        if self.finally_body:
            finally_block = f" finally {{\n{self.finally_body.To_CXX()}\n}}"
        
        return try_block + catch_blocks_str + finally_block

class Throw(_ASTNode):
    def __init__(self, exception: _ASTNode):
        super().__init__(NodeType.THROW)
        self.exception = exception

    def To_CXX(self) -> str:
        return f"throw {self.exception.To_CXX()};"



"""
try use ASTL to make nodes from this espresso code
class Vector:
    float x, y

    public:
    func Vector(float x=0, float y=0):
        this.x = x
        this.y = y
    
    float func magnitude():
        return float(sqrt(this.x**2 + this.y**2))
    
    Vector func operator+ (Vector other):
        return Vector(this.x + other.x, this.y + other.y)
    
    string ToString():
        return f"Vector(${this.x}, ${this.y})"

int func CalcFactorial(n):
    if not isinstance(n, int) or n < 0:
        raise ValueError("Input must be non-negative integer")
    return 1 if n <= 1 else n * CalcFactorial(n - 1)

string func RiskyOperation():
    if random::Random() > 0.5:
        raise RuntimeError("Random failure!")
    return "Success"

int func Main():
    // Test classes and operators
    Vector v1 = Vector(3, 4)
    Vector v2 = Vector(2, 5)
    print(f"Vector sum: {v1 + v2}")
    print(f"Magnitude: {v1.magnitude():.2f}")
    
    // Test recursion and error handling
    try:
        print(f"Factorial of 5: ${CalcFactorial(5)}")
        print(f"Factorial of -1: ${CalcFactorial(-1)}")
    catch ValueError:
        print(f"Error: {ValueError::what()}")
    
    // Test random exceptions
    for int i = 0; i < 5; i+=1:
        try:
            print(risky_operation())
        catch RuntimeError:
            print(f"Caught exception: ${RuntimeError::what()}")
"""

# Vector class definition
vector_class = ClassNode(
    name="Vector",
    body=Body([
        # Private fields
        MultiVarDeclare(
            var_names=[Identifier("x"), Identifier("y")],
            var_type=Identifier("float")
        ),
        
        # Public section
        ClassDivider(
            access="public",
            body=Body([
                # Constructor
                FunctionDecl(
                    name="Vector",
                    return_type=Identifier("void"),
                    params=[
                        FuncDeclParam(
                            name=Identifier("x"),
                            param_type=Identifier("float"),
                            default=NumericLiteral("0")
                        ),
                        FuncDeclParam(
                            name=Identifier("y"),
                            param_type=Identifier("float"),
                            default=NumericLiteral("0")
                        )
                    ],
                    body=Body([
                        VarAssign(
                            var_name=Identifier("this.x"),
                            value=Identifier("x"),
                            var_type=None
                        ),
                        VarAssign(
                            var_name=Identifier("this.y"),
                            value=Identifier("y"),
                            var_type=None
                        )
                    ])
                ),
                
                # magnitude() method
                FunctionDecl(
                    name= Identifier("magnitude"),
                    return_type=Identifier("float"),
                    params=[],
                    body=Body([
                        Return(
                            FunctionCall(
                                target="float",
                                params=[
                                    FuncCallParam(
                                        FunctionCall(
                                            target="math::sqrt",
                                            params=[
                                                FuncCallParam(
                                                    value=BinaryExpression(
                                                        left=BinaryExpression(
                                                            left=Identifier("this.x"),
                                                            op="**",
                                                            right=NumericLiteral("2")
                                                        ),
                                                        op="+",
                                                        right=BinaryExpression(
                                                            left=Identifier("this.y"),
                                                            op="**",
                                                            right=NumericLiteral("2")
                                                        )
                                                    )     
                                                )
                                            ]
                                        )
                                    )
                                ]
                            )
                        )
                    ])
                ),
                
                # operator+ method
                FunctionDecl(
                    name=Identifier("operator+"),
                    return_type=Identifier("Vector"),
                    params=[
                        FuncDeclParam(
                            name=Identifier("other"),
                            param_type=Identifier("Vector")
                        )
                    ],
                    body=Body([
                        Return(
                            FunctionCall(
                                target="Vector",
                                params=[
                                    FuncCallParam(
                                        BinaryExpression(
                                            left=Identifier("this.x"),
                                            op="+",
                                            right=Identifier("other.x")
                                        )
                                    ),
                                    FuncCallParam(
                                        BinaryExpression(
                                            left=Identifier("this.y"),
                                            op="+",
                                            right=Identifier("other.y")
                                        )
                                    )
                                ]
                            )
                        )
                    ])
                ),
                
                # ToString() method
                FunctionDecl(
                    name=Identifier("ToString"),
                    return_type=Identifier("string"),
                    params=[],
                    body=Body([
                        Return(
                            InterpolatedStringLiteral(
                                template='Vector(${this.x}, ${this.y})'
                            )
                        )
                    ])
                )
            ])
        )
    ])
)

# CalcFactorial function
calc_factorial = FunctionDecl(
    name="CalcFactorial",
    return_type=Identifier("int"),
    params=[
        FuncDeclParam(
            name=Identifier("n"),
            param_type=Identifier("int")
        )
    ],
    body=Body([
        IfExpr(
            condition=BooleanCondition(
                op="or",
                operands=[
                    UnaryExpression(
                        op="not",
                        operand=FunctionCall(
                            target="isinstance",
                            params=[
                                FuncCallParam(Identifier("n")),
                                FuncCallParam(Identifier("int"))
                            ]
                        )
                    ),
                    Comparison(
                        left=Identifier("n"),
                        op="<",
                        right=NumericLiteral("0")
                    )
                ]
            ),
            body=Body([
                Throw(
                    FunctionCall(
                        target="ValueError",
                        params=[
                            FuncCallParam(
                                NormalStringLiteral("Input must be non-negative integer")
                            )
                        ]
                    )
                )
            ]),
            else_body=Body([
                Return(
                    TernaryExpr(
                        condition=Comparison(
                            left=Identifier("n"),
                            op="<=",
                            right=NumericLiteral("1")
                        ),
                        true_expr=NumericLiteral("1"),
                        false_expr=BinaryExpression(
                            left=Identifier("n"),
                            op="*",
                            right=FunctionCall(
                                target="CalcFactorial",
                                params=[
                                    FuncCallParam(
                                        BinaryExpression(
                                            left=Identifier("n"),
                                            op="-",
                                            right=NumericLiteral("1")
                                        )
                                    )
                                ]
                            )
                        )
                    )
                )
            ])
        )
    ])
)

# RiskyOperation function
risky_operation = FunctionDecl(
    name="RiskyOperation",
    return_type=Identifier("string"),
    params=[],
    body=Body([
        IfExpr(
            condition=Comparison(
                left=FunctionCall(
                    target="random::Random",
                    params=[]
                ),
                op=">",
                right=NumericLiteral("0.5")
            ),
            body=Body([
                Throw(
                    FunctionCall(
                        target="RuntimeError",
                        params=[
                            FuncCallParam(
                                NormalStringLiteral("Random failure!")
                            )
                        ]
                    )
                )
            ]),
            else_body=Body([
                Return(
                    NormalStringLiteral("Success")
                )
            ])
        )
    ])
)

# Main function
main_function = FunctionDecl(
    name=Identifier("Main"),
    return_type=Identifier("int"),
    params=[],
    body=Body([
        # Vector tests
        VarAssign(
            var_name=Identifier("v1"),
            value=FunctionCall(
                target="Vector",
                params=[
                    FuncCallParam(NumericLiteral("3")),
                    FuncCallParam(NumericLiteral("4"))
                ]
            ),
            var_type=Identifier("Vector")
        ),
        VarAssign(
            var_name=Identifier("v2"),
            value=FunctionCall(
                target="Vector",
                params=[
                    FuncCallParam(NumericLiteral("2")),
                    FuncCallParam(NumericLiteral("5"))
                ]
            ),
            var_type=Identifier("Vector")
        ),
        FunctionCall(
            target="print",
            params=[
                FuncCallParam(
                    InterpolatedStringLiteral(
                        template='Vector sum: ${v1 + v2}'
                    )
                )
            ]
        ),
        FunctionCall(
            target=Identifier("print"),
            params=[
                FuncCallParam(
                    InterpolatedStringLiteral(
                        template='Magnitude: ${v1.magnitude():.2f}'
                    )
                )
            ]
        ),
        
        # Factorial tests
        TryCatch(
            try_body=Body([
                FunctionCall(
                    target="print",
                    params=[
                        FuncCallParam(
                            InterpolatedStringLiteral(
                                template='Factorial of 5: ${CalcFactorial(5)}'
                            )
                        )
                    ]
                ),
                FunctionCall(
                    target="print",
                    params=[
                        FuncCallParam(
                            InterpolatedStringLiteral(
                                template='Factorial of -1: ${CalcFactorial(-1)}'
                            )
                        )
                    ]
                )
            ]),
            catch_blocks=[
                (Identifier("ValueError"), Body([
                    FunctionCall(
                        target="print",
                        params=[
                            FuncCallParam(
                                InterpolatedStringLiteral(
                                    template='Error: ${ValueError::what()}'
                                )
                            )
                        ]
                    )
                ]))
            ]
        ),
        
        # Random exception tests
        CStyleForLoop(
            init=VarAssign(
                var_name=Identifier("i"),
                value=NumericLiteral("0"),
                var_type=Identifier("int")
            ),
            condition=Comparison(
                left=Identifier("i"),
                op="<",
                right=NumericLiteral("3")
            ),
            update=BinaryExpression(
                left=Identifier("i"),
                op="+=",
                right=NumericLiteral("1")
            ),
            body=Body([
                TryCatch(
                    try_body=Body([
                        FunctionCall(
                            target="print",
                            params=[
                                FuncCallParam(
                                    FunctionCall(
                                        target="risky_operation",
                                        params=[]
                                    )
                                )
                            ]
                        )
                    ]),
                    catch_blocks=[
                        (Identifier("RuntimeError"), Body([
                            FunctionCall(
                                target="print",
                                params=[
                                    FuncCallParam(
                                        InterpolatedStringLiteral(
                                            template='Caught exception: ${RuntimeError::what()}'
                                        )
                                    )
                                ]
                            )
                        ]))
                    ]
                )
            ])
        )
    ])
)

# Full program AST
program_ast = Body([
    vector_class,
    calc_factorial,
    risky_operation,
    main_function
], 0)

print(program_ast.To_CXX())  # For debugging, prints the generated C++ code