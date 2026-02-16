# quirk/lexer.py

import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value", "line"])

# =========================================================
# TOKEN SPECIFICATION
# Order matters — longer tokens must appear first
# =========================================================

TOKEN_SPEC = [

    # -------- COMMENTS --------
    ("COMMENT", r"#.*"),

    # -------- LITERALS --------
    ("FLOAT",  r"-?\d+\.\d+"),
    ("NUMBER", r"-?\d+(?!\.)"),

    ("STRING", r'"[^"]*"'),

    # -------- KEYWORDS --------
    ("FUNCTION", r"\bfunction\b"),
    ("RETURN", r"\breturn\b"),
    ("IF", r"\bif\b"),
    ("ELSE", r"\belse\b"),
    ("WHILE", r"\bwhile\b"),
    ("FOR", r"\bfor\b"),
    ("IN", r"\bin\b"),
    ("END", r"\bend\b"),
    ("PRINT", r"\bprint\b"),
    ("IMPORT", r"\bimport\b"),
    ("WITH", r"\bwith\b"),
    ("SEP", r"\bsep\b"),
    ("TRUE", r"\btrue\b"),
    ("FALSE", r"\bfalse\b"),
    ("AND", r"\band\b"),
    ("OR", r"\bor\b"),
    ("NOT", r"\bnot\b"),
    ("BREAK", r"\bbreak\b"),
    ("CONTINUE", r"\bcontinue\b"),

    # -------- OPERATORS --------
    ("POWER", r"\*\*"),
    ("INTDIV", r"//"),

    ("PLUSPLUSEQUAL", r"\+\+="),
    ("MINUSMINUSEQUAL", r"--="),
    ("TILDETILDEEQUAL", r"~~="),

    ("PLUSPLUS", r"\+\+"),
    ("MINUSMINUS", r"--"),
    ("TILDETILDE", r"~~"),

    ("PLUSEQUAL", r"\+="),
    ("MINUSEQUAL", r"-="),

    ("EQEQ", r"=="),
    ("NEQ", r"!="),
    ("GT", r">"),
    ("LT", r"<"),

    ("PLUS", r"\+"),
    ("MINUS", r"-"),
    ("STAR", r"\*"),
    ("MOD", r"%"),
    ("SLASH", r"/"),

    # -------- STRUCTURE --------
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACK", r"\["),
    ("RBRACK", r"\]"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("COLON", r":"),
    ("DOT", r"\."),
    ("EQUAL", r"="),

    # -------- IDENTIFIERS --------
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),

    # -------- WHITESPACE --------
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
]

MASTER_RE = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)

# =========================================================
# TOKENIZER
# =========================================================

def tokenize(code):
    tokens = []
    line = 1

    for match in MASTER_RE.finditer(code):
        kind = match.lastgroup
        value = match.group()

        if kind == "NEWLINE":
            tokens.append(Token("NEWLINE", value, line))
            line += 1

        elif kind == "SKIP":
            continue

        elif kind == "COMMENT":
            continue

        elif kind == "STRING":
            tokens.append(Token("STRING", value[1:-1], line))

        elif kind == "FLOAT":
            tokens.append(Token("FLOAT", value, line))

        else:
            tokens.append(Token(kind, value, line))

    return tokens
