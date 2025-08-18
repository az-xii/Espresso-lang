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
    VOID_LITERAL = "VOID_LITERAL"
    NULLPTR_LITERAL = "NULLPTR_LITERAL"

    FUNC_PARAM = "FUNC_PARAM"
    FUNC_CALL_PARAM = "FUNC_CALL_PARAM"
    FUNCTION_DECL = "FUNCTION_DECL"
    FUNCTION_CALL = "FUNCTION_CALL"
    LAMBDA_EXPR = "LAMBDA_EXPR"
    RETURN = "RETURN"
    NULLPTR_LITERAL
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


# list<int> -> ListWrapper<IntWrapper>
TYPE_MAP : dict = {
    # Espresso | C++
    "byte"  : "ByteWrapper", # 8-bit signed integer
    "short" : "ShortWrapper", # 16-bit signed integer
    "int"   : "IntWrapper", # 32-bit signed integer
    "long"  : "LongWrapper", # 64-bit signed integer

    "ubyte" : "UByteWrapper", # 8-bit unsigned integer
    "ushort": "UShortWrapper", # 16-bit unsigned integer
    "uint"  : "UIntWrapper", # 32-bit unsigned integer
    "ulong" : "ULongWrapper", # 64-bit unsigned integer

    "float"     : "FloatWrapper", # 32-bit floating point
    "double"    : "DoubleWrapper", # 64-bit floating point

    "fixed16_16"    : "EspressoBits", # 32-bit fixed point
    "fixed32_32"    : "EspressoBits", # 64-bit fixed point

    "ufixed16_16"   : "UFixed16_16",
    "ufixed32_32"   : "UFixed32_32",

    "char"      : "char",
    "string"    : "StringWrapper", # String type
    "bool"      : "bool", # Boolean type
    "void"      : "void", # Void type
    "any"       : "std::any", # Any type
    "list"      : "ListWrapper", # List type
    "collection": "CollectionWrapper", # Collection type
    "map"       : "MapWrapper", # Dictionary type
    "set"       : "SetWrapper", # Set type
    "tuple"     : "TuppleWrapper", # Tuple type
    "auto"      : "auto", # Auto type
    "union"     : "UnionWrapper", # Variant type
    "lambda"    : "LambdaWrapper" # Lambda type
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




class AnnotationDefine(Annotation):
    """Represents a DEFINE annotation."""
    def __init__(
            self, 
            name: Union[str, "Identifier"],
            value: "_Literal"):
        super().__init__(NodeType.ANNOTATION_DEFINE, value=value)
        self.value = value
        self.name = name if isinstance(name, Identifier) else Identifier(name)

    def To_CXX(self) -> str:
        return f"#DEFINE {self.name.To_CXX()} {self.value.To_CXX()}"

class AnnotationAssert(Annotation):
    """Represents an ASSERT annotation that generates runtime checks."""
    def __init__(self, condition: "_Value"):
        super().__init__(NodeType.ANNOTATION_ASSERT)
        self.condition = condition
        # Handle different message types

    def To_CXX(self) -> str:
        # If no message, use standard assert
        return f"assert({self.condition.To_CXX()});"

    
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
    def __init__(self, value: "_Literal"):
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
    """Represents binary operations (+, -, *, /, %, &, |, ^, <<, >>)"""
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

class VarDeclare(_ASTNode):
    def __init__(self, 
                 var_name: Identifier,
                 var_type: Identifier,
                 modifiers: List[_Modifier] = []):
        super().__init__(NodeType.VAR_DECLARE, modifiers=modifiers)
        self.var_name = var_name
        self.var_type = var_type

    def To_CXX(self) -> str:
        parts = []
        if self.modifiers:
            parts.append(' '.join(m.To_CXX() for m in self.modifiers))
        parts.append(ConvertType(self.var_type.To_CXX()).strip())
        parts.append(self.var_name.To_CXX())
        return ' '.join(parts) + ';'

class VarAssign(_ASTNode):
    def __init__(self, 
                 var_name: Identifier,
                 value: _Value,
                 var_type: Identifier,
                 modifiers: List[_Modifier] = []):
        super().__init__(NodeType.VAR_ASSIGN, modifiers=modifiers)
        self.var_name = var_name
        self.value = value
        self.var_type = var_type

    def To_CXX(self) -> str:
        parts = []
        if self.modifiers:
            parts.append(' '.join(m.To_CXX() for m in self.modifiers))
        parts.append(ConvertType(self.var_type.To_CXX()).strip())
        parts.append(self.var_name.To_CXX())
        parts.append(f"= {self.value.To_CXX()}")
        return ' '.join(parts) + ';'

class MultiVarDeclare(_ASTNode):
    def __init__(self,
                var_names: List[Identifier], 
                var_type: Identifier, 
                modifiers: List[_Modifier] = []):
        super().__init__(NodeType.MULTI_VAR_DECLARE, modifiers=modifiers)
        self.var_names = var_names
        self.var_type = var_type

    def To_CXX(self) -> str:
        parts = []
        if self.modifiers:
            parts.append(' '.join(ConvertModifier(m) for m in self.modifiers))
        parts.append(ConvertType(self.var_type.To_CXX()).strip())
        parts.append(', '.join(var.To_CXX() for var in self.var_names))
        return ' '.join(parts) + ';'

class MultiVarAssign(_ASTNode):
    def __init__(self,
                var_names: List[Identifier],
                value: _Value,
                var_type: Identifier, 
                modifiers: List[_Modifier] = []):
        super().__init__(NodeType.MULTI_VAR_ASSIGN, modifiers=modifiers)
        self.var_names = var_names
        self.var_type = var_type
        self.value = value

    def To_CXX(self) -> str:
        parts = []
        if self.modifiers:
            parts.append(' '.join(ConvertModifier(m) for m in self.modifiers))
        parts.append(ConvertType(self.var_type.To_CXX()).strip())
        parts.append(', '.join(var.To_CXX() for var in self.var_names))
        parts.append(f"= {self.value.To_CXX()}")
        return ' '.join(parts) + ';'

# ==============================================
# Literals
# ==============================================

# `1, 0.6, 0xDEADBEEF`
class NumericLiteral(_Literal):
    """Minimal numeric literal that passes through with C++ suffixes"""
    def __init__(self, value: str):
        super().__init__(NodeType.NUMERIC_LITERAL)
        self.raw_value = value.strip()

    def To_CXX(self) -> str:
        """Pass through with underscores removed"""
        return self.raw_value.replace('_', '')

# `{1, 0.6, 0xDEADBEEF}`
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

# `{{"Renz", 1}, {"Henry Lee Hu", 2}}`
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

# `"Hello, World!"`
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

# `r"Hello\nWorld"`
class RawStringLiteral(_Literal):
    """Raw string literal (no escape processing)"""
    def __init__(self, value: str):
        super().__init__(NodeType.RAW_STRING_LITERAL, value)

    def To_CXX(self) -> str:
        return f'R"({self.value})"'

# `f"Hello, ${name}"`
class InterpolatedStringLiteral(_Literal):
    """f-string style literal with f"text ${expr} more text" syntax"""
    def __init__(self, template: str):
        super().__init__(NodeType.F_STRING_LITERAL, value=template)
        self.parts = self._parse_template(template)

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
            else:
                current += template[i]
                i += 1
        if current:
            parts.append(current)
        return parts

    def To_CXX(self) -> str:
        format_parts = []
        args = []
        for part in self.parts:
            if isinstance(part, str):
                # Escape curly braces in literal parts
                format_parts.append(part.replace('{', '{{').replace('}', '}}'))
            else:
                format_parts.append("{}")
                args.append(part.To_CXX())
        return f'fmt::format("{"".join(format_parts)}", {", ".join(args)})'

# `true, false`
class BoolLiteral(_Literal):
    """Boolean literal (true/false)"""
    def __init__(self, value: bool):
        super().__init__(NodeType.BOOL_LITERAL)
        self.value = value

    def To_CXX(self) -> str:
        return "true" if self.value else "false"

# `void`
class VoidLiteral(_Literal):
    """Void literal (no value)"""
    def __init__(self):
        super().__init__(NodeType.VOID_LITERAL)

    def To_CXX(self) -> str:
        return "void"


class NullPtrLiteral(_Literal):
    """Void literal (no value)"""
    def __init__(self):
        super().__init__(NodeType.NULLPTR_LITERAL)

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
        
        return f"{self.target.To_CXX()}({', '.join(args)})"

class FunctionDecl(_ASTNode):
    def __init__(self, 
                 name: Identifier,
                 return_type: Identifier,
                 params: List[FuncDeclParam],
                 body: Body = None,
                 modifiers: List[_Modifier] = []):
        super().__init__(NodeType.FUNCTION_DECL, body=body or Body([]))
        self.name = name if isinstance(name, Identifier) else Identifier(name)
        self.return_type = return_type if isinstance(return_type, Identifier) else Identifier(return_type)
        self.params = params
        self.modifiers = modifiers or []

    def To_CXX(self) -> str:
        param_list = ', '.join(p.To_CXX() for p in self.params)
        mods = ' '.join(ConvertModifier(m) for m in self.modifiers) if self.modifiers else ""
        body = self.body.To_CXX()
        return_type = ConvertType(self.return_type.To_CXX())
        
        # Handle constructor special case
        if self.name.To_CXX() == return_type:
            return f"{mods}{self.name.To_CXX()}({param_list}) {{\n{body}\n}}"
        return f"{mods}{return_type} {self.name.To_CXX()}({param_list}) {{\n{body}\n}}"

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

class Case(_ASTNode):
    """Case syntax"""
    def __init__(self, case: _Value, body: Body):
        super().__init__(NodeType.CASE, case, body)

    def To_CXX(self):
        return "case {self.case.To_CXX()}:\n{self.body.To_CXX()}"

class Switch(_ASTNode):
    """Switch case syntax"""
    def __init__(self, subject: _Value, cases: Body):
        super().__init__(NodeType.Switch, value=subject, body=cases)

    def To_CXX(self):
        return "switch({self.subject.To_CXX()}) \{\n{self.body.To_CXX()}\}"

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

