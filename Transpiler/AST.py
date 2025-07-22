from ast import pattern
from enum import Enum
from textwrap import indent
from token import OP
from turtle import st
from typing import List, Union, Optional, Dict, Tuple, Any, Literal
from abc import ABC, abstractmethod
import re

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


    SCOPE_MODIFIER = "SCOPE_MODIFIER"
    CONST_MODIFIER = "CONST_MODIFIER"
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
    EXPRESSION_ARITHMETIC = "EXPRESSION_ARITHMETIC"
    EXPRESSION_BITWISE = "EXPRESSION_BITWISE"
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


ConditionOperators: set = {
    "==",   # Equal
    "<=",   # Less or Equal
    ">=",   # More or Equal
    "!=",   # Not Equal
    ">",    # Greater
    "<"     # Less
}

ArithmeticOperators: set = {
    "+",    # Add
    "-",    # Sub
    "*",    # Mul
    "/",    # Div
    "%",    # Mod
    "**",   # Exponent
}

BitwiseOperators: set = {
    "&",    # AND
    "|",    # OR
    "~",    # NOT
    "^",    # XOR
    "<<",   # Left Shift
    ">>",   # Right Shift
}

TYPE_MAP : dict = {
    # Espresso | C++
    "short" : "EspressoShort", # 32-bit signed integer
    "int": "EspressoInt", # 64-bit signed integer
    "ushort": "EspressoUShort", # 32-bit unsigned integer
    "uint": "EspressoUInt", # 64-bit unsigned integer
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

class _ASTNode(ABC):
    """Base AST node class with enhanced functionality."""
    def __init__(
        self, 
        node_type: NodeType, 
        body: Optional[Union[List["_ASTNode"], "Body"]] = None,
        value: Optional[Any] = None,
        annotations: Optional[List["Annotation"]] = None,
        indent_level: int = 0,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.type = node_type
        self.body = body if isinstance(body, Body) else Body(body or [])
        self.value = value
        self.annotations = annotations or []
        self.indent_level = indent_level

    def add_annotation(self, annotation: "Annotation") -> None:
        self.annotations.append(annotation)

    @property
    def is_statement(self) -> bool:
        return not isinstance(self, _Value)
    
    @property 
    def is_expression(self) -> bool:
        return isinstance(self, _Value)

    @abstractmethod
    def To_CXX(self) -> str:
        raise NotImplementedError("Subclasses must implement To_CXX")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type}, value={self.value})"

class _Value(_ASTNode, ABC):
    """Base class for all value-producing expressions (literals, variables, operations, etc.)"""
    pass

class Body():
    def __init__(self, statements: List[_ASTNode], indent_level: int = 0):
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

# ==============================================
# Basic Syntax Nodes
# ==============================================

class NewLine(_ASTNode):
    """Represents a newline in the source code."""
    def __init__(self):
        super().__init__(NodeType.NEWLINE, value="\n")

    def To_CXX(self) -> str:
        return "\n"
 
class Indent(_ASTNode):
    """Represents an indentation in the source code."""
    def __init__(self, level: int = 1):
        super().__init__(NodeType.INDENT, value=" " * (4 * level))  # 4 spaces per indent level

    def To_CXX(self) -> str:
        return str(self.value)
    
class Identifier(_Value, _ASTNode):
    """Represents an identifier in the source code."""
    def __init__(self, name: str):
        super().__init__(NodeType.IDENTIFIER, value=name)

    def To_CXX(self) -> str:
        return str(self.value)


# ==============================================
# Annotation Nodes
# ==============================================

class Annotation(_ASTNode):
    """Base class for annotations"""
    pass

class AnnotationDefine(Annotation):
    """Represents a DEFINE annotation."""
    def __init__(
            self, 
            name: Union[str, "Identifier"],
            value: "_LiteralNode"):
        super().__init__(NodeType.ANNOTATION_DEFINE, value=value)
        self.value = value
        self.name = name if isinstance(name, Identifier) else Identifier(name)

    def To_CXX(self) -> str:
        return f"#DEFINE {self.name.To_CXX()} {self.value.To_CXX()}"

