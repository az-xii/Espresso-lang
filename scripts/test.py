from typing import Tuple, Dict
import re



GRAMMAR = r"""
start: (statement | NEWLINE)*

statement: var_declare
         | var_assign
         | multi_var_declare
         | multi_var_assign
         | function_decl
         | main_function
         | function_call
         | class_def
         | if_expr
         | while_loop
         | for_in_loop
         | c_style_for_loop
         | return_stmt
         | break_stmt
         | continue_stmt
         | try_catch
         | throw_stmt
         | annotation
         | comment
         | cpp_block
         | expression ";"

expression: comparison
          | binary_expr
          | unary_expr
          | literal
          | identifier
          | function_call
          | ternary_expr
          | lambda_expr

comparison: binary_expr (COMP_OP binary_expr)*
binary_expr: unary_expr (BIN_OP unary_expr)*
unary_expr: (UNARY_OP)* atom
atom: literal
    | identifier
    | function_call
    | "(" expression ")"
    | "[" [expression ("," expression)*] "]" -> list_literal
    | "{{" [kv_pair ("," kv_pair)*] "}}" -> map_literal

kv_pair: expression ":" expression
    
literal: NUMBER -> numeric_literal
       | STRING -> string_literal
       | RAW_STRING -> raw_string_literal
       | INTERP_STRING -> interpolated_string_literal
       | BOOLEAN -> bool_literal
       | "nullptr" -> null_ptr_literal
       | "void" -> void_literal

identifier: ID

// C++ style variable declarations: int x = 42;
var_declare: [modifier+] TYPE ID ["=" expression] [";"] 
var_assign: ID "=" expression ";"
multi_var_declare: [modifier+] TYPE ID ("," ID)* ";"
multi_var_assign: ID ("," ID)* "=" expression ";"

// Traditional function declaration
function_decl: [modifier+] "func" ID [generic_params] "(" [func_param ("," func_param)*] ")" ["->" TYPE] [":" member_init ("," member_init)*] "{" statement* "}"

// Special main function syntax: main: { ... }
main_function: "main" ":" "{" statement* "}"

function_call: ID [generic_args] "(" [func_call_param ("," func_call_param)*] ")"

func_param: ID ":" TYPE ["=" expression]
func_call_param: [ID "="] expression
generic_params: "<" generic_param ("," generic_param)* ">"
generic_param: ID [":" TYPE] ["=" expression]
generic_args: "<" TYPE ("," TYPE)* ">"
member_init: ID "(" expression ")"

class_def: [modifier+] "class" ID [generic_params] [":" inheritance] "{" class_member* "}"
class_member: access_specifier ":" statement*
           | statement
inheritance: TYPE ("," TYPE)*
access_specifier: "public" | "private" | "protected"


if_expr: "if" expression "{" statement* "}" ["elif" expression "{" statement* "}"]* ["else" "{" statement* "}"]
ternary_expr: expression "?" expression ":" expression

while_loop: "while" expression "{" statement* "}"
for_in_loop: "for" ID "in" expression "{" statement* "}"
c_style_for_loop: "for" "(" var_declare expression ";" expression ")" "{" statement* "}"

return_stmt: "return" [expression] ";"
break_stmt: "break" ";"
continue_stmt: "continue" ";"

try_catch: "try" "{" statement* "}" "catch" "(" TYPE ID ")" "{" statement* "}" ["finally" "{" statement* "}"]
throw_stmt: "throw" expression ";"

lambda_expr: "[" [capture] "]" "(" [func_param ("," func_param)*] ")" ["->" TYPE] "{" statement* "}"
capture: "=" | "&" | ID ("," ID)*

annotation: "@define" ID "=" expression
          | "@assert" expression
          | "@io"
          | "@safe"
          | "@unsafe"
          | "@panic" expression
          | "@namespace" ID "{" statement* "}"

modifier: "private"     -> private_modifier
        | "public"      -> public_modifier
        | "protected"   -> protected_modifier
        | "const"       -> const_modifier
        | "constexpr"   -> constexpr_modifier
        | "consteval"   -> consteval_modifier
        | "static"      -> static_modifier
        | "abstract"    -> abstract_modifier
        | "override"    -> override_modifier
        | "virtual"     -> virtual_modifier

comment: LINE_COMMENT | BLOCK_COMMENT
cpp_block: CPP_BLOCK

COMP_OP: "==" | "!=" | "<" | ">" | "<=" | ">="
BIN_OP: "+" | "-" | "*" | "/" | "%" | "&" | "|" | "^" | "<<" | ">>" | "&&" | "||"
       | "+=" | "-=" | "*=" | "/=" | "%=" | "&=" | "|=" | "^=" | "<<=" | ">>="
UNARY_OP: "!" | "-" | "+" | "~"

TYPE: /[A-Za-z_][A-Za-z0-9_<>,\s]*/  // Handles complex types like list<int>, Map<string, int>
ID: /[A-Za-z_][A-Za-z0-9_]*/
NUMBER: /[0-9]+(\.[0-9]+)?([eE][+-]?[0-9]+)?/
STRING: /"([^"\\]|\\.)*"/
RAW_STRING: /R"([^"\\]|\\.)*"/
INTERP_STRING: /\$"([^"\\]|\\.)*"/
BOOLEAN: "true" | "false"
LINE_COMMENT: /\/\/[^\n]*/
BLOCK_COMMENT: /\/\*.*?\*\//
CPP_BLOCK: /__CPP_BLOCK_\d+__/

NEWLINE: /\n+/
%ignore " "
%ignore "\t"
"""

