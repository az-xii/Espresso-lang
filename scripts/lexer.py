#! venv/bin/python3
from __future__ import annotations
import re
import json
import sys
import os.path
from typing import Tuple, Dict, Iterable, List
from lark import Lark, UnexpectedInput
from dataclasses import dataclass

SAMPLE = r"""
func linearSearch<T>(const list<T>& nums, const T& target> -> union<int, string> {
    for (int i = 0; i < nums.size(); ++i) {
        if (nums[i] == target) { return i; }
    }
    return "Not in iterable!"
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

# -------------------- Preprocessor for splitting tokens --------------------
def split_tokens(tokens: List[Token]) -> List[Tuple[Token]]:
    """Split tokens at line breaks, returning a list of lines with their tokens."""
    lines: List[List[Token]] = []
    line_count = max(t.line for t in tokens) if tokens else 0

    if line_count == 0:
        return []
    
    for i in range(1, line_count + 1):
        line_tokens = [t for t in tokens if t.line == i]
        lines.append(line_tokens)
    return lines

# -------------------- Grammar --------------------
GRAMMAR = r"""
start: (CPP_BLOCK | LITERAL | COMMENTS | DECOR | TYPE | KEYW | OP | PATH | DELIM | ANGLE_PATH)*

CPP_BLOCK.10: /__CPP_BLOCK_\d+__/

LITERAL: RAW_STRING
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
     | "@define" | "@panic" | "@cpp" | "@operator" | "@cast" | "@usingns"

TYPE.10: "byte" | "short" | "int" | "long" | "ubyte" | "ushort" | "ulong"
    | "float" | "double" | "fixed16_16" | "fixed32_32" | "char" | "string"
    | "bool" | "void" | "any" | "list" | "collection" | "map" | "set"
    | "tuple" | "auto" | "union" | "lambda"

KEYW.10: "func" | "class" | "this" | "super" | "private" | "public" | "protected"
    | "const" | "consteval" | "constexpr" | "static" | "override" | "virtual"
    | "if" | "elif" | "else" | "switch" | "case" | "while" | "for" | "in"
    | "break" | "continue" | "try" | "catch" | "throw" | "main:" | "return"

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

    text = SAMPLE

    try:
        tokens, blocks = Lexer.lex_source(text)
        print(tokens)
        print(blocks)
    except RuntimeError as e:
        print("Error during lexing:", e, file=sys.stderr)
        sys.exit(2)
    
    lines = split_tokens(tokens)
    print(f"Tokens -- {len(lines)} line(s):")
    for i, line in enumerate(lines, start=1):
        print(f"   {i} | ", end="")
        print(" ".join(f"{t.type}('{t.val}')" for t in line))

    print("\nC++ Blocks:")
    for i, b in enumerate(blocks):
        print(f"[{i}]\n{b}")

if __name__ == "__main__":
    main()