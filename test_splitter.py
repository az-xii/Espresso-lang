import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class StatementType(Enum):
    FUNCTION_DECL = "function_decl"
    CLASS_DECL = "class_decl" 
    MAIN_BLOCK = "main_block"
    VARIABLE_DECL = "variable_decl"
    VARIABLE_ASSIGN = "variable_assignment"
    ANNOTATION = "annotation"
    COMMENT = "comment"
    CPP_BLOCK = "cpp_block"
    EXPRESSION = "expression"
    CONTROL_FLOW = "control_flow"  # if, while, for, etc.
    UNKNOWN = "unknown"

@dataclass
class StatementBlock:
    type: StatementType
    content: str
    line_start: int
    line_end: int
    indent_level: int = 0

class StatementSplitter:
    def __init__(self):
        self.cpp_blocks: Dict[str, str] = {}
        
    def split_statements(self, source: str, cpp_blocks: Dict[str, str] = None) -> List[StatementBlock]:
        """Split source code into logical statement blocks"""
        self.cpp_blocks = cpp_blocks or {}
        
        lines = source.split('\n')
        statements = []
        i = 0
        
        while i < len(lines):
            line = lines[i].rstrip()  # Only strip right side to preserve leading whitespace
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
                
            # Handle inline comments by splitting code from comment
            if '//' in line:
                # Split on the first '//' that's not inside a string
                comment_index = self._find_comment_start(line)
                if comment_index >= 0:
                    code_part = line[:comment_index].rstrip()
                    comment_part = line[comment_index:].strip()
                    
                    if code_part:
                        # Process the code part as a separate statement
                        code_stmt = self._process_line(code_part, lines, i)
                        if code_stmt:
                            statements.append(code_stmt)
                    
                    # Add the comment part
                    statements.append(StatementBlock(
                        type=StatementType.COMMENT,
                        content=comment_part,
                        line_start=i,
                        line_end=i,
                        indent_level=len(line) - len(line.lstrip())
                    ))
                    
                    i += 1
                    continue
            
            # Handle multi-line comments
            if '/*' in line:
                comment_index = line.find('/*')
                if comment_index >= 0:
                    # Check if there's code before the comment
                    code_part = line[:comment_index].rstrip()
                    if code_part:
                        code_stmt = self._process_line(code_part, lines, i)
                        if code_stmt:
                            statements.append(code_stmt)
                    
                    # Extract the multi-line comment
                    comment_lines, end_line = self._extract_multi_line_comment(lines, i, comment_index)
                    statements.append(StatementBlock(
                        type=StatementType.COMMENT,
                        content='\n'.join(comment_lines),
                        line_start=i,
                        line_end=end_line,
                        indent_level=len(line) - len(line.lstrip())
                    ))
                    i = end_line + 1
                    continue
            
            # Process the line normally (no inline comments)
            stmt = self._process_line(line, lines, i)
            if stmt:
                statements.append(stmt)
                if stmt.line_end > i:
                    i = stmt.line_end
            i += 1
            
        return statements
    
    def _process_line(self, line: str, lines: List[str], current_line: int) -> Optional[StatementBlock]:
        """Process a single line or multi-line construct"""
        stripped = line.strip()
        
        if not stripped:
            return None
            
        # Handle multi-line constructs
        if stripped.startswith('func '):
            block, end_line = self._extract_braced_block(lines, current_line)
            return StatementBlock(
                type=StatementType.FUNCTION_DECL,
                content=block,
                line_start=current_line,
                line_end=end_line,
                indent_level=len(line) - len(line.lstrip())
            )
                
        if stripped.startswith('class '):
            block, end_line = self._extract_braced_block(lines, current_line)
            return StatementBlock(
                type=StatementType.CLASS_DECL,
                content=block,
                line_start=current_line,
                line_end=end_line,
                indent_level=len(line) - len(line.lstrip())
            )
                
        if stripped.startswith('main:'):
            block, end_line = self._extract_main_block(lines, current_line)
            return StatementBlock(
                type=StatementType.MAIN_BLOCK,
                content=block,
                line_start=current_line,
                line_end=end_line,
                indent_level=len(line) - len(line.lstrip())
            )
                
        # Handle control flow (if, while, for, etc.)
        if self._is_control_flow_start(stripped):
            block, end_line = self._extract_braced_block(lines, current_line)
            return StatementBlock(
                type=StatementType.CONTROL_FLOW,
                content=block,
                line_start=current_line,
                line_end=end_line,
                indent_level=len(line) - len(line.lstrip())
            )
                
        # Handle annotations
        if stripped.startswith('@'):
            if '{' in stripped:  # Multi-line annotation
                block, end_line = self._extract_braced_block(lines, current_line)
                return StatementBlock(
                    type=StatementType.ANNOTATION,
                    content=block,
                    line_start=current_line,
                    line_end=end_line,
                    indent_level=len(line) - len(line.lstrip())
                )
            else:  # Single-line annotation
                return StatementBlock(
                    type=StatementType.ANNOTATION,
                    content=line,
                    line_start=current_line,
                    line_end=current_line,
                    indent_level=len(line) - len(line.lstrip())
                )
                
        # Handle C++ blocks
        if '__CPP_BLOCK_' in stripped:
            return StatementBlock(
                type=StatementType.CPP_BLOCK,
                content=line,
                line_start=current_line,
                line_end=current_line,
                indent_level=len(line) - len(line.lstrip())
            )
        
        # Handle multi-line data structures (like your map example)
        if self._is_multi_line_data_structure(lines, current_line):
            block, end_line = self._extract_data_structure(lines, current_line)
            return StatementBlock(
                type=self._classify_statement(block.split('\n')[0].strip()),
                content=block,
                line_start=current_line,
                line_end=end_line,
                indent_level=len(line) - len(line.lstrip())
            )
                
        # Handle single-line statements
        stmt_type = self._classify_statement(stripped)
        return StatementBlock(
            type=stmt_type,
            content=line,
            line_start=current_line,
            line_end=current_line,
            indent_level=len(line) - len(line.lstrip())
        )
    
    def _find_comment_start(self, line: str) -> int:
        """Find the start of a comment, avoiding false positives in strings"""
        in_string = False
        string_char = None
        escaped = False
        
        for i, char in enumerate(line):
            if escaped:
                escaped = False
                continue
                
            if char == '\\':
                escaped = True
                continue
                
            if not in_string and char in ['"', "'"]:
                in_string = True
                string_char = char
            elif in_string and char == string_char:
                in_string = False
                string_char = None
            elif not in_string and char == '/' and i + 1 < len(line) and line[i+1] == '/':
                return i
                
        return -1
    
    def _extract_multi_line_comment(self, lines: List[str], start_line: int, start_index: int) -> Tuple[List[str], int]:
        """Extract a multi-line comment block"""
        comment_lines = []
        first_line = lines[start_line]
        
        # Handle the first line
        if start_index > 0:
            comment_lines.append(first_line[start_index:])
        else:
            comment_lines.append(first_line)
        
        # Check if comment ends on the same line
        if '*/' in first_line[start_index:]:
            return comment_lines, start_line
            
        # Continue through subsequent lines
        i = start_line + 1
        while i < len(lines):
            line = lines[i]
            comment_lines.append(line)
            
            if '*/' in line:
                break
            i += 1
            
        return comment_lines, i
    
    def _is_multi_line_data_structure(self, lines: List[str], start_line: int) -> bool:
        """Check if this line starts a multi-line data structure"""
        line = lines[start_line].strip()
        
        # Look for patterns like: type name = { ... }
        if re.match(r'^\w+<\w+(\s*,\s*\w+)*>\s+\w+\s*=', line) or re.match(r'^\w+\s+\w+\s*=', line):
            if '{' in line and '}' not in line:
                return True
            # Check if the next line starts with brace or indented content
            if start_line + 1 < len(lines):
                next_line = lines[start_line + 1].strip()
                if next_line.startswith('{') or (next_line and len(lines[start_line + 1]) - len(lines[start_line + 1].lstrip()) > 0):
                    return True
        return False
    
    def _extract_data_structure(self, lines: List[str], start_line: int) -> Tuple[str, int]:
        """Extract a multi-line data structure like map, list, etc."""
        content_lines = [lines[start_line]]
        brace_count = 0
        in_string = False
        string_char = None
        escaped = False
        
        # Count initial braces in first line
        first_line = lines[start_line]
        for char in first_line:
            if escaped:
                escaped = False
                continue
            if char == '\\':
                escaped = True
                continue
            if not in_string and char == '{':
                brace_count += 1
            elif not in_string and char == '}':
                brace_count -= 1
            elif char in ['"', "'"] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
        
        i = start_line
        while brace_count > 0 and i + 1 < len(lines):
            i += 1
            line = lines[i]
            content_lines.append(line)
            
            # Count braces in this line, avoiding strings
            in_string = False
            string_char = None
            escaped = False
            
            for char in line:
                if escaped:
                    escaped = False
                    continue
                if char == '\\':
                    escaped = True
                    continue
                if not in_string and char == '{':
                    brace_count += 1
                elif not in_string and char == '}':
                    brace_count -= 1
                elif char in ['"', "'"] and not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char and in_string:
                    in_string = False
                    string_char = None
                
                if brace_count == 0:
                    break
        
        return '\n'.join(content_lines), i
    
    def _extract_function_block(self, lines: List[str], start_line: int) -> Tuple[str, int]:
        """Extract a complete function declaration with its body"""
        return self._extract_braced_block(lines, start_line)
    
    def _extract_class_block(self, lines: List[str], start_line: int) -> Tuple[str, int]:
        """Extract a complete class declaration with its body"""  
        return self._extract_braced_block(lines, start_line)
    
    def _extract_main_block(self, lines: List[str], start_line: int) -> Tuple[str, int]:
        """Extract main block - could be indented statements or braced"""
        main_line = lines[start_line].strip()
        
        # Check if main: is followed by a brace on same line or next line
        if '{' in main_line:
            return self._extract_braced_block(lines, start_line)
            
        # Check if next non-empty line has a brace
        i = start_line + 1
        while i < len(lines) and not lines[i].strip():
            i += 1
            
        if i < len(lines) and lines[i].strip() == '{':
            # Treat the brace as part of main block
            return self._extract_braced_block(lines, start_line, brace_line=i)
            
        # No braces - collect indented statements
        content_lines = [lines[start_line]]  # Include main: line
        i = start_line + 1
        base_indent = None
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                content_lines.append(line)
                i += 1
                continue
                
            # Calculate indentation
            indent = len(line) - len(line.lstrip())
            
            # Set base indentation from first non-empty line
            if base_indent is None and stripped:
                base_indent = indent
                
            # If we hit a line with less indentation than base, we're done
            if stripped and base_indent is not None and indent <= 0:
                break
                
            content_lines.append(line)
            i += 1
            
        return '\n'.join(content_lines), i - 1
    
    def _extract_braced_block(self, lines: List[str], start_line: int, brace_line: Optional[int] = None) -> Tuple[str, int]:
        """Extract a block delimited by braces, handling nesting"""
        content_lines = []
        brace_count = 0
        found_opening_brace = False
        
        # If brace_line is specified, start from there for brace counting
        brace_start = brace_line if brace_line is not None else start_line
        
        for i in range(start_line, len(lines)):
            line = lines[i]
            content_lines.append(line)
            
            # Start counting braces from the appropriate line
            if i >= brace_start:
                # Count braces, being careful about strings and comments
                cleaned_line = self._remove_strings_and_comments(line)
                
                for char in cleaned_line:
                    if char == '{':
                        brace_count += 1
                        found_opening_brace = True
                    elif char == '}':
                        brace_count -= 1
                        
                        # If we close all braces, we're done
                        if found_opening_brace and brace_count == 0:
                            return '\n'.join(content_lines), i
        
        # If we never found a closing brace, return what we have
        return '\n'.join(content_lines), len(lines) - 1
    
    def _remove_strings_and_comments(self, line: str) -> str:
        """Remove string literals and comments from a line to avoid counting braces inside them"""
        result = []
        i = 0
        in_string = False
        string_char = None
        escaped = False
        
        while i < len(line):
            char = line[i]
            
            if escaped:
                escaped = False
                i += 1
                continue
                
            if char == '\\':
                escaped = True
                i += 1
                continue
                
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                elif char == '/' and i + 1 < len(line) and line[i+1] == '/':
                    break  # Rest of line is comment
                else:
                    result.append(char)
            else:
                if char == string_char:
                    in_string = False
                    string_char = None
                    
            i += 1
            
        return ''.join(result)
    
    def _is_control_flow_start(self, line: str) -> bool:
        """Check if line starts a control flow statement"""
        control_keywords = ['if ', 'while ', 'for ', 'switch ', 'try ', 'catch ']
        return any(line.startswith(keyword) for keyword in control_keywords)
    
    def _classify_statement(self, line: str) -> StatementType:
        """Classify a single-line statement"""
        line = line.strip()
        
        # Variable declarations (type followed by identifier)
        type_pattern = r'^(const\s+)?(static\s+)?(int|long|short|byte|float|double|bool|char|string|void|auto|list|map|set|tuple)\s+\w+'
        if re.match(type_pattern, line):
            if '=' in line:
                return StatementType.VARIABLE_ASSIGN
            else:
                return StatementType.VARIABLE_DECL
                
        # Assignment (identifier = expression)
        if re.match(r'^\w+\s*=', line) and not line.startswith('=='):
            return StatementType.VARIABLE_ASSIGN
            
        # Function calls (identifier(...))
        if re.match(r'^\w+.*\(.*\)', line):
            return StatementType.EXPRESSION
            
        return StatementType.EXPRESSION

