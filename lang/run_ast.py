from quirk.lexer import tokenize
from quirk.parser import Parser
from quirk.ast_interpreter import Interpreter

code = """
x = 5 + 3
y = x + 10
print y
"""

tokens = tokenize(code)
ast = Parser(tokens).parse()

Interpreter().run(ast)
