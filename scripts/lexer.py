#! venv/bin/python3
from __future__ import annotations
from calendar import c
import re
import json
import sys
import os.path
import argparse
import textwrap
from typing import Tuple, Dict, Iterable, List
from lark import Lark, UnexpectedInput
from dataclasses import dataclass

__all__ = ["Lexer", "Token"]

SAMPLE = r"""
func main() -> int {
    runtime::Output("Hello, World")
}
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

# -------------------- Grammar --------------------
GRAMMAR = r"""
start: (CPP_BLOCK | LITERAL | COMMENTS | DECOR | TYPE | KEYW | OP | PATH | DELIM | ANGLE_PATH)*

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
C_BLOCK_COMMENT: /\/\*([^\*]|\*(?!\/))*\*\//
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

TYPE.10: "byte" | "short" | "int" | "long" | "ubyte" | "ushort" | "ulong"
    | "float" | "double" | "fixed16_16" | "fixed32_32" | "char" | "string"
    | "bool" | "void" | "any" | "list" | "collection" | "map" | "set"
    | "tuple" | "auto" | "union" | "lambda"

KEYW.10: "func" | "class" | "this" | "super" | "private" | "public" | "protected"
    | "const" | "consteval" | "constexpr" | "static" | "override" | "virtual"
    | "if" | "elif" | "else" | "switch" | "case" | "while" | "for" | "in"
    | "break" | "continue" | "try" | "catch" | "throw" | "main" | "return" | "main"

OP: OP_MULTI | OP_SINGLE
OP_MULTI: "::" | "->" | "=>" | "++" | "--" | "+=" | "-=" | "*=" | "/="
        | "==" | "!=" | "<=" | ">=" | "||" | "&&" | "<<" | ">>" | ".." 
        | "->"
OP_SINGLE: /[+\-*\/%=<>!&|^~]/

# PATH: identifiers that may include ::, ., -> separators and simple [index] parts.
# Note: this is intended to cover common path forms like `runtime::Output`, `obj.field`, `ptr->field`, `mydict[key]`.
PATH: /[A-Za-z_][A-Za-z0-9_]*(?:(?:(?:::)|->|\.)[A-Za-z_][A-Za-z0-9_]*)*(?:\[[^\]\n]+\])*/

DELIM: "(" | ")" | "[" | "]" | "{" | "}" | "," | ";" | ":" | "?" | "." 

ANGLE_PATH: /<[^>\n]+>/


