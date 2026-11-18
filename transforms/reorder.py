"""Family 2: reorder independent adjacent statements.
Two adjacent statements in the same block are swapped only if
  * each occupies whole lines by itself (no ';', no shared lines),
  * neither has side effects: assignments whose RHS only calls whitelisted pure builtins,
    imports (with each other only), or function definitions (with each other only,
    no decorators/defaults referencing each other),
  * no read/write or write/write conflict on any name.
Comment/blank lines between the two statements stay in place.
Returns transformed text or None if no safe swap exists."""
import ast
import random

from transforms.common import parse, uses_dynamic

PURE = {"int", "float", "str", "len", "abs", "min", "max", "sum", "range", "list", "tuple", "set", "dict",
        "sorted", "bool", "pow", "divmod", "round", "frozenset", "ord", "chr", "bin", "hex", "zip", "enumerate",
        "reversed", "map", "any", "all"}


def names(node, ctxs):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ctxs):
            out.add(n.id)
    return out


def kind(st, shadowed):
    if isinstance(st, (ast.Import, ast.ImportFrom)):
        return "import"
    if isinstance(st, ast.FunctionDef) and not st.decorator_list:
        return "def"
    if isinstance(st, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
        val = st.value
        if val is None:
            return None
        for n in ast.walk(val):
            if isinstance(n, ast.Call):
                if not (isinstance(n.func, ast.Name) and n.func.id in PURE and n.func.id not in shadowed):
                    return None
            if isinstance(n, (ast.Yield, ast.YieldFrom, ast.Await, ast.NamedExpr, ast.Lambda,
                              ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp)):
                return None
        targets = st.targets if isinstance(st, ast.Assign) else [st.target]
        for t in targets:
            for n in ast.walk(t):
                if isinstance(n, (ast.Attribute, ast.Starred)):
                    return None
        return "assign"
    return None


def rw(st):
    if isinstance(st, (ast.Import, ast.ImportFrom)):
        return set(), {(a.asname or a.name).split(".")[0] for a in st.names}
    if isinstance(st, ast.FunctionDef):
        reads = set()
        for d in st.args.defaults + st.args.kw_defaults:
            if d is not None:
                reads |= names(d, ast.Load)
        return reads, {st.name}
    writes = names(st, (ast.Store, ast.Del))
    reads = names(st, ast.Load)
    if isinstance(st, ast.AugAssign):
        reads |= writes
    # subscript-target: a[i] = x reads AND mutates a
    targets = st.targets if isinstance(st, ast.Assign) else [st.target]
    for t in targets:
        for n in ast.walk(t):
            if isinstance(n, ast.Subscript):
                base = names(n.value, ast.Load)
                writes |= base
    return reads, writes


def independent(a, b):
    ra, wa = rw(a)
    rb, wb = rw(b)
    return not (wa & (rb | wb)) and not (wb & ra)


def transform(src, seed=0, max_swaps=3):
    tree = parse(src)
    if tree is None or uses_dynamic(tree):
        return None
    rng = random.Random(seed)
    shadowed = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    shadowed |= {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    lines = src.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    line_owner = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.stmt):
            for ln in range(n.lineno, n.end_lineno + 1):
                line_owner.setdefault(ln, []).append(n)

    def whole_lines(st):
        first = lines[st.lineno - 1].encode()
        if first[: st.col_offset].decode(errors="ignore").strip():  # something before stmt on its line
            return False
        rest = lines[st.end_lineno - 1].encode()[st.end_col_offset:].decode(errors="ignore").strip()
        return rest == "" or rest.startswith("#")

    cands = []
    for n in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            body = getattr(n, field, None)
            if not isinstance(body, list):
                continue
            for i in range(len(body) - 1):
                a, b = body[i], body[i + 1]
                ka, kb = kind(a, shadowed), kind(b, shadowed)
                if ka is None or ka != kb:
                    continue
                if isinstance(n, ast.Module) and i == 0 and isinstance(a, ast.ImportFrom) and a.module == "__future__":
                    continue
                if a.end_lineno >= b.lineno or not whole_lines(a) or not whole_lines(b):
                    continue
                if not independent(a, b):
                    continue
                cands.append((a, b))
    if not cands:
        return None
    rng.shuffle(cands)
    chosen, used = [], set()
    for a, b in cands:
        if id(a) in used or id(b) in used:
            continue
        chosen.append((a, b))
        used |= {id(a), id(b)}
        if len(chosen) >= max_swaps:
            break
    # apply swaps bottom-up on line blocks
    for a, b in sorted(chosen, key=lambda p: -p[0].lineno):
        A = lines[a.lineno - 1 : a.end_lineno]
        mid = lines[a.end_lineno : b.lineno - 1]
        B = lines[b.lineno - 1 : b.end_lineno]
        lines[a.lineno - 1 : b.end_lineno] = B + mid + A
    text = "".join(lines)
    if text.rstrip("\n") == src.rstrip("\n") or parse(text) is None:
        return None
    return text