class AnnotationAssert(Annotation):
    """Represents an ASSERT annotation that generates runtime checks."""
    def __init__(self, 
                 condition: "_ASTNode", 
                 message: Optional[Union[str, "_StringLiteral", "Identifier"]] = None):
        super().__init__(NodeType.ANNOTATION_ASSERT)
        self.condition = condition
        # Handle different message types
        if isinstance(message, str):
            self.message = NormalStringLiteral(message)
        elif isinstance(message, (_StringLiteral, Identifier)):
            self.message = message
        else:
            self.message = None

    def To_CXX(self) -> str:
        # If no message, use standard assert
        if not self.message:
            return f"assert({self.condition.To_CXX()});"
        
        # Use more detailed assertion with message
        return (
            f"if (!({self.condition.To_CXX()})) {{\n"
            f"    throw std::runtime_error({self.message.To_CXX()});\n"
            f"}}"
        )
    
class AnnotationIO(Annotation):
    """Represents an IO operation"""
    def __init__(self):
        super().__init__(NodeType.ANNOTATION_IO)

    def To_CXX(self):
        return "//IO:"

class AnnotationSafe(Annotation):
    """Unsafe operations"""
    def __init__(self):
        super().__init__(NodeType.ANNOTATION_SAFE)

    def To_CXX(self):
        return f"//SAFE:"

class AnnotationUnsafe(Annotation):
    """Unsafe operations"""
    def __init__(self):
        super().__init__(NodeType.ANNOTATION_UNSAFE)

    def To_CXX(self):
        return f"//UNSAFE:"

class AnnotationPanic(Annotation):
    """Intentional Crash"""
    def __init__(self, value: "_LiteralNode"):
        super().__init__(NodeType.ANNOTATION_PANIC, value=value)

    def To_CXX(self):
        return f"abort({self.value})"
    
class AnnotationNamespace(Annotation):
    """Nampespace"""
    def __init__(self, ns_name: Union[str, "Identifier"], children: Union[List["_ASTNode"], "Body"]):
        super().__init__(NodeType.ANNOTATION_NAMESPACE, value=ns_name if isinstance(ns_name, Identifier) else Identifier(ns_name))
        self.body = children if isinstance(children, Body) else Body(children or [], 1)

    def To_CXX(self):
        ns_name = self.value.To_CXX() if self.value is not None else ""
        return f"namespace {ns_name} {{\n{self.body.To_CXX()}\n}}"


# ==============================================
# Modifier Classes
# ==============================================

class Modifier(_ASTNode):
    """Base class for all modifiers"""
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)

    def To_CXX(self):
        pass

class ScopeModifier(Modifier):
    """Access control modifiers (public/private/protected)"""
    def __init__(self, scope: Literal["public", "private", "protected"]):
        super().__init__(NodeType.SCOPE_MODIFIER)
        self.scope = scope
        
    def To_CXX(self) -> str:
        return f"{self.scope}:\n"  # Will be used in member declarations

class ConstModifier(Modifier):
    """Const/immutable modifier"""
    def __init__(self):
        super().__init__(NodeType.CONST_MODIFIER)

class StaticModifier(Modifier):
    """Static/class-level modifier"""
    def __init__(self):
        super().__init__(NodeType.STATIC_MODIFIER)

class AbstractModifier(Modifier):
    """Abstract class/method modifier"""
    def __init__(self):
        super().__init__(NodeType.ABSTRACT_MODIFIER)

class OverrideModifier(Modifier):
    """Override class/method modifier"""
    def __init__(self):
        super().__init__(NodeType.OVERRIDE_MODIFIER)

class VirtualModifier(Modifier):
    """Virtual class/method modifier"""
    def __init__(self):
        super().__init__(NodeType.VIRTUAL_MODIFIER)



# ==============================================
# Variables
# ==============================================

class VarDeclare(_ASTNode):
    def __init__(self, 
                 var_name: Union[str, Identifier],
                 var_type: Union[str, Identifier],
                 modifiers: List[Modifier] = []):
        super().__init__(NodeType.VAR_DECLARE)
        self.var_name = var_name if isinstance(var_name, Identifier) else Identifier(var_name)
        self.var_type = var_type if isinstance(var_type, Identifier) else Identifier(var_type)
        self.modifiers = modifiers or []

    def To_CXX(self) -> str:
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) if self.modifiers else ""
        type_str = ConvertType(self.var_type.To_CXX())
        return f"{mods} {type_str} {self.var_name.To_CXX()};"

