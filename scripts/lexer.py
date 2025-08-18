#! venv/bin/python3
"""
az_lexer.py

A tokenizer for the "AZ" language using Lark.

Save and run:
    pip install lark-parser
    python az_lexer.py path/to/source.az

If no file is given the embedded sample is used.

Produces a token stream (type, value, line, column). By default prints a friendly table;
use --json to emit a JSON list.
"""

from __future__ import annotations
import re
import sys
import json
import argparse
from typing import Tuple, Dict, Iterable
from lark import Lark, Token, UnexpectedInput

# -------------------- Sample --------------------
SAMPLE = r"""
// ==== Level 6. C++ interop ====

@include <iostream>
@using namespace std
@cpp {
    // Pure C++. Need C++ syntax, not Espresso
    bool is_prime(int n) {
        if n < 2 {
            return false;
        }
        for int i = 2; i <= int(math::sqrt(n)); i+=1 {
            if n % i == 0 {
                return false;
            }
        }
        return true;
    }
}

main: 
    list<int> primes = []

    for int num = 0, num < 50, num += 1 {
        if is_prime(num) {
            primes.append(num)
        }
    }

    cout << $"Primes under 50: {primes.Join(", ")}" << endl

    return 0
"""

# -------------------- Preprocessor for balanced @cpp { ... } blocks --------------------
def extract_cpp_blocks(source: str, marker: str = "@cpp") -> Tuple[str, Dict[str, str]]:
    """
    Replace each @cpp { ... } balanced block with a placeholder: __CPP_BLOCK_n__
    and return (transformed_source, mapping_of_placeholders_to_blocks).

    Attempts to correctly handle nested braces and ignores braces found
    inside strings or comments inside the block.
    """
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
        out_parts.append(source[i:start])     # text before marker
        j = start + len(m.group(0))

        # skip whitespace
        while j < n and source[j].isspace():
            j += 1

        # if there is no opening brace, treat as plain token
        if j >= n or source[j] != '{':
            out_parts.append(source[start:start+len(m.group(0))])
            i = start + len(m.group(0))
            continue

        # find balanced closing brace
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
        block_only = block[brace_pos:]  # remove "@cpp" marker
        placeholder = f"__CPP_BLOCK_{placeholder_index}__"
        mapping[placeholder] = block_only
        out_parts.append(placeholder)
        placeholder_index += 1
        i = k

    merged = ''.join(out_parts)
    return merged, mapping

# -------------------- Lark grammar --------------------
GRAMMAR = r"""
start: (CPP_BLOCK | LITERAL | COMMENTS | DECOR | TYPE | KEYW | OP | ID | DELIM | MISC)*

CPP_BLOCK.10: /__CPP_BLOCK_\d+__/

LITERAL: LINE_COMMENT
       | C_BLOCK_COMMENT  
       | RAW_STRING
       | INTERP_STRING
       | STRING
       | CHAR
       | DECIMAL
       | BINARY
       | HEX
       | OCT
       | INTEGER
       | BOOLEAN

COMMENTS: LINE_COMMENT | C_BLOCK_COMMENT

LINE_COMMENT: /\/\/[^\n]*/
C_BLOCK_COMMENT: /\/\*([^*]|\*(?!\/))*\*\//
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

DECOR: "@include" | "@using" | "@alias" | "@namespace" | "@assert" 
     | "@define" | "@panic" | "@cpp" | "@operator" | "@cast"

TYPE: "byte" | "short" | "int" | "long" | "ubyte" | "ushort" | "ulong"
    | "float" | "double" | "fixed16_16" | "fixed32_32" | "char" | "string"
    | "bool" | "void" | "any" | "list" | "collection" | "map" | "set"
    | "tuple" | "auto" | "union" | "lambda"

KEYW: "func" | "class" | "this" | "super" | "private" | "public" | "protected"
    | "const" | "consteval" | "constexpr" | "static" | "override" | "virtual"
    | "if" | "elif" | "else" | "switch" | "case" | "while" | "for" | "in"
    | "break" | "continue" | "try" | "catch" | "throw" | "main" | "return"
    | "namespace"

OP: OP_MULTI | OP_SINGLE
OP_MULTI: "::" | "->" | "=>" | "++" | "--" | "+=" | "-=" | "*=" | "/="
        | "==" | "!=" | "<=" | ">=" | "||" | "&&" | "<<" | ">>"
OP_SINGLE: /[+\-*\/\%=<>!&|^~]/

ID: /[A-Za-z_][A-Za-z0-9_]*/

DELIM: "(" | ")" | "[" | "]" | "{" | "}" | "," | ";" | ":" | "<" | ">"

MISC: ANGLE_PATH | QUESTION | DOT
ANGLE_PATH: /<[^>\n]+>/
QUESTION: "?"
DOT: "."

%import common.WS
%ignore WS
"""

# -------------------- Tokenization helper --------------------
def build_parser() -> Lark:
    return Lark(GRAMMAR, start='start', parser='lalr', lexer='contextual', propagate_positions=True)

def lex_source(source: str, include_comments: bool = True):
    preprocessed, cpp_map = extract_cpp_blocks(source)
    parser = build_parser()
    try:
        stream = parser.lex(preprocessed)
    except UnexpectedInput as e:
        raise RuntimeError(f"Lexing failed: {e!s}")

    for tok in stream:
        val = tok.value
        if tok.type == 'CPP_BLOCK' and tok.value in cpp_map:
            val = cpp_map[tok.value]
        if not include_comments and tok.type in ('LINE_COMMENT', 'C_BLOCK_COMMENT'):
            continue
        yield {
            "type": tok.type,
            "value": val,
            "line": getattr(tok, "line", None),
            "column": getattr(tok, "column", None),
        }

# -------------------- CLI --------------------
def main(argv: Iterable[str] = None):
    ap = argparse.ArgumentParser(description="Tokenize an AZ source file using Lark.")
    ap.add_argument("file", nargs="?", help="Source file path. If omitted uses embedded sample.")
    ap.add_argument("--json", action="store_true", help="Emit JSON list of tokens.")
    ap.add_argument("--max", type=int, default=120, help="Max length of printed token.value (when not using --json).")
    ap.add_argument("--no-comments", action="store_true", help="Remove comment tokens from output.")
    args = ap.parse_args(list(argv) if argv is not None else None)

    if args.file:
        text = open(args.file, "r", encoding="utf-8").read()
    else:
        text = SAMPLE

    try:
        tokens = list(lex_source(text, include_comments=not args.no_comments))
    except RuntimeError as e:
        print("Error during lexing:", e, file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
        return

    for t in tokens:
        v = t["value"]
        vs = v.replace("\n", "\\n")
        if len(vs) > args.max:
            vs = vs[:args.max-3] + "..."
        print(f"{t['type']:15} (line {t['line']:>3}, col {t['column']:>2})  {vs}")

if __name__ == "__main__":
    main()