TEST = r"""
func linearSearch<T>(const list<T>& arr, const T& target> -> union<int, string> {
    for (int i = 0; i < arr.size(); ++i) {
        if (arr[i] == target) { return i; }
    }
    return "Not in iterable!"
}


// Main access
main:
    list<int> my_list = [1, 3, 99, 41, 42, 24, 11, 67, 69, 360]
    @cpp { std::cout << "41 is at index" << linearSearch(my_list, 41) << std::endl; }
    @cpp { std::cout << "100 is at index" << linearSearch(my_list, 100) << std::endl; }
"""

# -------------------- Preprocessor for balanced @cpp { ... } blocks --------------------
def extract_cpp_blocks(source: str, marker: str = "@cpp") -> Tuple[str, Dict[str, str]]:
    """Replace each @cpp { ... } balanced block with a placeholder: __CPP_BLOCK_n__"""
    out_parts = []
    i = 0
    n = len(source)
    mapping: Dict[str, str] = {}
    placeholder_index = 0

    while i < n:
        m = re.search(re.escape(marker) + r'\b', source[i:])
        if not m:
            out_parts.append(source[i:])
            break
        start = i + m.start()
        out_parts.append(source[i:start])
        j = start + len(m.group(0))

        while j < n and source[j].isspace():
            j += 1

        if j >= n or source[j] != '{':
            out_parts.append(source[start:start+len(m.group(0))])
            i = start + len(m.group(0))
            continue

        k = j
        depth = 0
        in_string = False
        string_delim = ''
        in_char = False
        escaped = False
        in_line_comment = False
        in_block_comment = False

        while k < n:
            ch = source[k]
            nxt = source[k+1] if k+1 < n else ''
            if in_line_comment:
                if ch == '\n':
                    in_line_comment = False
            elif in_block_comment:
                if ch == '*' and nxt == '/':
                    in_block_comment = False
                    k += 1
            elif in_string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == string_delim:
                    in_string = False
            elif in_char:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == "'":
                    in_char = False
            else:
                if ch == '/' and nxt == '/':
                    in_line_comment = True
                    k += 1
                elif ch == '/' and nxt == '*':
                    in_block_comment = True
                    k += 1
                elif ch == '"':
                    in_string = True
                    string_delim = '"'
                elif ch == "'":
                    in_char = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        k += 1
                        break
            k += 1

        if depth != 0:
            out_parts.append(source[start:])
            i = n
            break

        block = source[start:k]
        brace_pos = block.find('{')
        block_only = block[brace_pos:]  # include { ... }
        placeholder = f"__CPP_BLOCK_{placeholder_index}__"
        mapping[placeholder] = block_only
        out_parts.append(placeholder)
        placeholder_index += 1
        i = k

    merged = ''.join(out_parts)
    return merged, mapping

# -------------------- C++ Block Cleaner --------------------
def clean_block(block: str) -> str:
    # Preserve comment markers and avoid stripping content too aggressively.
    if not block:
        return ""

    # Remove exactly one outer pair of braces if present (keep interior spacing)
    first = block.find('{')
    last = block.rfind('}')
    if first != -1 and last != -1 and first < last:
        inner = block[first+1:last]
    else:
        inner = block

    # Keep original leading spaces; split into lines and trim only blank leading/trailing lines
    lines = inner.splitlines()
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    if not lines:
        return ""

    # Compute minimum indentation from non-empty, non-comment lines
    indents = []
    for line in lines:
        if line.strip() and not line.strip().startswith("//"):
            indents.append(len(line) - len(line.lstrip()))

    min_indent = min(indents) if indents else 0

    # Remove that many spaces from every line when possible (leave short/comment lines intact)
    new_lines = [
        (line[min_indent:] if len(line) >= min_indent else line)
        for line in lines
    ]

    return "\n".join(new_lines).rstrip()

# -------------------- Lark Transformer --------------------

def main():
    test_source = TEST
    processed_source, cpp_mapping = extract_cpp_blocks(test_source)

    # Clean each extracted C++ block
    for key in cpp_mapping:
        cpp_mapping[key] = clean_block(cpp_mapping[key])

    print("Processed Source:")
    print(processed_source)
    print("\nC++ Blocks:")
    for key, block in cpp_mapping.items():
        print(f"{key}:\n{block}\n")

if __name__ == "__main__":
    main()
