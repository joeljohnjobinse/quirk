# quirk/compiler.py

from quirk.ast_nodes import *


class Compiler:
    def __init__(self):
        self.lines = []
        self.indent = 0

    def emit(self, line):
        self.lines.append("    " * self.indent + line)

    def compile(self, program):
        for s in program.statements:
            self.emit_stmt(s)
        return "\n".join(self.lines)

    def emit_stmt(self, node):
        if isinstance(node, Assign):
            self.emit(f"{self.emit_expr(node.target)} = {self.emit_expr(node.value)}")

        elif isinstance(node, Print):
            self.emit(f"print({self.emit_expr(node.value)})")

        elif isinstance(node, If):
            self.emit(f"if {self.emit_expr(node.condition)}:")
            self.indent += 1
            for s in node.then_body:
                self.emit_stmt(s)
            self.indent -= 1
            if node.else_body:
                self.emit("else:")
                self.indent += 1
                for s in node.else_body:
                    self.emit_stmt(s)
                self.indent -= 1

        elif isinstance(node, While):
            self.emit(f"while {self.emit_expr(node.condition)}:")
            self.indent += 1
            for s in node.body:
                self.emit_stmt(s)
            self.indent -= 1

        elif isinstance(node, ForEach):
            self.emit(f"for {node.var} in {self.emit_expr(node.iterable)}:")
            self.indent += 1
            for s in node.body:
                self.emit_stmt(s)
            self.indent -= 1

        elif isinstance(node, FunctionDef):
            self.emit(f"def {node.name}({', '.join(node.params)}):")
            self.indent += 1
            for s in node.body:
                self.emit_stmt(s)
            self.indent -= 1

        elif isinstance(node, Return):
            self.emit(f"return {self.emit_expr(node.value)}")

    def emit_expr(self, node):
        if isinstance(node, Number):
            return str(node.value)
        if isinstance(node, String):
            return repr(node.value)
        if isinstance(node, Variable):
            return node.name
        if isinstance(node, BinaryOp):
            return f"({self.emit_expr(node.left)} {node.op} {self.emit_expr(node.right)})"
        if isinstance(node, ListLiteral):
            return "[" + ", ".join(self.emit_expr(e) for e in node.elements) + "]"
        if isinstance(node, Index):
            return f"{self.emit_expr(node.base)}[{self.emit_expr(node.index)}]"
        if isinstance(node, Call):
            return f"{node.name}(" + ", ".join(self.emit_expr(a) for a in node.args) + ")"