class VarAssign(_ASTNode):
    def __init__(self, var_name: Union[str, Identifier],
                 value: _Value,  # Now explicitly requires a Value node
                 var_type: Optional[Union[str, Identifier]]):
        super().__init__(NodeType.VAR_ASSIGN)
        self.var_name = var_name if isinstance(var_name, Identifier) else Identifier(var_name)
        self.value = value  # Guaranteed to be a Value node
        self.var_type = var_type if isinstance(var_type, Identifier) else Identifier(var_type) if var_type else None

    def To_CXX(self) -> str:
        type_str = f"{ConvertType(self.var_type.To_CXX())} " if self.var_type else ""
        return f"{type_str}{self.var_name.To_CXX()} = {self.value.To_CXX()};"

class MultiVarDeclare(_Value):
    def __init__(self, 
                 names: List[Union[str, Identifier]],
                 var_type: Union[str, Identifier],
                 modifiers: List[Modifier] = []):
        super().__init__(NodeType.MULTI_VAR_DECLARE)
        self.names = [name if isinstance(name, Identifier) else Identifier(name) for name in names]
        self.var_type = var_type
        self.modifiers = modifiers or []

    def To_CXX(self) -> str:
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) + ' ' if self.modifiers else ''
        type_str = ConvertType(self.var_type.To_CXX() if isinstance(self.var_type, Identifier) else self.var_type)
        names_str = ', '.join(name.To_CXX() for name in self.names)
        return f"{mods}{type_str} {names_str};"

class MultiVarAssign(_Value):
    def __init__(self, 
                 names: List[Union[str, Identifier]],
                 var_type: Union[str, Identifier],
                 value: _Value,
                 modifiers: List[Modifier] = []):
        super().__init__(NodeType.MULTI_VAR_ASSIGN)
        self.names = [name if isinstance(name, Identifier) else Identifier(name) for name in names]
        self.var_type = var_type
        self.value = value
        self.modifiers = modifiers or []

    def To_CXX(self) -> str:
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) + ' ' if self.modifiers else ''
        type_str = ConvertType(self.var_type.To_CXX() if isinstance(self.var_type, Identifier) else self.var_type)
        names_str = ', '.join(name.To_CXX() for name in self.names)
        return f"{mods}{type_str} {names_str} = {self.value.To_CXX()};"
    
    
# ==============================================
# Conditions and Expressions
# ==============================================

class Condition(_Value, _ASTNode):
    """Base class for all condition types"""
    pass

class Comparison(Condition):
    """Represents comparison operations (==, <=, >=, etc.)"""
    def __init__(self, left: _ASTNode, op: str, right: _ASTNode):
        if op not in ConditionOperators:
            raise ValueError(f"Invalid comparison operator: {op}")
        super().__init__(NodeType.COMPARISON)
        self.left = left
        self.op = op
        self.right = right

    def To_CXX(self) -> str:
        return f"{self.left.To_CXX()} {self.op} {self.right.To_CXX()}"

class BooleanCondition(Condition):
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
        return f" {cxx_op} ".join(op.To_CXX() for op in self.operands)

class Expression(_Value, _ASTNode):
    """Base class for all expression types"""
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)

class ArithmeticExpression(Expression):
    """Represents arithmetic operations (+, -, *, /, %)"""
    def __init__(self, op: str, left: _ASTNode, right: _ASTNode):
        if op not in ArithmeticOperators:
            raise ValueError(f"Invalid comparison operator: {op}")
        super().__init__(NodeType.EXPRESSION_ARITHMETIC)
        self.op = op
        self.left = left
        self.right = right

    def To_CXX(self) -> str:
        left_str = f"({self.left.To_CXX()})" if isinstance(self.left, (ArithmeticExpression, BitwiseExpression)) else self.left.To_CXX()
        right_str = f"({self.right.To_CXX()})" if isinstance(self.right, (ArithmeticExpression, BitwiseExpression)) else self.right.To_CXX()
        return f"{left_str} {self.op} {right_str}"

