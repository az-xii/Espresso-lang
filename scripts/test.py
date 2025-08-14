#! venv/bin/python3
"""
az_lexer.py

A tokenizer for the "AZ" language using Lark.

Save and run:
    pip install lark-parser
    python az_lexer.py path/to/source.az

If no file is given the embedded sample (from your prompt) is used.

Produces a token stream (type, value, line, column). By default prints a friendly table;
use --json to emit a JSON list.

Design notes:
 - @cpp { ... } blocks are extracted via a preprocessor that matches balanced braces
   (and attempts to respect strings and comments inside those blocks).
 - The Lark grammar is token-focused (start: (TOKEN)*). We use parser.lex() to obtain tokens.
 - Multi-character operators are declared before single-char ones to ensure correct lexing.
"""

from __future__ import annotations
import re
import sys
import json
import argparse
from typing import Tuple, Dict, Iterable
from lark import Lark, Token, UnexpectedInput

# -------------------- Sample (used when no file is provided) --------------------
SAMPLE = r"""
// ==== Level 1. Hello World (Basic I/O) ====
@include <iostream>
main:
    io::Output("Hello, world!")

    // Input example
    string name = io::Input("Enter your name: ")
    std::cout << $"Hello, {name}!" << std::endl

    // Write to file
    string data = "Sample data\nSecond line"
    io::File file = Open("output.text", "rw")

    // Read from file
    string content = file.Read()
    io::Output("File content:")
    io::Output(content)
    return 0
"""

# -------------------- Preprocessor for balanced @cpp { ... } blocks --------------------
def extract_cpp_blocks(source: str, marker: str = "@cpp") -> Tuple[str, Dict[str, str]]:
    """
    Replace each @cpp { ... } balanced block with a placeholder: __CPP_BLOCK_n__
    and return (transformed_source, mapping_of_placeholders_to_blocks).

    This attempts to correctly handle nested braces and ignores braces found
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

        # if there is no opening brace, treat it as a plain token and continue
        if j >= n or source[j] != '{':
            out_parts.append(source[start:start+len(m.group(0))])
            i = start + len(m.group(0))
            continue

        # find balanced closing brace (respect strings and comments)
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
                # not inside a quote/comment
                if ch == '/' and nxt == '/':
                    in_line_comment = True
                    k += 1
                elif ch == '/' and nxt == '*':
                    in_block_comment = True
                    k += 1
                elif ch == '"' or ch == "'":
                    if ch == '"':
                        in_string = True
                        string_delim = '"'
                    else:
                        in_char = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        k += 1  # include the closing brace
                        break
            k += 1

        if depth != 0:
            # unbalanced block: stop and append remainder
            out_parts.append(source[start:])
            i = n
            break

        block = source[start:k]
        placeholder = f"__CPP_BLOCK_{placeholder_index}__"
        mapping[placeholder] = block
        out_parts.append(placeholder)
        placeholder_index += 1
        i = k

    merged = ''.join(out_parts)
    return merged, mapping

# -------------------- Lark grammar (token focused) --------------------
GRAMMAR = r"""
start: (TOKEN)*

TOKEN: CPP_BLOCK
     | LINE_COMMENT
     | C_BLOCK_COMMENT
     | INTERP_STRING
     | STRING
     | FLOAT
     | NUMBER
     | AT_DIRECTIVE
     | ANGLE_PATH
     | OP_MULTI
     | OP_SINGLE
     | IDENT
     | SYMBOL

// placeholders for pre-extracted C++ blocks
CPP_BLOCK: /__CPP_BLOCK_\d+__/

// Comments
LINE_COMMENT: /\/\/[^\n]*/
C_BLOCK_COMMENT: /\/\*([^*]|\*(?!\/))*\*\//

// Strings: interpolated ($"...") before plain
INTERP_STRING: /\$"([^"\\]|\\.)*"/
STRING: /"([^"\\]|\\.)*"/

// Numbers: floats and integers (floats allow suffixes like f32)
FLOAT: /\d+\.\d+([eE][+-]?\d+)?[A-Za-z0-9_]*/
NUMBER: /\d+([eE][+-]?\d+)?/

// @directives and includes
AT_DIRECTIVE: /@[A-Za-z_]\w*(::[A-Za-z_]\w*)?/
ANGLE_PATH: /<[^>\n]+>/

// Operators (multi-char first)
OP_MULTI: /::|->|=>|\+\+|--|\+=|-=|\*=|\/=|==|!=|<=|>=|\|\||&&|<<|>>|\?|\:/
OP_SINGLE: /[+\-*\/\%=<>!&|^~]/

IDENT: /[A-Za-z_][A-Za-z0-9_]*/
SYMBOL: /[()\[\]{},.;:@]/

%import common.WS
%ignore WS
"""

# -------------------- Tokenization helper --------------------
def build_parser() -> Lark:
    """Build and return a Lark instance used only for lexing."""
    return Lark(GRAMMAR, start='start', parser='lalr', lexer='contextual', propagate_positions=True)

def lex_source(source: str, include_comments: bool = True):
    """
    Yield tokens as dicts {type, value, line, column}. If include_comments is False,
    skip comment tokens.
    """
    preprocessed, cpp_map = extract_cpp_blocks(source)
    parser = build_parser()
    try:
        stream = parser.lex(preprocessed)
    except UnexpectedInput as e:
        raise RuntimeError(f"Lexing failed: {e!s}")

    for tok in stream:
        # tok is a lark.Token object
        val = tok.value
        if tok.type == 'CPP_BLOCK' and val in cpp_map:
            val = cpp_map[val]
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

    # pretty print
    for t in tokens:
        v = t["value"]
        vs = v.replace("\n", "\\n")
        if len(vs) > args.max:
            vs = vs[:args.max-3] + "..."
        print(f"{t['type']:15} (line {t['line']:>3}, col {t['column']:>2})  {vs}")

if __name__ == "__main__":
    main()