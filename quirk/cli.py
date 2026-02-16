# quirk/cli.py

import argparse
import sys

from quirk.lexer import tokenize
from quirk.parser import Parser
from quirk.parser import QuirkSyntaxError
from quirk.ast_interpreter import Interpreter, RuntimeError


BLOCK_STARTERS = ("if", "while", "for", "function")


def run_code(code, interpreter):
    try:
        tokens = tokenize(code)
        ast = Parser(tokens).parse()
        interpreter.run(ast)

    except QuirkSyntaxError as e:
        print(str(e))

    except RuntimeError as e:
        print(str(e))

    except Exception:
        print("Internal Error: Unexpected failure.")


def repl():
    print("Quirk REPL — type 'exit' to quit")
    interpreter = Interpreter()

    buffer = []
    open_blocks = 0

    while True:
        try:
            prompt = ">>> " if open_blocks == 0 else "... "
            line = input(prompt)

            if line.strip() == "":
                continue

            if line.strip() == "exit" and open_blocks == 0:
                break

            buffer.append(line)

            stripped = line.strip()

            # Count block openings
            for kw in BLOCK_STARTERS:
                if stripped.startswith(kw + " "):
                    open_blocks += 1

            # Count block endings
            if stripped == "end":
                open_blocks -= 1

            # If block complete, execute
            if open_blocks == 0:
                code = "\n".join(buffer)
                buffer.clear()

                run_code(code, interpreter)

        except RuntimeError as e:
            print(e)
            buffer.clear()
            open_blocks = 0

        except Exception as e:
            print(f"Error: {e}")
            buffer.clear()
            open_blocks = 0


def run_file(path):
    with open(path, "r") as f:
        code = f.read()

    interpreter = Interpreter()
    run_code(code, interpreter)


def main():
    parser = argparse.ArgumentParser(
        prog="quirk",
        description="Quirk CLI"
    )

    sub = parser.add_subparsers(dest="command")

    run_cmd = sub.add_parser("run")
    run_cmd.add_argument("file")

    repl_cmd = sub.add_parser("repl")

    args = parser.parse_args()

    if args.command == "run":
        run_file(args.file)

    elif args.command == "repl":
        repl()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
