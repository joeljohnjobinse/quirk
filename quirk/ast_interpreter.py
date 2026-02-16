# quirk/ast_interpreter.py

import os
from quirk.ast_nodes import *
from quirk.lexer import tokenize
from quirk.parser import Parser


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class RuntimeError(Exception):
    def __init__(self, message, line):
        self.line = line
        self.message = message
        super().__init__(f"Runtime Error (line {line}): {message}")



# =========================================================
# SCOPE SYSTEM
# =========================================================

class ScopeStack:
    def __init__(self):
        self.scopes = [{}]

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def set(self, name, value):
        self.scopes[-1][name] = value

    def get(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise KeyError(name)


# =========================================================
# INTERPRETER
# =========================================================

class Interpreter:

    def __init__(self):
        self.scopes = ScopeStack()
        self.functions = {}
        self.modules = {}

        self._load_builtins()

    # =====================================================
    # BUILTINS
    # =====================================================

    def _load_builtins(self):
        self.scopes.set("range", lambda *a: list(range(*a)))
        self.scopes.set("len", lambda x: len(x))
        self.scopes.set("sum", lambda x: sum(x))
        self.scopes.set("min", lambda *a: min(*a))
        self.scopes.set("max", lambda *a: max(*a))

    # =====================================================
    # PROGRAM
    # =====================================================

    def run(self, program):
        for stmt in program.statements:
            self.execute(stmt)

    # =====================================================
    # STATEMENTS
    # =====================================================

    def execute(self, node):

        if isinstance(node, Import):
            self.load_module(node.module_name, node.line)
            return

        if isinstance(node, Assign):
            value = self.evaluate(node.value)

            if isinstance(node.target, Variable):
                self.scopes.set(node.target.name, value)
                return

            if isinstance(node.target, TuplePattern):
                self.unpack_tuple(node.target, value, node.line)
                return

        if isinstance(node, CompoundAssign):
            current = self.scopes.get(node.target.name)
            value = self.evaluate(node.value)

            if node.op == "PLUSEQUAL":
                self.scopes.set(node.target.name, current + value)

            elif node.op == "MINUSEQUAL":
                self.scopes.set(node.target.name, current - value)

            elif node.op == "PLUSPLUSEQUAL":
                current.update(value)

            elif node.op == "MINUSMINUSEQUAL":
                current.difference_update(value)

            elif node.op == "TILDETILDEEQUAL":
                current.symmetric_difference_update(value)

            return

        if isinstance(node, Print):
            values = [self.evaluate(v) for v in node.values]
            sep = self.evaluate(node.sep) if node.sep else " "
            end = self.evaluate(node.end) if node.end else "\n"
            print(*values, sep=sep, end=end)
            return

        if isinstance(node, ExprStmt):
            self.evaluate(node.expr)
            return

        if isinstance(node, FunctionDef):
            self.functions[node.name] = node
            self.scopes.set(node.name, node)
            return

        if isinstance(node, Return):
            raise ReturnSignal(self.evaluate(node.value))

        if isinstance(node, Break):
            raise BreakSignal()

        if isinstance(node, Continue):
            raise ContinueSignal()

        if isinstance(node, If):
            cond = self.evaluate(node.condition)
            body = node.then_body if cond else node.else_body
            if body:
                for stmt in body:
                    self.execute(stmt)
            return

        if isinstance(node, While):
            while self.evaluate(node.condition):
                try:
                    for stmt in node.body:
                        self.execute(stmt)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return

        if isinstance(node, ForEach):
            iterable = self.evaluate(node.iterable)

            for item in iterable:
                self.scopes.push()
                self.scopes.set(node.var.name, item)

                try:
                    for stmt in node.body:
                        self.execute(stmt)
                except ContinueSignal:
                    pass
                except BreakSignal:
                    self.scopes.pop()
                    break

                self.scopes.pop()

    # =====================================================
    # EXPRESSIONS
    # =====================================================

    def evaluate(self, node):

        if isinstance(node, Number):
            return node.value

        if isinstance(node, String):
            return node.value

        if isinstance(node, Boolean):
            return node.value

        if isinstance(node, Attribute):
            obj = self.evaluate(node.object)

            if isinstance(obj, dict):
                if node.name in obj:
                    return obj[node.name]

            raise RuntimeError(
                f"Attribute '{node.name}' not found",
                node.line
            )


            if isinstance(obj, dict):
                if node.name in obj:
                    return obj[node.name]

            raise RuntimeError(
                f"Attribute '{node.name}' not found",
                node.line
            )

        if isinstance(node, Variable):
            try:
                return self.scopes.get(node.name)
            except KeyError:
                raise RuntimeError(f"Undefined variable '{node.name}'", node.line)

        if isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if node.op == "+":
                return left + right
            if node.op == "-":
                return left - right
            if node.op == "*":
                return left * right
            if node.op == "//":
                return left // right
            if node.op == "%":
                return left % right
            if node.op == "**":
                return left ** right
            if node.op == "==":
                return left == right
            if node.op == "!=":
                return left != right
            if node.op == ">":
                return left > right
            if node.op == "<":
                return left < right
            if node.op == "and":
                return left and right
            if node.op == "or":
                return left or right

        if isinstance(node, PostfixIncrement):
            val = self.scopes.get(node.variable.name)
            self.scopes.set(node.variable.name, val + 1)
            return val

        if isinstance(node, PostfixDecrement):
            val = self.scopes.get(node.variable.name)
            self.scopes.set(node.variable.name, val - 1)
            return val

        if isinstance(node, Call):
            func = self.evaluate(node.name)
            args = [self.evaluate(a) for a in node.args]

            if callable(func):
                return func(*args)

            if isinstance(func, FunctionDef):
                return self.call_function(func, args)

            raise RuntimeError("Invalid function call", node.line)

        if isinstance(node, AttributeAccess):
            obj = self.evaluate(node.obj)
            if isinstance(obj, dict):
                if node.attr in obj:
                    return obj[node.attr]
            raise RuntimeError(f"No attribute '{node.attr}'", node.line)

        if isinstance(node, TupleLiteral):
            return tuple(self.evaluate(e) for e in node.elements)

        if isinstance(node, ListLiteral):
            return [self.evaluate(e) for e in node.elements]
        
        if isinstance(node, SetLiteral):
            s = set()
            for e in node.elements:
                value = self.evaluate(e)
                s.add(value)
            return s

        if isinstance(node, MapLiteral):
            m = {}
            for k_node, v_node in node.pairs:
                key = self.evaluate(k_node)
                value = self.evaluate(v_node)
                m[key] = value
            return m



        raise RuntimeError("Unknown expression", node.line)
    

    # =====================================================
    # FUNCTION CALL
    # =====================================================

    def call_function(self, fn, args):

        if len(args) != len(fn.params):
            raise RuntimeError("Argument count mismatch", fn.line)

        self.scopes.push()

        for param, arg in zip(fn.params, args):
            self.scopes.set(param.name, arg)

        try:
            for stmt in fn.body:
                self.execute(stmt)
        except ReturnSignal as r:
            self.scopes.pop()
            return r.value

        self.scopes.pop()
        return None

    # =====================================================
    # TUPLE UNPACK
    # =====================================================

    def unpack_tuple(self, pattern, value, line):
        if not isinstance(value, tuple):
            raise RuntimeError("Tuple assignment requires tuple", line)

        if len(pattern.elements) != len(value):
            raise RuntimeError("Tuple length mismatch", line)

        for var, val in zip(pattern.elements, value):
            self.scopes.set(var.name, val)

    # =====================================================
    # MODULE LOADER
    # =====================================================
    

    def load_module(self, name, line):

        MODULE_PATHS = [
                    ".",
                    "lang",
        ]

        if name in self.modules:
            self.scopes.set(name, self.modules[name])
            return

        filename = None

        for base in MODULE_PATHS:
            path = os.path.join(base, f"{name}.sl")
            if os.path.exists(path):
                filename = path
                break

        if not filename:
            raise RuntimeError(f"Module '{name}' not found", line)

        with open(filename, "r") as f:
            code = f.read()

        tokens = tokenize(code)
        for t in tokens:
            print(t.type, t.value)
        ast = Parser(tokens).parse()

        module_interpreter = Interpreter()
        module_interpreter.run(ast)

        module_dict = {}
        module_dict.update(module_interpreter.functions)
        module_dict.update(module_interpreter.scopes.scopes[0])

        self.modules[name] = module_dict
        self.scopes.set(name, module_dict)