%import common.WS
%ignore WS
"""

def build_parser() -> Lark:
    return Lark(GRAMMAR, start='start', parser='lalr', lexer='contextual', propagate_positions=True)



# -------------------- Token class --------------------
@dataclass(frozen=True)
class Token:
    type: str
    line: int
    col: int
    val: str

    def as_tuple(self):
        return (self.type, self.line, self.col, self.val)

    def as_json(self):
        return {"type": self.type, "line": self.line, "col": self.col, "value": self.val}

# -------------------- Lexer class --------------------
class Lexer:
    @staticmethod
    def lex_source(source: str, include_comments: bool = True) -> Tuple[List[Token], List[str]]:
        """
        :param source: AZ source code
        :param include_comments: whether to include comments in token stream
        :return: (tokens, cpp_blocks)
                 where tokens = [(type, line, column, value)] and value for CPP_BLOCK is an integer index
                       cpp_blocks = list of raw C++ block strings
        """
        preprocessed, cpp_map = extract_cpp_blocks(source)
        parser = build_parser()
        try:
            stream = parser.lex(preprocessed)
        except UnexpectedInput as e:
            raise RuntimeError(f"Lexing failed: {e!s}")

        # Collect raw tokens first (so we can inspect lookahead)
        raw = list(stream)

        # First pass: map CPP_BLOCK placeholders -> stored blocks, optionally drop comments
        interim: List[dict] = []
        cpp_blocks: List[str] = []
        for tok in raw:
            val = tok.value
            if tok.type == 'CPP_BLOCK':
                idx = len(cpp_blocks)
                cpp_blocks.append(cpp_map[val])
                val = str(idx)
            if not include_comments and tok.type in ('LINE_COMMENT', 'C_BLOCK_COMMENT'):
                continue
            interim.append({"type": tok.type, "line": tok.line, "col": tok.column, "val": val})

        # Second pass: merge patterns like ID|TYPE + ANGLE_PATH into a single TYPE token.
        # This handles `list<int>`, `Rocket<Satellite>`, `Map<string, list<int>>` (if ANGLE_PATH already contains the inner text).
        tokens: List[Tuple[str,int,int,str]] = []
        i = 0
        while i < len(interim):
            t = interim[i]
            # merge when a base identifier/type is immediately followed by an ANGLE_PATH token
            if t["type"] in ("PATH", "TYPE") and i + 1 < len(interim) and interim[i+1]["type"] == "ANGLE_PATH":
                combined = f"{t['val']}{interim[i+1]['val']}"
                tokens.append(Token("TYPE", t["line"], t["col"], combined))
                i += 2
                continue
            tokens.append(Token(t["type"], t["line"], t["col"], t["val"]))
            i += 1
        
        # Third pass: convert C++ block into raw strings
        cpp_blocks = [clean_block(b) for b in cpp_blocks]
            
        return tokens, cpp_blocks


    @staticmethod
    def lex_source_as_json(source: str, include_comments: bool = True) -> str:
        """
        Lex source code and return JSON representation of tokens and C++ blocks.
        :param source: AZ source code
        :param include_comments: whether to include comments in token stream
        :return: JSON string with tokens and cpp_blocks
        """
        tokens, cpp_blocks = Lexer.lex_source(source, include_comments)
        return json.dumps({"tokens": tokens, "cpp_blocks": cpp_blocks}, indent=2, ensure_ascii=False)
    
    @staticmethod
    def lex_source_from_file(file_path: str, include_comments: bool = True) -> Tuple[List[Token], List[str]]:
        """
        Lex source code from a file and return tokens and C++ blocks.
        :param file_path: path to the source file
        :param include_comments: whether to include comments in token stream
        :return: (tokens, cpp_blocks)
                 where tokens = [(type, line, column, value)] and value for CPP_BLOCK is an integer index
                       cpp_blocks = list of raw C++ block strings
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")
        if not os.path.isfile(file_path):
            raise ValueError(f"Expected a file, but got a directory: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        return Lexer.lex_source(source, include_comments)

# -------------------- CLI --------------------
def main(argv: Iterable[str] = None):
    ap = argparse.ArgumentParser(description="Tokenize an AZ source file using Lark.")
    ap.add_argument("file", nargs="?", help="Source file path. If omitted uses embedded sample.")
    ap.add_argument("--json", action="store_true", help="Emit JSON list of tokens.")
    ap.add_argument("--encoding", default="utf-8", help="File encoding (default: utf-8).")
    ap.add_argument("--max", type=int, default=120, help="Max length of printed token.value (when not using --json).")
    ap.add_argument("--no-comments", action="store_true", help="Remove comment tokens from output.")
    args = ap.parse_args(list(argv) if argv is not None else None)

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: Source file not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        if not os.path.isfile(args.file):
            print(f"Error: Expected a file, but got a directory: {args.file}", file=sys.stderr)
            sys.exit(1)
        encoding = args.encoding if args.encoding else "utf-8"
        text = open(args.file, "r", encoding=encoding).read()
    else:
        text = SAMPLE

    try:
        tokens, blocks = Lexer.lex_source(text, include_comments=not args.no_comments)
    except RuntimeError as e:
        print("Error during lexing:", e, file=sys.stderr)
        sys.exit(2)

    if args.json:
        print(json.dumps((tokens, blocks), indent=2, ensure_ascii=False))
        return
    
    print("Tokens:")
    for t in tokens:
        print(t.as_tuple())

    print("\nC++ Blocks:")
    for i, b in enumerate(blocks):
        print(f"[{i}]\n{b}")


if __name__ == "__main__":
    main()
