from enum import Enum
from typing import List, Union, Optional, Type
# Helper classes and enums for AST nodes

class NodeType(Enum):
    NEWLINE = "NewLine"  # Represents a newline in the AST
    INDENT = "Indent"  # Represents an indentation level in the AST
    IMPORT_DECL = "ImportDecl"  # `import math`
    DEFINE_DECL = "DefineDecl"  # `define PI 3.14`

    ASSIGN_VAR_DECL = "AssignVarDecl" # `int x = 10`
    INIT_VAR_DECL = "InitVarDecl" # `int x`
    MULTI_ASSIGN_VAR_DECL = "MultiAssignVarDecl" # `int x = 10, y = 20`
    MULTI_INIT_VAR_DECL = "MultiAssignVarDecl" # `int x, y, z`
    VARIABLE = "Variable"  # Represents a variable name (e.g., `x`, `y`, `z`)
    AUG_ASSIGN = "AugAssign"  # `x += 1`
    BINARY_OP = "BinaryOpExpr"  # Represents binary operations (e.g., `a + b`, `x > y`)
    COMPARATOR = "Comparator"  # Represents comparison operations (e.g., `x < y`, `a == b`)
    BITWISE_OP = "BitwiseOp"  # Represents bitwise operations (e.g., `a & b`, `x | y`)

    BOOLEAN_OPS = "BooleanOps"  # Represents boolean operations (e.g., `and`, `or`, `not`)
    IF_EXPR = "IfExpr"  # `if (condition) { ... }`
    TERNARY_EXPR = "TernaryExpr"  # `condition ? true_expr : false_expr`
    ELIF_EXPR = "ElifExpr"  # `elif (condition) { ... }`
    ELSE_EXPR = "ElseExpr"  # `else { ... }`

    WHILE_EXPR = "WhileExpr"  # `while (condition) { ... }`
    C_STYLE_FOR_EXPR = "CStyleForExpr"  # `for (initial, while condition, increment) { ... }`
    FOR_IN_EXPR = "ForInExpr"  # `for (item in iterable) { ... }`

    FUNCTION_DECL = "FunctionDecl"  # `def function_name(params) { ... }`
    LAMBDA_EXPR = "LambdaExpr"  # `lambda (params): {expression}`
    FUNCTION_CALL = "FunctionCall"  # `function_name(args)`

    CLASS_DECL = "ClassDecl"  # `class ClassName { ... }`
    CLASS_CREATE = "ClassCreate"  # `ClassName(args)`
    
    NUMERIC_LITERAL = "NumericLiteral"  # Represents a numeric literal (e.g., 42, 3.14)
    STRING_LITERAL = "StringLiteral"  # Represents a string literal (e.g., "Hello, World!")
    INTERPOLATED_STRING_LITERAL = "InterpolatedStringLiteral"  # Represents an f-string (e.g., f"Value: {x + 1}")
    BOOLEAN_LITERAL = "BooleanLiteral"  # Represents a boolean literal (e.g., true, false)
    MAP_LITERAL = "MapLiteral"  # Represents a map literal (e.g., {key: value})
    LIST_LITERAL = "ListLiteral"  # Represents a list literal (e.g., [1, 2, 3])
    TUPLE_LITERAL = "TupleLiteral"  # Represents a tuple literal (e.g., (1, 2, 3))
    SET_LITERAL = "SetLiteral"  # Represents a set literal (e.g., {1, 2, 3})

class ASTNode:
    def __init__(self, node_type: NodeType, children: list["ASTNode"]=None, value: Union["ASTNode", str]=None):
        self.type = node_type  # e.g., "FunctionDecl", "TernaryExpr"
        self.children = children or []
        self.value = value     # Literal value if terminal node

    def add_child(self, child):
        """Add a child node to this AST node."""
        self.children.append(child)

    def To_CXX(self) ->str:
        """Convert the AST node to C++ code."""
        raise NotImplementedError("To_CXX method must be implemented in subclasses")

    def __repr__(self):
        """String representation of the AST node."""
        return f"ASTNode(type={self.type}, value={self.value}, children={self.children})"

