"""Final-pass Step 2: leakage checks. Writes leakage_check.md; exit code 1 if any check fails."""
import json, os, sys
from collections import defaultdict

EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
progs = {}
for l in open(os.path.join(EXP, "data", "programs.jsonl")):
    p = json.loads(l)
    progs[p["id"]] = p
pairs = {s: [json.loads(l) for l in open(os.path.join(EXP, "data", f"pairs_{s}.jsonl"))] for s in ("train", "val", "test")}


def norm(src):
    """Whitespace-insensitive normalization: strip each line, drop blank lines."""
    return "\n".join(l.strip() for l in src.splitlines() if l.strip())


res = []
# 1+2: problem IDs and originals per split, from programs actually used in each split's pairs
pid_splits, orig_splits = defaultdict(set), defaultdict(set)
for s, P in pairs.items():
    for p in P:
        for i in (p["id_a"], p["id_b"]):
            pid_splits[progs[i]["pid"]].add(s)
            orig_splits[progs[i]["source_group"]].add(s)
bad_pid = [k for k, v in pid_splits.items() if len(v) > 1]
bad_orig = [k for k, v in orig_splits.items() if len(v) > 1]
res.append(("No problem ID in more than one split", len(pid_splits), len(bad_pid)))
res.append(("No original program (problem+solution ID) in more than one split", len(orig_splits), len(bad_orig)))
# also: programs.jsonl split labels agree with pair membership
mislabeled = sum(1 for s, P in pairs.items() for p in P for i in (p["id_a"], p["id_b"]) if progs[i]["split"] != s)
res.append(("Every paired program's split label matches the pair file it appears in", sum(len(P) * 2 for P in pairs.values()), mislabeled))
# 3: deadcode only in test
dc = {s: sum(1 for p in P for i in (p["id_a"], p["id_b"]) if progs[i]["family"] == "deadcode") for s, P in pairs.items()}
res.append(("Dead-code programs appear only in the test split (train, val counts must be 0)",
            f"train {dc['train']}, val {dc['val']}, test {dc['test']}", dc["train"] + dc["val"]))
# 4: no identical test pair after normalization
ident = [p for p in pairs["test"] if norm(progs[p["id_a"]]["src"]) == norm(progs[p["id_b"]]["src"])]
res.append(("No test pair whose two programs are identical after whitespace normalization", len(pairs["test"]), len(ident)))
ok = all(r[2] == 0 for r in res)
with open(os.path.join(EXP, "leakage_check.md"), "w") as f:
    f.write("# Leakage check (final-pass Step 2)\n\nSource: data/programs.jsonl and data/pairs_{train,val,test}.jsonl; script data/leakage_check.py.\n\n")
    f.write("| check | items checked | violations | result |\n|---|---|---|---|\n")
    for name, n, bad in res:
        f.write(f"| {name} | {n} | {bad} | {'PASS' if bad == 0 else 'FAIL'} |\n")
    f.write(f"\nPairs per split: " + ", ".join(f"{s} {len(P)}" for s, P in pairs.items()) + "\n")
    if ident:
        f.write("\nIdentical test pairs (first 10):\n" + "\n".join(f"- {p['id_a']} vs {p['id_b']} ({p['family']})" for p in ident[:10]) + "\n")
    f.write(f"\n**Overall: {'ALL PASS' if ok else 'FAILURE'}**\n")
print(open(os.path.join(EXP, "leakage_check.md")).read())
sys.exit(0 if ok else 1)