class BitwiseExpression(Expression):
    """Represents bitwise operations (&, |, ^, ~, <<, >>)"""
    def __init__(self, op: str, left: _ASTNode, right: Optional[_ASTNode] = None):
        if op not in BitwiseOperators:
            raise ValueError(f"Invalid comparison operator: {op}")    
        super().__init__(NodeType.EXPRESSION_BITWISE)
        self.op = op
        self.left = left
        self.right = right

    def To_CXX(self) -> str:
        if self.op == '~':
            return f"~{self.left.To_CXX()}"
        if self.right is None:
            raise ValueError(f"Binary operator {self.op} requires two operands")
        return f"{self.left.To_CXX()} {self.op} {self.right.To_CXX()}"

class UnaryExpression(Expression):
    """Represents unary operations (!, -, +)"""
    def __init__(self, op: str, operand: _ASTNode):
        super().__init__(NodeType.EXPRESSION_UNARY)
        self.op = op
        self.operand = operand

    def To_CXX(self) -> str:
        # Handle special case for 'not' which we map to '!'
        op = '!' if self.op == 'not' else self.op
        return f"{op}{self.operand.To_CXX()}"


# ==============================================
# Literals
# ==============================================

class _LiteralNode(_Value, _ASTNode):
    """Base class for literals"""
    pass

class NumericLiteral(_LiteralNode):
    """Enhanced numeric literal with two's complement support and automatic typing"""
    TYPE_SUFFIXES = {
        # Unsigned
        'u8': 'EspressoByte',
        'u16': 'EspressoUShort',
        'u32': 'EspressoUInt',
        'u64': 'EspressoULong',
        'U': 'EspressoUInt',
        'UL': 'EspressoULong',
        # Signed
        'i8': 'EspressoByte',
        'i16': 'EspressoShort',
        'i32': 'EspressoInt',
        'i64': 'EspressoLong',
        'L': 'EspressoLong',
        'LL': 'EspressoLong',
        # Floating point
        'f32': 'EspressoFloat',
        'f64': 'EspressoDouble',
        'F': 'EspressoFloat',
        'D': 'EspressoDouble'
    }

    # Size limits for type inference (using your type sizes)
    TYPE_RANGES = [
        ('EspressoByte',  -128, 127),
        ('EspressoShort', -32768, 32767),
        ('EspressoInt',   -2147483648, 2147483647),
        ('EspressoLong',  -9223372036854775808, 9223372036854775807),
        ('EspressoUShort', 0, 65535),
        ('EspressoUInt',   0, 4294967295),
        ('EspressoULong',  0, 18446744073709551615)
    ]

    def __init__(self, value: str):
        super().__init__(NodeType.NUMERIC_LITERAL)
        self.raw_value = value
        self.value, self.suffix, self.is_negative = self._parse_value(value)
        self.type = self._infer_type()

    def _parse_value(self, value: str) -> Tuple[str, str, bool]:
        """Extract numeric value, suffix, and sign"""
        clean_value = value.replace('_', '')
        is_negative = clean_value.startswith('-')
        if is_negative:
            clean_value = clean_value[1:]

        suffix = ''
        for possible_suffix in sorted(self.TYPE_SUFFIXES.keys(), key=len, reverse=True):
            if clean_value.lower().endswith(possible_suffix.lower()):
                suffix = possible_suffix
                clean_value = clean_value[:-len(suffix)]
                break

        return clean_value, suffix, is_negative

    def _infer_type(self) -> str:
        """Determine Espresso type based on value and suffix"""
        if self.suffix:
            return self.TYPE_SUFFIXES[self.suffix]

        if '.' in self.value or 'e' in self.value.lower():
            return 'EspressoDouble'

        num = abs(int(self.value, 0))
        
        # Check unsigned types first if no negative sign
        if not self.is_negative:
            for type_name, min_val, max_val in self.TYPE_RANGES:
                if type_name.startswith('EspressoU') and num <= max_val:
                    return type_name

        # Check signed types
        for type_name, min_val, max_val in self.TYPE_RANGES:
            if not type_name.startswith('EspressoU'):
                if (not self.is_negative and num <= max_val) or \
                   (self.is_negative and abs(num) <= abs(min_val)):
                    return type_name

        raise ValueError(f"Value {self.raw_value} is out of range for all types")

    def _apply_twos_complement(self, value: int, type_name: str) -> str:
        """Convert negative numbers to two's complement representation"""
        if not self.is_negative:
            return str(value)
        
        bits = {
            'EspressoByte': 8,
            'EspressoShort': 16,
            'EspressoInt': 32,
            'EspressoLong': 64
        }.get(type_name, 32)

        mask = (1 << bits) - 1
        complemented = (~abs(value) + 1) & mask
        
        if self.value.startswith(('0x', '0X')):
            return f"0x{complemented:X}"
        elif self.value.startswith(('0b', '0B')):
            return f"0b{complemented:b}"
        elif self.value.startswith('0') and len(self.value) > 1:
            return f"0{complemented:o}"
        
        return f"{complemented} /* {value} in {bits}-bit two's complement */"

    def To_CXX(self) -> str:
        """Generate C++ code with proper type handling"""
        # Handle floating point
        if self.type in ('EspressoFloat', 'EspressoDouble'):
            return f"{self.value}{'F' if self.type == 'EspressoFloat' else ''}"

        # Handle integers
        try:
            num_value = int(self.value, 0)
        except ValueError:
            num_value = int(self.value)

        # Apply two's complement for signed types
        if self.is_negative and not self.suffix and not self.type.startswith('EspressoU'):
            return self._apply_twos_complement(num_value, self.type)

        # Default case - use original formatting but clean up underscores
        clean_value = self.raw_value.replace('_', '')
        if self.is_negative:
            clean_value = f"-{clean_value}"
        return clean_value