TYPE_MAP = {
    # Espresso | C++
    "int" : "EspressoInt", # 32-bit signed integer
    "long": "EspressoLong", # 64-bit signed integer
    "u32": "EspressoU32", # 32-bit unsigned integer
    "u64": "EspressoU64", # 64-bit unsigned integer
    "float": "EspressoFloat", # 32-bit floating point
    "double": "EspressoDouble", # 64-bit floating point
    "decimal": "EspressoDecimal", # 128-bit floating point
    "bin" : "EspressoU32", # 32-bit binary
    "hex" : "EspressoU32", # 32-bit hexadecimal
    "oct" : "EspressoU32", # 32-bit octal
    "string": "EspressoTypes:String", # String type
    "bool": "bool", # Boolean type
    "void": "void", # Void type
    "any": "Espressoany", # Any type
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

# AST NODE TYPES

class NewLine(ASTNode):
    r"""
    Represents a newline in the AST.
    Espresso:
    \n
    C++:
    \n
    """
    def __init__(self):
        super().__init__(NodeType.NEWLINE, value="\n")

    def To_CXX(self) -> str:
        """Convert the newline to C++ code."""
        return "\n"

class Indent(ASTNode):
    def __init__(self, level=1, use_spaces=False, space_count=4):
        super().__init__(NodeType.INDENT)
        self.level = level
        self.use_spaces = use_spaces  # If False, use tabs
        self.space_count = space_count  # Default: 4 spaces per indent
    
    def To_CXX(self) -> str:
        if self.use_spaces:
            return " " * (self.space_count * self.level)
        return "\t" * self.level

class Identifier(ASTNode):
    """
    Represents an identifier in the AST.
    Espresso:
    x
    C++:
    x
    """
    def __init__(self, name: str):
        super().__init__(NodeType.VARIABLE, value=name)
        self.name = name

    def To_CXX(self) -> str:
        """Convert the identifier to C++ code."""
        return self.name

class DefineDecl(ASTNode):
    """
    Represents a define declaration in the AST.
    Espresso:
    @def f32 PI =  3.14
    C++:
    constexpr EspressoF32 PI 3.14
    """
    def __init__(self, name, value):
        super().__init__(NodeType.DEFINE_DECL, value=value)
        self.name = name

    def To_CXX(self) -> str:
        """Convert the define declaration to C++ code."""
        return f"#define {self.name} {self.value}"

class Variable(ASTNode):
    def __init__(self, name):
        super().__init__(NodeType.VARIABLE, value=name)
        self.name = name

    def To_CXX(self):
        return self.name

class ImportDecl(ASTNode):
    """
    Represents an import declaration in the AST.
    Espresso:
    import math
    C++:
    #include "Espresso/math.cpp"
    """
    def __init__(self, module_name):
        super().__init__(NodeType.IMPORT_DECL, value=module_name)

    def To_CXX(self) -> str:
        """Convert the import declaration to C++ code."""
        return f'#include "Espresso/{self.value}.cpp"'

class AssignVarDecl(ASTNode):
    """
    Represents an initialization variable declaration in the AST.
    Espresso:
    int x = 10
    C++:
    int x = 10;
    """
    def __init__(self, var_name, var_type, value):
        super().__init__(NodeType.INIT_VAR_DECL, value=value)
        self.var_name = var_name
        self.var_type = var_type


    def To_CXX(self) -> str:
        """Convert the variable declaration to C++ code."""
        return f'{ConvertType(self.var_type)} {self.var_name} = {self.value};'
    
class InitVarDecl(ASTNode):
    """
    Represents a variable declaration without initialization in the AST.
    Espresso:
    int x
    C++:
    int x;
    """
    def __init__(self, var_name, var_type):
        super().__init__(NodeType.INIT_VAR_DECL)
        self.var_name = var_name
        self.var_type = var_type

    def To_CXX(self) -> str:
        """Convert the variable declaration to C++ code."""
        return f"{ConvertType(self.var_type)} {self.var_name};"
    
class MultiAssignVarDecl(ASTNode):
    """
    Represents a multiple variable declaration with initialization in the AST.
    Espresso:
    int x = 10, y = 20
    C++:
    int x = 10, y = 20;
    """
    def __init__(self, var_decls):
        super().__init__(NodeType.MULTI_ASSIGN_VAR_DECL)
        self.var_decls = var_decls  # List of tuples (var_name, var_type, value)

    def To_CXX(self) -> str:
        """Convert the multiple variable declaration to C++ code."""
        decls = ', '.join(f'{ConvertType(var_type)} {var_name} = {value}' for var_name, var_type, value in self.var_decls)
        return f"{decls};"
    

class MultiInitVarDecl(ASTNode):
    """
    Represents a multiple variable declaration without initialization in the AST.
    Espresso:
    int x, y, z
    C++:
    int x, y, z;
    """
    def __init__(self, var_decls):
        super().__init__(NodeType.MULTI_INIT_VAR_DECL)
        self.var_decls = var_decls  # List of tuples (var_name, var_type)

    def To_CXX(self) -> str:
        """Convert the multiple variable declaration to C++ code."""
        decls = ', '.join(f'{ConvertType(var_type)} {var_name}' for var_name, var_type in self.var_decls)
        return f"{decls};"

class AugAssign(ASTNode):
    def __init__(self, target, op, value):
        super().__init__(NodeType.AUG_ASSIGN)
        self.target = target
        self.op = op
        self.value = value

    def To_CXX(self):
        return f"{self.target.To_CXX()} {self.op}= {self.value.To_CXX()};"

class Comparator(ASTNode):
    def __init__(self, left, op, right):
        super().__init__(NodeType.COMPARATOR)
        self.left = left
        self.op = op
        self.right = right

    def To_CXX(self):
        return f"{self.left.To_CXX()} {self.op} {self.right.To_CXX()}"
    

class BitwiseOp(ASTNode):
    """
    Represents bitwise operations (&, |, ^, ~, <<, >>).
    Espresso: a & b | c ^ d << e >> f ~g
    C++: a & b | c ^ d << e >> f ~g
    """
    def __init__(self, op, operands):
        super().__init__(NodeType.BINARY_OP)
        self.op = op  # '&', '|', '^', '~', '<<', '>>'
        self.operands = operands  # List of ASTNode

    def To_CXX(self):
        if self.op == '~':
            # Unary bitwise NOT
            return f"~{self.operands[0].To_CXX()}"
        elif self.op in ('&', '|', '^', '<<', '>>'):
            # Binary bitwise ops (left-associative)
            return f" {self.op} ".join(op.To_CXX() for op in self.operands)
        else:
            raise ValueError(f"Unknown bitwise operator: {self.op}")

class FunctionDecl(ASTNode):
    def __init__(self, name, return_type, params, body, modifiers=None, has_named_params=False):
        super().__init__(NodeType.FUNCTION_DECL, children=body)
        self.name = name
        self.return_type = return_type
        self.params = params  # List of (name, type, default_value)
        self.modifiers = modifiers or []
        self.has_named_params = has_named_params

    def To_CXX(self) -> str:
        if not self.has_named_params:
            # Traditional parameter list
            param_list = ', '.join(
                f"{ConvertType(param_type)} {param_name}" 
                for param_name, param_type, _ in self.params
            )
            body = '\n'.join(child.To_CXX() for child in self.children)
            return f"{' '.join(self.modifiers)}{ConvertType(self.return_type)} {self.name}({param_list}) {{\n{body}\n}}"
        
        else:
            # 1. Generate parameter struct
            struct_code = f"struct {self.name}_Params {{\n"
            for param_name, param_type, default_val in self.params:
                default = f" = {default_val}" if default_val else ""
                struct_code += f"    {ConvertType(param_type)} {param_name}{default};\n"
            struct_code += "};\n\n"
            
            # 2. Generate function with explicit unpacking
            fn_code = f"{' '.join(self.modifiers)}{ConvertType(self.return_type)} {self.name}({self.name}_Params p) }}\n"
            
            # Unpack all parameters
            for param_name, _, _ in self.params:
                fn_code += f"    auto {param_name} = p.{param_name};\n"
            
            # Add function body
            fn_code += '\n'.join(f"    {child.To_CXX()}" for child in self.children)
            fn_code += "\n}"
            

            return struct_code + fn_code
        
class FunctionCall(ASTNode):
    def __init__(self, function_name, args, is_named=False):
        super().__init__(NodeType.FUNCTION_CALL, value=function_name)
        self.args = args  # List of (param_name, value_expr) for named, or just value_expr for positional
        self.is_named = is_named

    def To_CXX(self) -> str:
        if not self.is_named:
            # Traditional positional call
            args_str = ', '.join(arg.To_CXX() for arg in self.args)
            return f"{self.value}({args_str})"
        else:
            # Named parameter call (C++20 designated initializers)
            args_str = ', '.join(
                f".{param_name}={value.To_CXX()}" 
                for param_name, value in self.args
            )
            return f"{self.value}({{{args_str}}})"

class LambdaExpr(ASTNode):
    """
    Represents a lambda expression in the AST.
    Espresso:
    lambda (ParamType param1, ParamType param2) -> ReturnType : { ... }
    C++:
    [capture](ParamType param1, ParamType param2) -> ReturnType { ... }
    """
    def __init__(self, params, return_type, body, capture=None):
        super().__init__(NodeType.LAMBDA_EXPR, value=body)
        self.params = params  # List of tuples (param_name, param_type)
        self.return_type = return_type
        self.capture = capture  # Optional capture list

    def To_CXX(self) -> str:
        """Convert the lambda expression to C++ code."""
        capture_str = f"[{self.capture}]" if self.capture else "[]"
        param_list = ', '.join(f'{ConvertType(param_type)} {param_name}' for param_name, param_type in self.params)
        return f"{capture_str}({param_list}) -> {ConvertType(self.return_type)} {{ ''.join(child.To_CXX() for child in self.children) }}"

class BooleanOp(ASTNode):
    """
    Represents boolean operations (and, or, not).
    Espresso: not a and b or c
    C++: !a && b || c
    """
    def __init__(self, op, operands):
        super().__init__(NodeType.BINARY_OP)
        self.op = op  # 'and', 'or', 'not'
        self.operands = operands  # List of ASTNode

    def To_CXX(self):
        if self.op == 'not':
            # Unary NOT
            return f"!{self.operands[0].To_CXX()}"
        elif self.op == 'and':
            # Binary AND (left-associative)
            return ' && '.join(op.To_CXX() for op in self.operands)
        elif self.op == 'or':
            # Binary OR (left-associative)
            return ' || '.join(op.To_CXX() for op in self.operands)
        else:
            raise ValueError(f"Unknown boolean operator: {self.op}")

class IfExpr(ASTNode):
    """
    Represents an if expression in the AST.
    Espresso:
    if (condition) { ... }
    C++:
    if (condition) { ... }
    """
    def __init__(self, condition: "Comparator", body):
        super().__init__(NodeType.IF_EXPR, value=condition, children=body)

    def To_CXX(self) -> str:
        """Convert the if expression to C++ code."""
        return f"if ({self.value.To_CXX()}) {{ ''.join(child.To_CXX() for child in self.children) }}"
    
class ElifExpr(ASTNode):
    """
    Represents an elif expression in the AST.
    Espresso:
    elif (condition) { ... }
    C++:
    else if (condition) { ... }
    """
    def __init__(self, condition: "Comparator", body):
        super().__init__(NodeType.ELIF_EXPR, value=condition, children=body)

    def To_CXX(self) -> str:
        """Convert the elif expression to C++ code."""
        return f"else if ({self.value.To_CXX()}) {{ ''.join(child.To_CXX() for child in self.children) }}"
    
class ElseExpr(ASTNode):
    """
    Represents an else expression in the AST.
    Espresso:
    else { ... }
    C++:
    else { ... }
    """
    def __init__(self, body):
        super().__init__(NodeType.ELSE_EXPR, children=body)

    def To_CXX(self) -> str:
        """Convert the else expression to C++ code."""
        return f"else {{ ''.join(child.To_CXX() for child in self.children) }}"
    
class WhileExpr(ASTNode):
    """
    Represents a while expression in the AST.
    Espresso:
    while (condition) { ... }
    C++:
    while (condition) { ... }
    """
    def __init__(self, condition: "Comparator", body):
        super().__init__(NodeType.WHILE_EXPR, value=condition, children=body)

    def To_CXX(self) -> str:
        """Convert the while expression to C++ code."""
        return f"while ({self.value}) {{ ''.join(child.To_CXX() for child in self.children) }}"
    
class CStyleForExpr(ASTNode):
    """
    Represents a C-style for loop expression in the AST.
    Espresso:
    for (initialization; condition; increment) { ... }
    C++:
    for (initialization; condition; increment) { ... }
    """
    def __init__(self, initialization, condition: "Comparator", increment, body):
        super().__init__(NodeType.C_STYLE_FOR_EXPR, value=condition, children=body)
        self.initialization = initialization
        self.increment = increment

    def To_CXX(self) -> str:
        """Convert the C-style for loop to C++ code."""
        return f"for ({self.initialization}; {self.value}; {self.increment}) {{ ''.join(child.To_CXX() for child in self.children) }}"
    
class ForInExpr(ASTNode):
    """
    Represents a for-in loop expression in the AST.
    Espresso:
    for (var in iterable) { ... }
    C++:
    for (auto var : iterable) { ... }
    """
    def __init__(self, var_name, var_type, iterable, body):
        super().__init__(NodeType.FOR_IN_EXPR, value=iterable, children=body)
        self.var_name = var_name
        self.var_type = var_type

    def To_CXX(self) -> str:
        """Convert the for-in loop to C++ code."""
        return f"for ({ConvertType(self.var_type)} {self.var_name} : {self.value}) {{ ''.join(child.To_CXX() for child in self.children) }}"
    
class TernaryExpr(ASTNode):
    """
    Represents a ternary expression in the AST.
    Espresso:
    condition ? true_expr : false_expr
    C++:
    condition ? true_expr : false_expr
    """
    def __init__(self, condition, true_expr, false_expr):
        super().__init__(NodeType.TERNARY_EXPR, value=condition)
        self.true_expr = true_expr
        self.false_expr = false_expr

    def To_CXX(self) -> str:
        """Convert the ternary expression to C++ code."""
        return f"{self.value} ? {self.true_expr} : {self.false_expr}"

    
class ClassDecl(ASTNode):
    """
    Represents a class declaration in the AST.
    Espresso:
    class ClassName { ... }
    C++:
    class ClassName { ... }
    """
    def __init__(self, class_name, body, modifiers=[], inherits=[]):
        super().__init__(NodeType.FUNCTION_DECL, value=class_name, children=body)
        self.class_name = class_name
        self.modifiers = modifiers
        self.inherits = inherits

    def To_CXX(self) -> str:
        """Convert the class declaration to C++ code."""
        inherits_str = f" : public {', '.join(self.inherits)}" if self.inherits else ""
        modifiers_str = ' '.join(self.modifiers)
        body_str = ''.join(child.To_CXX() for child in self.children)
        return f"{modifiers_str}class {self.class_name} {inherits_str} {{ {body_str} }}"
    
class ClassCreate(ASTNode):
    """
    Represents a class instantiation in the AST.
    Espresso:
    ClassName(args)
    C++:
    ClassName(args)
    """
    def __init__(self, class_name, args):
        super().__init__(NodeType.FUNCTION_CALL, value=class_name)
        self.args = args  # List of argument expressions

    def To_CXX(self) -> str:
        """Convert the class instantiation to C++ code."""
        args_str = ', '.join(arg.To_CXX() for arg in self.args)
        return f"{self.value}({args_str})"
    
class NumericLiteral(ASTNode):
    def __init__(self, raw_value: str):
        super().__init__(NodeType.NUMERIC_LITERAL, value=raw_value)
        self.raw_value = raw_value.replace("_", "")  # Remove underscores upfront

    def To_CXX(self, target_type: str = None) -> str:
        """Convert to C++, optionally respecting a target type (e.g., from variable declaration)."""
        clean_value = self.raw_value
        
        # Case 1: Explicit target type (e.g., "u32", "decimal")
        if target_type:
            return f"static_cast<{ConvertType(target_type)}>({clean_value})"
        
        # Case 2: Infer from literal syntax
        if "." in clean_value or "e" in clean_value.lower():
            return clean_value  # Let C++ infer double/float
        elif clean_value.startswith(("0x", "0X")):
            return f"static_cast<EspressoU32>({clean_value})"  # Hex → U32
        elif clean_value.startswith(("0b", "0B")):
            return f"static_cast<EspressoU32>({clean_value})"  # Bin → U32
        elif clean_value.startswith(("0o", "0O")):
            return f"static_cast<EspressoU32>({clean_value})"  # Oct → U32
        else:
            return clean_value  # Default: let C++ handle it (likely int)
            
class StringLiteral(ASTNode):
    """Base class for all string literals. Handles common escaping."""
    def __init__(self, value: str, is_raw=False):
        super().__init__(NodeType.STRING_LITERAL, value=value)
        self.is_raw = is_raw  # If True, treat as raw string (no escapes)

    def To_CXX(self) -> str:
        if self.is_raw:
            return f'R"({self.value})"'  # C++ raw string literal (R"(content)")
        else:
            # Escape special chars (e.g., \n → \\n) for C++
            escaped = self.value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        

class InterpolatedString(ASTNode):
    """Espresso: f"Hello {name}!" → C++: EspressoFunc::Format("Hello {}!", name)"""
    def __init__(self, parts: list):
        super().__init__(NodeType.STRING_LITERAL)
        self.parts = parts  # Alternating strings and expressions
    
    def To_CXX(self) -> str:
        # Step 1: Build format string (replace interpolations with {})
        format_str = []
        arg_list = []
        arg_index = 0
        
        for part in self.parts:
            if isinstance(part, str):
                format_str.append(part.replace("{", "{{").replace("}", "}}"))  # Escape braces
            else:
                format_str.append(f"{{{arg_index}}}")  # Add positional placeholder
                arg_list.append(part.To_CXX())
                arg_index += 1
        
        # Step 2: Combine into EspressoFunc::Format call
        format_args = ", ".join(arg_list)
        return f"""EspressoFunc::Format("{"".join(format_str)}", {format_args})"""
    
class BooleanLiteral(ASTNode):
    """Represents a boolean literal in the AST."""
    def __init__(self, value: bool):
        super().__init__(NodeType.BOOLEAN_LITERAL, value=str(value).lower())

    def To_CXX(self) -> str:
        """Convert the boolean literal to C++ code."""
        return "true" if self.value == "true" else "false"

class VoidLiteral(ASTNode):
    """
    Represents a void literal (no value).
    Espresso: `void`
    C++: `void` (used for empty returns)
    """
    def __init__(self):
        super().__init__(NodeType.VOID_LITERAL, value="void")

    def To_CXX(self) -> str:
        return "void"
