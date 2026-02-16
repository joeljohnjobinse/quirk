from quirk.lexer import tokenize
from quirk.parser import Parser

code = """
x = 5 + 3
print x
"""

tokens = tokenize(code)
parser = Parser(tokens)
ast = parser.parse()

print(ast)