class ItemContainerLiteral(_LiteralNode):
    """Base class for list/set/tuple literals using uniform {} syntax"""
    def __init__(self, items: List[_ASTNode], delims : str = "{}"):
        assert delims in ["()", "{}"], f"Unknown demlimiter {delims}"
        super().__init__(NodeType.LIST_LITERAL)  # We'll reuse this node type
        self.items = items
        self.delims = delims

    def To_CXX(self) -> str:
        items_str = ", ".join(item.To_CXX() for item in self.items)
        return f"{self.delims[0]}{items_str}{self.delims[1]}"

class KVContainerLiteral(_LiteralNode):
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

class _StringLiteral(_LiteralNode):
    """Base class for all string literals"""
    def __init__(self, node_type: NodeType, value: str):
        super().__init__(node_type)
        self.value = value

class NormalStringLiteral(_StringLiteral):
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

class RawStringLiteral(_StringLiteral):
    """Raw string literal (no escape processing)"""
    def __init__(self, value: str):
        super().__init__(NodeType.RAW_STRING_LITERAL, value)

    def To_CXX(self) -> str:
        return f'R"({self.value})"'

class InterpolatedStringLiteral(_StringLiteral):
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

class BoolLiteral(_LiteralNode):
    """Boolean literal (true/false)"""
    def __init__(self, value: bool):
        super().__init__(NodeType.BOOL_LITERAL)
        self.value = value

    def To_CXX(self) -> str:
        return "true" if self.value else "false"

class VoidLiteral(_LiteralNode):
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
                 name: Union[str, Identifier],
                 param_type: Union[str, Identifier],
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
                 name: Optional[Union[str, Identifier]] = None):
        super().__init__(NodeType.FUNC_CALL_PARAM)
        self.value = value
        self.name = name if isinstance(name, Identifier) else Identifier(name) if name else None

    def To_CXX(self) -> str:
        if self.name:
            return f".{self.name.To_CXX()}={self.value.To_CXX()}"
        return self.value.To_CXX()

class FunctionCall(_Value, _ASTNode):
    def __init__(self, 
                 target: Union[str, Identifier, _ASTNode],
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
                 name: Union[str, Identifier],
                 return_type: Union[str, Identifier],
                 params: List[FuncDeclParam],
                 body: Union[List["_ASTNode"], "Body"],
                 modifiers: List[Modifier] = []):
        super().__init__(NodeType.FUNCTION_DECL, children=body)
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
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) if self.modifiers else ""
        body = self.body.To_CXX()
        return f"{mods} {ConvertType(self.return_type.To_CXX())} {self.name.To_CXX()}({param_list}) {{\n{body}\n}}"

    def _generate_named(self) -> str:
        # 1. Generate parameter struct
        struct_name = f"{self.name.To_CXX()}_Params"
        struct_members = []
        for param in self.params:
            member = f"{ConvertType(param.param_type.To_CXX())} _{param.name.To_CXX()};"
            struct_members.append(member)
        
        struct_def = f"struct {struct_name} {{\n"
        struct_def += Body(struct_members, 1).To_CXX() + "\n};\n\n"

        # 2. Generate function with struct parameter
        mods = ' '.join(m.To_CXX() or "" for m in self.modifiers) if self.modifiers else ""
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
                 params: List[Tuple[Union[str, Identifier], 
                                   Union[str, Identifier]]],
                 body: Union[List["_ASTNode"], "Body"] ,
                 return_type: Union[str, Identifier] = "",
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
        if value is not None and not value.is_expression:
            raise TypeError("Return value must be an expression")
        super().__init__(NodeType.RETURN, value=value if value else None)

    def To_CXX(self):
        return f"return {self.value.To_CXX()};" if self.value else "return;"