# Test the splitter with your map example
def test_splitter():
    TEST_SOURCE = """func linearSearch<T>(const list<T>& arr, const T& target> -> union<int, string> {
    for (int i = 0; i < arr.size(); ++i) {
        if (arr[i] == target) { return i } /* Found target at index i */
    }
    return "Not in iterable!"  // Return message if not found
    /* End of function */
}

// Main access
main: // Entry point
    list<int> my_list = [1, 3, 99, 41, 42, 24, 11, 67, 69, 360] // Sample list
    
    map<int, string> players = {  // Player data
        1: "Alex",  // Player 1
        2: "Lucy"   // Player 2
    }
    
    __CPP_BLOCK_0__  // Call search function
    __CPP_BLOCK_1__"""

    cpp_blocks = {
        "__CPP_BLOCK_0__": "std::cout << \"41 is at index\" << linearSearch(my_list, 41) << std::endl;",
        "__CPP_BLOCK_1__": "std::cout << \"100 is at index\" << linearSearch(my_list, 100) << std::endl;"
    }

    splitter = StatementSplitter()
    statements = splitter.split_statements(TEST_SOURCE, cpp_blocks)
    
    print("Split Statements:")
    print("=" * 50)
    for i, stmt in enumerate(statements):
        print(f"{i}: {stmt.type.value}")
        print(f"   Lines {stmt.line_start}-{stmt.line_end}")
        print(f"   Content: {repr(stmt.content[:80])}...")
        print()

if __name__ == "__main__":
    test_splitter()