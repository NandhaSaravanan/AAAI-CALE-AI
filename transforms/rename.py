"""Family 1: rename local variables and function parameters to random identifiers.
Not renamed: built-ins, imported names, attributes, function/class names, keyword-argument
names at call sites (and any parameter whose name is used as a call keyword), and names
declared global/nonlocal are renamed consistently program-wide (single namespace mapping).
Returns transformed text or None if not safely applicable."""
import ast
import random

from transforms.common import BUILTINS, all_names, fresh_name, line_offsets, parse, to_index, uses_dynamic


def transform(src, seed=0, frac=1.0):
    tree = parse(src)
    if tree is None or uses_dynamic(tree):
        return None
    rng = random.Random(seed)
    imported, defs, kw_used, star_import = set(), set(), set(), False
    for n in ast.walk(tree):
        if isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                if a.name == "*":
                    star_import = True
                imported.add((a.asname or a.name).split(".")[0])
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defs.add(n.name)
        elif isinstance(n, ast.keyword) and n.arg:
            kw_used.add(n.arg)
    if star_import:
        return None  # cannot know which names come from the star import
    # candidates: names bound by assignment / for / with / comprehension / except / params
    cands = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            cands.add(n.id)
        elif isinstance(n, ast.arg):
            cands.add(n.arg)
        elif isinstance(n, ast.ExceptHandler) and n.name:
            return None  # except ... as name: name position not in AST; skip for safety
        elif isinstance(n, (ast.MatchAs, ast.MatchStar, ast.MatchMapping)):
            return None
    # names bound directly in a class body become attributes (self.x) -> never rename
    class_bound = set()
    for c in ast.walk(tree):
        if isinstance(c, ast.ClassDef):
            for st in c.body:
                for n in ast.walk(st):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                        class_bound.add(n.id)
    cands -= BUILTINS | imported | defs | kw_used | class_bound
    cands = {c for c in cands if not c.startswith("__")}
    if not cands:
        return None
    cands = sorted(cands)
    rng.shuffle(cands)
    k = max(1, round(len(cands) * frac))
    taken = all_names(tree)
    mapping = {c: fresh_name(rng, taken) for c in cands[:k]}

    lines = line_offsets(src)
    edits = []  # (start_idx, end_idx, new)
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id in mapping:
            s = to_index(lines, n.lineno, n.col_offset)
            edits.append((s, s + len(n.id), mapping[n.id], n.id))
        elif isinstance(n, ast.arg) and n.arg in mapping:
            s = to_index(lines, n.lineno, n.col_offset)
            edits.append((s, s + len(n.arg), mapping[n.arg], n.arg))
        elif isinstance(n, (ast.Global, ast.Nonlocal)):
            if any(x in mapping for x in n.names):
                return None  # names in global stmt have no positions; skip
    text = "".join(lines)
    for s, e, new, old in sorted(edits, reverse=True):
        if text[s:e] != old:
            return None  # position mismatch (e.g. f-string internals) -> unsafe
        text = text[:s] + new + text[e:]
    if text == src or parse(text) is None:
        return None
    return text
