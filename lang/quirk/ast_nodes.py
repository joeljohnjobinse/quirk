# quirk/ast_nodes.py

# =========================================================
# BASE NODE
# =========================================================

class Node:
    def __init__(self, line):
        self.line = line


# =========================================================
# PROGRAM
# =========================================================

class Program(Node):
    def __init__(self, statements):
        super().__init__(1)
        self.statements = statements


# =========================================================
# STATEMENTS
# =========================================================

class Assign(Node):
    def __init__(self, target, value, line):
        super().__init__(line)
        self.target = target
        self.value = value


class CompoundAssign(Node):
    def __init__(self, target, op, value, line):
        super().__init__(line)
        self.target = target
        self.op = op
        self.value = value


class Print(Node):
    def __init__(self, values, sep, end, line):
        super().__init__(line)
        self.values = values
        self.sep = sep
        self.end = end


class ExprStmt(Node):
    def __init__(self, expr, line):
        super().__init__(line)
        self.expr = expr


class If(Node):
    def __init__(self, condition, then_body, else_body, line):
        super().__init__(line)
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body


class While(Node):
    def __init__(self, condition, body, line):
        super().__init__(line)
        self.condition = condition
        self.body = body


class ForEach(Node):
    def __init__(self, var, iterable, body, line):
        super().__init__(line)
        self.var = var
        self.iterable = iterable
        self.body = body


class FunctionDef(Node):
    def __init__(self, name, params, body, line):
        super().__init__(line)
        self.name = name
        self.params = params
        self.body = body


class Return(Node):
    def __init__(self, value, line):
        super().__init__(line)
        self.value = value


class Break(Node):
    pass


class Continue(Node):
    pass


class Import(Node):
    def __init__(self, module_name, line):
        super().__init__(line)
        self.module_name = module_name


# =========================================================
# EXPRESSIONS
# =========================================================

class Number(Node):
    def __init__(self, value, line):
        super().__init__(line)
        self.value = value


class String(Node):
    def __init__(self, value, line):
        super().__init__(line)
        self.value = value


class Boolean(Node):
    def __init__(self, value, line):
        super().__init__(line)
        self.value = value


class Variable(Node):
    def __init__(self, name, line):
        super().__init__(line)
        self.name = name


class BinaryOp(Node):
    def __init__(self, left, op, right, line):
        super().__init__(line)
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(Node):
    def __init__(self, op, operand, line):
        super().__init__(line)
        self.op = op
        self.operand = operand


class ListLiteral(Node):
    def __init__(self, elements, line):
        super().__init__(line)
        self.elements = elements


class TupleLiteral(Node):
    def __init__(self, elements, line):
        super().__init__(line)
        self.elements = elements


class SetLiteral(Node):
    def __init__(self, elements, line):
        super().__init__(line)
        self.elements = elements


class MapLiteral(Node):
    def __init__(self, pairs, line):
        super().__init__(line)
        self.pairs = pairs


class Index(Node):
    def __init__(self, obj, index, line):
        super().__init__(line)
        self.obj = obj
        self.index = index


class Call(Node):
    def __init__(self, name, args, line):
        super().__init__(line)
        self.name = name
        self.args = args


class AttributeAccess(Node):
    def __init__(self, obj, attr, line):
        super().__init__(line)
        self.obj = obj
        self.attr = attr


class PostfixIncrement(Node):
    def __init__(self, variable, line):
        super().__init__(line)
        self.variable = variable


class PostfixDecrement(Node):
    def __init__(self, variable, line):
        super().__init__(line)
        self.variable = variable


class TuplePattern(Node):
    def __init__(self, elements, line):
        super().__init__(line)
        self.elements = elements
