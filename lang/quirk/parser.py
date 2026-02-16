from quirk.ast_nodes import *


# =========================================================
# SYNTAX ERROR
# =========================================================

class QuirkSyntaxError(Exception):
    def __init__(self, message, token=None):
        if token:
            super().__init__(f"Syntax Error (line {token.line}): {message}")
        else:
            super().__init__(f"Syntax Error: {message}")


# =========================================================
# PARSER
# =========================================================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # -----------------------------------------------------
    # Core utilities
    # -----------------------------------------------------

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self):
        self.pos += 1

    def eat(self, type_):
        tok = self.current()

        if not tok:
            raise QuirkSyntaxError(
                f"Expected '{type_}' but reached end of file"
            )

        if tok.type != type_:
            raise QuirkSyntaxError(
                f"Expected '{type_}', got '{tok.value}'",
                tok
            )

        self.advance()
        return tok

    def skip_newlines(self):
        while self.current() and self.current().type == "NEWLINE":
            self.advance()

    # -----------------------------------------------------
    # Program
    # -----------------------------------------------------

    def parse(self):
        statements = []

        while self.current():
            self.skip_newlines()
            if not self.current():
                break
            statements.append(self.statement())

        return Program(statements)

    # -----------------------------------------------------
    # Statements
    # -----------------------------------------------------

    def statement(self):
        self.skip_newlines()
        tok = self.current()

        if not tok:
            raise QuirkSyntaxError("Unexpected end of input")

        if tok.type == "IMPORT":
            return self.import_stmt()

        if tok.type == "PRINT":
            return self.print_stmt()

        if tok.type == "FUNCTION":
            return self.function_def()

        if tok.type == "IF":
            return self.if_stmt()

        if tok.type == "WHILE":
            return self.while_stmt()

        if tok.type == "FOR":
            return self.for_stmt()

        if tok.type == "RETURN":
            self.eat("RETURN")
            return Return(self.expression(), tok.line)

        if tok.type == "BREAK":
            self.eat("BREAK")
            return Break(tok.line)

        if tok.type == "CONTINUE":
            self.eat("CONTINUE")
            return Continue(tok.line)

        # Assignment or expression
        expr = self.expression()

        if self.current() and self.current().type in (
            "EQUAL", "PLUSEQUAL", "MINUSEQUAL",
            "PLUSPLUSEQUAL", "MINUSMINUSEQUAL", "TILDETILDEEQUAL"
        ):
            op = self.current().type
            self.advance()
            value = self.expression()

            if isinstance(expr, Variable):
                if op == "EQUAL":
                    return Assign(expr, value, expr.line)
                return CompoundAssign(expr, op, value, expr.line)

            if isinstance(expr, TupleLiteral):
                return Assign(TuplePattern(expr.elements, expr.line), value, expr.line)

            raise QuirkSyntaxError(
                "Invalid assignment target (must be variable or tuple)",
                tok
            )

        return ExprStmt(expr, expr.line)

    # -----------------------------------------------------
    # Import
    # -----------------------------------------------------

    def import_stmt(self):
        tok = self.eat("IMPORT")
        name = self.eat("IDENT")
        return Import(name.value, tok.line)

    # -----------------------------------------------------
    # Print
    # -----------------------------------------------------

    def print_stmt(self):
        tok = self.eat("PRINT")

        values = [self.expression()]
        while self.current() and self.current().type == "COMMA":
            self.eat("COMMA")
            values.append(self.expression())

        sep = None
        end = None

        if self.current() and self.current().type == "WITH":
            self.eat("WITH")

            while self.current() and self.current().type in ("SEP", "END"):
                if self.current().type == "SEP":
                    self.eat("SEP")
                    sep = self.expression()
                elif self.current().type == "END":
                    self.eat("END")
                    end = self.expression()

        return Print(values, sep, end, tok.line)

    # -----------------------------------------------------
    # Blocks
    # -----------------------------------------------------

    def function_def(self):
        start = self.eat("FUNCTION")
        name = self.eat("IDENT").value
        self.eat("LPAREN")

        params = []
        if self.current() and self.current().type != "RPAREN":
            params.append(self.expression())
            while self.current() and self.current().type == "COMMA":
                self.eat("COMMA")
                params.append(self.expression())

        self.eat("RPAREN")
        self.skip_newlines()

        body = self.parse_block("function", start)

        return FunctionDef(name, params, body, start.line)

    def if_stmt(self):
        start = self.eat("IF")
        cond = self.expression()
        self.skip_newlines()

        then_body = []

        while self.current() and self.current().type not in ("ELSE", "END"):
            then_body.append(self.statement())
            self.skip_newlines()

        else_body = []

        if self.current() and self.current().type == "ELSE":
            self.eat("ELSE")
            self.skip_newlines()

            while self.current() and self.current().type != "END":
                else_body.append(self.statement())
                self.skip_newlines()

        if not self.current():
            raise QuirkSyntaxError("Missing 'end' for if statement", start)

        self.eat("END")
        return If(cond, then_body, else_body or None, start.line)

    def while_stmt(self):
        start = self.eat("WHILE")
        cond = self.expression()
        self.skip_newlines()

        body = self.parse_block("while loop", start)
        return While(cond, body, start.line)

    def for_stmt(self):
        start = self.eat("FOR")
        var = Variable(self.eat("IDENT").value, start.line)
        self.eat("IN")
        iterable = self.expression()
        self.skip_newlines()

        body = self.parse_block("for loop", start)
        return ForEach(var, iterable, body, start.line)

    def parse_block(self, name, start_token):
        body = []

        while self.current() and self.current().type != "END":
            body.append(self.statement())
            self.skip_newlines()

        if not self.current():
            raise QuirkSyntaxError(
                f"Missing 'end' for {name}",
                start_token
            )

        self.eat("END")
        return body

    # -----------------------------------------------------
    # Expressions
    # -----------------------------------------------------

    def expression(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.current() and self.current().type == "OR":
            tok = self.eat("OR")
            node = BinaryOp(node, "or", self.and_expr(), tok.line)
        return node

    def and_expr(self):
        node = self.compare_expr()
        while self.current() and self.current().type == "AND":
            tok = self.eat("AND")
            node = BinaryOp(node, "and", self.compare_expr(), tok.line)
        return node

    def compare_expr(self):
        node = self.additive_expr()
        while self.current() and self.current().type in ("EQEQ", "NEQ", "GT", "LT"):
            tok = self.eat(self.current().type)
            node = BinaryOp(node, tok.value, self.additive_expr(), tok.line)
        return node

    def additive_expr(self):
        node = self.term()
        while self.current() and self.current().type in ("PLUS", "MINUS"):
            tok = self.eat(self.current().type)
            node = BinaryOp(node, tok.value, self.term(), tok.line)
        return node

    def term(self):
        node = self.power()
        while self.current() and self.current().type in ("STAR", "MOD", "INTDIV"):
            tok = self.eat(self.current().type)
            node = BinaryOp(node, tok.value, self.power(), tok.line)
        return node

    def power(self):
        node = self.primary()
        while self.current() and self.current().type == "POWER":
            tok = self.eat("POWER")
            node = BinaryOp(node, "**", self.primary(), tok.line)
        return node

    # -----------------------------------------------------
    # Primary
    # -----------------------------------------------------

    def primary(self):
        tok = self.current()

        if not tok:
            raise QuirkSyntaxError("Unexpected end of expression")

        if tok.type == "NUMBER":
            return Number(int(self.eat("NUMBER").value), tok.line)

        if tok.type == "FLOAT":
            return Number(float(self.eat("FLOAT").value), tok.line)

        if tok.type == "STRING":
            return String(self.eat("STRING").value, tok.line)

        if tok.type == "TRUE":
            self.eat("TRUE")
            return Boolean(True, tok.line)

        if tok.type == "FALSE":
            self.eat("FALSE")
            return Boolean(False, tok.line)

        if tok.type == "IDENT":
            return self.variable_or_call()

        if tok.type == "LPAREN":
            return self.group_or_tuple()

        if tok.type == "LBRACK":
            return self.list_literal()

        if tok.type == "LBRACE":
            return self.map_or_set()

        raise QuirkSyntaxError(f"Unexpected token '{tok.value}'", tok)

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def variable_or_call(self):
        tok = self.eat("IDENT")
        node = Variable(tok.value, tok.line)

        if self.current() and self.current().type == "LPAREN":
            self.eat("LPAREN")
            args = []
            if self.current() and self.current().type != "RPAREN":
                args.append(self.expression())
                while self.current() and self.current().type == "COMMA":
                    self.eat("COMMA")
                    args.append(self.expression())
            self.eat("RPAREN")
            return Call(node, args, tok.line)

        return node

    def group_or_tuple(self):
        start = self.eat("LPAREN")

        if self.current() and self.current().type == "RPAREN":
            self.eat("RPAREN")
            return TupleLiteral([], start.line)

        first = self.expression()

        if self.current() and self.current().type == "COMMA":
            elements = [first]
            while self.current() and self.current().type == "COMMA":
                self.eat("COMMA")
                elements.append(self.expression())
            self.eat("RPAREN")
            return TupleLiteral(elements, start.line)

        self.eat("RPAREN")
        return first

    def list_literal(self):
        start = self.eat("LBRACK")
        elements = []

        if self.current() and self.current().type == "RBRACK":
            self.eat("RBRACK")
            return ListLiteral(elements, start.line)

        elements.append(self.expression())
        while self.current() and self.current().type == "COMMA":
            self.eat("COMMA")
            elements.append(self.expression())

        self.eat("RBRACK")
        return ListLiteral(elements, start.line)

    def map_or_set(self):
        start = self.eat("LBRACE")

        if self.current() and self.current().type == "RBRACE":
            self.eat("RBRACE")
            return MapLiteral([], start.line)

        first = self.expression()

        if self.current() and self.current().type == "COLON":
            pairs = []
            self.eat("COLON")
            value = self.expression()
            pairs.append((first, value))

            while self.current() and self.current().type == "COMMA":
                self.eat("COMMA")
                if self.current().type == "RBRACE":
                    break
                key = self.expression()
                self.eat("COLON")
                val = self.expression()
                pairs.append((key, val))

            self.eat("RBRACE")
            return MapLiteral(pairs, start.line)

        elements = [first]
        while self.current() and self.current().type == "COMMA":
            self.eat("COMMA")
            if self.current().type == "RBRACE":
                break
            elements.append(self.expression())

        self.eat("RBRACE")
        return SetLiteral(elements, start.line)
