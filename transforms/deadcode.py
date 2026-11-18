"""Family 3 (held-out): dead-code insertion.
Inserts, before randomly chosen statements that start their own line, either
  (a) an unused assignment to a fresh name with a constant expression, or
  (b) an opaque never-taken branch: `<fresh> = <c>` followed by `if <fresh> < 0:` whose
      body is plausible code (print/assignment) that is never executed.
Fresh names never collide with existing names. Output is unchanged by construction;
Step 2 re-verifies it by execution.
Returns transformed text or None if not safely applicable."""
import ast
import random

from transforms.common import all_names, fresh_name, parse

BODY_TEMPLATES = [
    "print({v})",
    "{v} = {v} * 2 + 1",
    "{w} = [{v}] * 3",
    "print({v}, {v} + 1)",
    "{w} = {v} // 2",
]


def snippet(rng, taken, indent, unit):
    v = fresh_name(rng, taken)
    c = rng.randint(1, 997)
    if rng.random() < 0.5:
        expr = rng.choice([f"{c}", f"{c} * {rng.randint(2, 9)}", f"[{c}, {rng.randint(0, 99)}]", f"'{v[:3]}'",
                           f"{c} % {rng.randint(2, 9)}", f"len('{v}')"])
        return [f"{indent}{v} = {expr}\n"]
    w = fresh_name(rng, taken)
    body = rng.choice(BODY_TEMPLATES).format(v=v, w=w)
    cond = rng.choice([f"{v} < 0", f"{v} > {c + 1000}", f"{v} == -{c}", f"{v} * {v} < 0"])
    return [f"{indent}{v} = {c}\n", f"{indent}if {cond}:\n", f"{indent}{unit}{body}\n"]


def transform(src, seed=0, n_insert=None):
    tree = parse(src)
    if tree is None:
        return None
    rng = random.Random(seed)
    lines = src.splitlines(keepends=True)
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    # detect indentation unit
    unit = "    "
    for l in lines:
        s = l[: len(l) - len(l.lstrip(" \t"))]
        if s:
            unit = s if "\t" in s else (" " * min(len(s), 4) if len(s) % 4 else "    ")
            if s.startswith("\t"):
                unit = "\t"
            elif len(s) == 2:
                unit = "  "
            break
    spots = []
    for n in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            body = getattr(n, field, None)
            if not isinstance(body, list):
                continue
            for i, st in enumerate(body):
                if isinstance(n, ast.Module) and i == 0:
                    if isinstance(st, ast.ImportFrom) and st.module == "__future__":
                        continue
                    if isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant) and isinstance(st.value.value, str):
                        continue
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and i == 0 and \
                        isinstance(st, ast.Expr) and isinstance(st.value, ast.Constant):
                    continue
                if getattr(st, "decorator_list", None):
                    continue
                line = lines[st.lineno - 1]
                pre = line.encode()[: st.col_offset].decode(errors="ignore")
                if pre.strip() != "" or line.lstrip().startswith("elif"):
                    continue  # stmt shares its line (e.g. after ';' or 'if x: stmt')
                spots.append((st.lineno, pre))
    spots = sorted(set(spots))
    if not spots:
        return None
    k = n_insert or rng.randint(1, min(3, len(spots)))
    chosen = rng.sample(spots, k)
    taken = all_names(tree)
    for lineno, indent in sorted(chosen, reverse=True):
        lines[lineno - 1 : lineno - 1] = snippet(rng, taken, indent, unit)
    text = "".join(lines)
    if parse(text) is None:
        return None
    return text
