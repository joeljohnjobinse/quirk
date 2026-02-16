class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class RuntimeAbort(Exception):
    def __init__(self, message):
        self.message = message


class Interpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}
        self.strict = False

        self.builtins = {
            "toNumber": lambda x: int(x),
            "toString": lambda x: str(x),
            "length": lambda x: len(x),
            "append": self._append
        }

    # -------------------------
    # Built-in implementations
    # -------------------------
    def _append(self, lst, value):
        if not isinstance(lst, list):
            raise RuntimeAbort("append() expects a list")
        lst.append(value)

    # -------------------------
    # Expression evaluation
    # -------------------------
    def eval_expr(self, expr):
        expr = expr.strip()

        eval_env = {}
        eval_env.update(self.vars)
        eval_env.update(self.builtins)

        def call_func(name, *args):
            if name not in self.functions:
                raise RuntimeAbort(f"Function '{name}' not defined")

            params, body = self.functions[name]

            if len(args) != len(params):
                raise RuntimeAbort(
                    f"{name} expects {len(params)} arguments, got {len(args)}"
                )

            local_vars = dict(zip(params, args))
            saved_vars = self.vars
            self.vars = local_vars

            try:
                self.run("\n".join(body))
            except ReturnException as r:
                self.vars = saved_vars
                return r.value
            finally:
                self.vars = saved_vars

            return None

        for name in self.functions:
            eval_env[name] = (lambda *a, n=name: call_func(n, *a))

        try:
            return eval(expr, {}, eval_env)
        except NameError as e:
            if self.strict:
                raise RuntimeAbort(f"Undefined name: {e}")
            raise RuntimeAbort("Undefined variable or function")
        except IndexError:
            raise RuntimeAbort(f"List index out of range in expression: {expr}")
        except TypeError:
            raise RuntimeAbort(f"Invalid operation in expression: {expr}")

    # -------------------------
    # Block collector
    # -------------------------
    def collect_block(self, lines, i):
        block = []
        depth = 1
        i += 1

        while i < len(lines) and depth > 0:
            line = lines[i]

            if line.startswith(("if", "for", "function")):
                depth += 1
            elif line == "end":
                depth -= 1
                if depth == 0:
                    break

            if depth > 0:
                block.append(line)

            i += 1

        if depth != 0:
            raise RuntimeAbort("Missing 'end' for block")

        return block, i

    # -------------------------
    # Main interpreter
    # -------------------------
    def run(self, code):
        lines = [line.strip() for line in code.split("\n") if line.strip()]
        i = 0

        while i < len(lines):
            line = lines[i]

            if line == "strict on":
                self.strict = True

            elif line == "strict off":
                self.strict = False

            elif line.startswith("print"):
                print(self.eval_expr(line.replace("print", "").strip()))

            elif line.startswith("return"):
                value = self.eval_expr(line.replace("return", "").strip())
                raise ReturnException(value)

            elif line.startswith("function"):
                header = line.replace("function", "").strip()
                parts = header.split(" ", 1)
                name = parts[0]
                params = []

                if len(parts) > 1:
                    params = [p.strip() for p in parts[1].split(",")]

                body, i = self.collect_block(lines, i)
                self.functions[name] = (params, body)

            # for item in list
            elif line.startswith("for") and " in " in line:
                _, var, _, iterable = line.split()
                lst = self.eval_expr(iterable)

                if not isinstance(lst, list):
                    raise RuntimeAbort("for-in expects a list")

                block, i = self.collect_block(lines, i)

                for item in lst:
                    self.vars[var] = item
                    self.run("\n".join(block))

            # for i from A to B (exclusive)
            elif line.startswith("for"):
                parts = line.split()
                var = parts[1]
                start = self.eval_expr(parts[3])
                end = self.eval_expr(parts[5])

                block, i = self.collect_block(lines, i)

                for val in range(start, end):
                    self.vars[var] = val
                    self.run("\n".join(block))

            elif line.startswith("if"):
                conditions = []
                blocks = []
                else_block = None

                conditions.append(line.replace("if", "").strip())
                raw_block, i = self.collect_block(lines, i)

                current = []
                depth = 0

                for ln in raw_block:
                    if ln.startswith(("if", "for", "function")):
                        depth += 1
                    elif ln == "end":
                        depth -= 1

                    if ln.startswith("else if") and depth == 0:
                        blocks.append(current)
                        current = []
                        conditions.append(ln.replace("else if", "").strip())
                    elif ln == "else" and depth == 0:
                        blocks.append(current)
                        current = []
                        else_block = []
                    else:
                        if else_block is not None:
                            else_block.append(ln)
                        else:
                            current.append(ln)

                blocks.append(current)

                for cond, blk in zip(conditions, blocks):
                    if self.eval_expr(cond):
                        self.run("\n".join(blk))
                        break
                else:
                    if else_block:
                        self.run("\n".join(else_block))

            elif "=" in line:
                left, right = line.split("=", 1)
                left = left.strip()

                if "[" in left and left.endswith("]"):
                    name, index = left.split("[", 1)
                    index = index[:-1].strip()

                    lst = self.vars.get(name.strip())
                    if not isinstance(lst, list):
                        raise RuntimeAbort(f"{name.strip()} is not a list")

                    idx = self.eval_expr(index)
                    if idx < 0 or idx >= len(lst):
                        raise RuntimeAbort(
                            f"List index {idx} out of range (length = {len(lst)})"
                        )

                    lst[idx] = self.eval_expr(right.strip())
                else:
                    if self.strict and left not in self.vars:
                        raise RuntimeAbort(f"Variable '{left}' not defined")
                    self.vars[left] = self.eval_expr(right.strip())

            i += 1
