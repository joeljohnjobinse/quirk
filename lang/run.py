from mylang import Interpreter, RuntimeAbort

with open("test.my") as f:
    code = f.read()

try:
    Interpreter().run(code)
except RuntimeAbort as e:
    print("Runtime Error:", e.message)