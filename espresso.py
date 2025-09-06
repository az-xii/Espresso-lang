import scripts.lexer as lexer
import pprint
src = "int x = 10"

tokens = lexer.Lexer.lex_source(src)
for token in tokens:
    pprint.pprint(token)