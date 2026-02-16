from quirk.ast_nodes import *

program = Program([
    Assign(
        "x",
        BinaryOp(
            Number(5),
            "+",
            Number(3)
        )
    ),
    Print(Variable("x"))
])

print(program)