# ==============================================
# OOP
# ==============================================

class GenericParam(_ASTNode):
    """Represents a template parameter (type or non-type)"""
    def __init__(self, 
                 name: Union[str, Identifier], 
                 param_type: Optional[Union[str, Identifier]] = None,
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
                name: Union[str, "Identifier"],
                body: List["_ASTNode"],
                generic_params: List["GenericParam"] = [],
                parents: List[Union[str, "Identifier"]] = [], 
                modifiers: List["Modifier"] = []):
        super().__init__(NodeType.CLASS_DEFINE, body=body or [])
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
            self._modifiers() +
            f"class {self.name.To_CXX()}{self._parents()} {{\n{body_content}\n}};"
        )

    def _template(self):
        return f"template<{', '.join(p.To_CXX() for p in self.generic_params)}>\n" if self.generic_params else ""

    def _modifiers(self):
        mod_map = [(AbstractModifier, "abstract"), (ConstModifier, "const"), (StaticModifier, "static")]
        mods = [kw for mod, kw in mod_map if any(isinstance(m, mod) for m in self.modifiers)]
        return (" ".join(mods) + " ") if mods else ""

    def _parents(self):
        if not self.parents: return ""
        return " : public " + ", ".join(p.To_CXX() if isinstance(p, _ASTNode) else str(p) for p in self.parents)

class ClassInstantiation(_Value, _ASTNode):
    """Represents creating a new class instance (constructor call)"""
    def __init__(self,
                 class_name: Union[str, Identifier],
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


# ==============================================
# Control Flow Structures
# ==============================================

class IfExpr(_ASTNode):
    def __init__(self, condition: _ASTNode, 
                 body: Union[List["_ASTNode"], "Body"],
                 elifs: List[Tuple[_ASTNode, Union[List["_ASTNode"], "Body"]]] = [],
                 else_body: Union[List["_ASTNode"], "Body"] = []):
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
    def __init__(self, value: _ASTNode, arms: List[Tuple[_ASTNode, Union[List["_ASTNode"], "Body"]]], else_body: Union[List["_ASTNode"], "Body"] = []):
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
    def __init__(self, condition: _ASTNode, body: Union[List["_ASTNode"], "Body"]):
        super().__init__(NodeType.WHILE_LOOP, body=body)
        self.condition = condition

    def To_CXX(self) -> str:
        return f"while ({self.condition.To_CXX()}) {{\n{self.body.To_CXX()}\n}}"

class ForInLoop(_ASTNode):
    def __init__(self, var_name: Union[str, Identifier],
                 iterable: _ASTNode,
                 body: Union[List["_ASTNode"], "Body"]):
        super().__init__(NodeType.FOR_IN_LOOP, body=body)
        self.var_name = var_name if isinstance(var_name, Identifier) else Identifier(var_name)
        self.iterable = iterable

    def To_CXX(self) -> str:
        return f"for (auto&& {self.var_name.To_CXX()} : {self.iterable.To_CXX()}) {{\n{self.body.To_CXX()}\n}}"

class CStyleForLoop(_ASTNode):
    def __init__(self, init: _ASTNode,
                 condition: _ASTNode,
                 update: _ASTNode,
                 body: List[_ASTNode]):
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
    def __init__(self, try_body: List[_ASTNode], 
                 catch_blocks: List[Tuple[Union[str, Identifier], Union[List["_ASTNode"], "Body"]]],
                 finally_body: Optional[Union[List["_ASTNode"], "Body"]] = []):
        super().__init__(NodeType.TRY_CATCH, children=try_body)
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

