from quirk.lexer import tokenize
from quirk.parser import Parser
from quirk.ast_interpreter import Interpreter
from quirk.compiler import Compiler

code = """
function fact(n)
    if n < 2
        return 1
    end
    return n * fact(n - 1)
end

i = 0
nums = [1, 2, 3]

while i < 3
    nums[i] = fact(nums[i])
    i = i + 1
end

print nums

"""

ast = Parser(tokenize(code)).parse()

print("=== Interpreter ===")
Interpreter().run(ast)

print("\n=== Compiled Python ===")
py = Compiler().compile(ast)
print(py)
