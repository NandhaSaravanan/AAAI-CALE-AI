"""Shared helpers. Transforms edit the ORIGINAL TEXT at AST-reported positions
(never ast.unparse), so comments/formatting are preserved and the only change is
the transformation itself."""
import ast
import builtins
import keyword
import random

BUILTINS = set(dir(builtins))
KEYWORDS = set(keyword.kwlist) | set(getattr(keyword, "softkwlist", []))
DYNAMIC = {"eval", "exec", "locals", "globals", "vars", "__import__", "getattr", "setattr", "delattr"}


def parse(src):
    try:
        return ast.parse(src)
    except (SyntaxError, ValueError, MemoryError, RecursionError):
        return None


def uses_dynamic(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id in DYNAMIC:
            return True
    return False


def line_offsets(src):
    """Return list of (line_text_bytes) so we can convert (lineno, utf8 col) to str index."""
    return src.splitlines(keepends=True)


def to_index(lines, lineno, col_bytes):
    """Convert ast (1-based lineno, utf-8 byte col) into a str index into ''.join(lines)."""
    idx = sum(len(l) for l in lines[: lineno - 1])
    line = lines[lineno - 1]
    return idx + len(line.encode("utf-8")[:col_bytes].decode("utf-8", errors="ignore"))


def fresh_name(rng, taken, style="random"):
    letters = "abcdefghijklmnopqrstuvwxyz"
    while True:
        n = rng.choice(letters) + "".join(rng.choice(letters + "0123456789_") for _ in range(rng.randint(2, 7)))
        if n not in taken and n not in BUILTINS and n not in KEYWORDS and not n.startswith("__"):
            taken.add(n)
            return n


def all_names(tree):
    s = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            s.add(n.id)
        elif isinstance(n, ast.arg):
            s.add(n.arg)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            s.add(n.name)
        elif isinstance(n, ast.alias):
            s.add((n.asname or n.name).split(".")[0])
        elif isinstance(n, ast.Attribute):
            s.add(n.attr)
        elif isinstance(n, ast.keyword) and n.arg:
            s.add(n.arg)
    return s


def same_ast(a, b):
    return ast.dump(ast.parse(a)) == ast.dump(ast.parse(b))
