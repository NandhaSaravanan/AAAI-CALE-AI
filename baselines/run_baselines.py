"""Step 5: JPlag and Dolos on the same val/test pair files.
Both tools compare all files within one run, so pairs are processed in chunks: each chunk dir holds
the files of ~150 pairs; we read back only the requested pairs. Similarity = JPlag AVG similarity,
Dolos `similarity`. A pair that a tool cannot score (e.g. JPlag rejects a submission with too few
tokens) gets score 0.0 and is counted in baselines/coverage.json.
Moss: skipped (no user ID)."""
import csv, json, os, shutil, subprocess, sys, zipfile
from concurrent.futures import ThreadPoolExecutor

EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
JAVA = "/opt/homebrew/opt/openjdk/bin/java"
JPLAG = os.path.join(EXP, "tools", "jplag.jar")
DOLOS = os.path.join(EXP, "tools", "dolos", "node_modules", ".bin", "dolos")
WORK = os.path.join(EXP, "work", "baselines")
CHUNK = 150
JPLAG_T = None  # use JPlag default min-token-match for python3


def fname(i):
    return i.replace("/", "__").replace("#", "--") + ".py"


def run_chunk(args):
    tool, split, ci, pairs, src = args
    d = os.path.join(WORK, tool, split, f"c{ci:04d}")
    sub = os.path.join(d, "sub")
    z_prev = os.path.join(d, "res.jplag")
    reuse = tool == "jplag" and os.path.exists(z_prev)  # chunk already finished in an earlier run (same inputs)
    if os.path.exists(d) and not reuse:
        shutil.rmtree(d)
    os.makedirs(sub, exist_ok=True)
    ids = sorted({p["id_a"] for p in pairs} | {p["id_b"] for p in pairs})
    for i in ids:
        with open(os.path.join(sub, fname(i)), "w") as f:
            s = src[i]
            # whitespace normalization for both tools: JPlag ANTLR grammar fails on missing final newline / trailing indented blank lines
            s = "\n".join(l.rstrip() for l in s.splitlines()).rstrip("\n") + "\n"
            f.write(s)
    sim = {}
    if tool == "jplag":
        z = os.path.join(d, "res.jplag")
        if not reuse:
            # --cluster-skip: JPlag's spectral clustering (irrelevant to pairwise scores) can fail to converge,
            # crashing main while a non-daemon progress-bar thread keeps the JVM alive forever.
            try:
                r = subprocess.run([JAVA, "-jar", JPLAG, "-l", "python3", "-M", "RUN", "-n", "-1", "--cluster-skip",
                                    "--overwrite", "-r", os.path.join(d, "res"), sub], capture_output=True, text=True, timeout=600)
                msg = r.stdout[-1500:] + r.stderr[-1500:]
            except subprocess.TimeoutExpired:
                msg = "timeout 600s"
            if not os.path.exists(z):
                return tool, split, ci, None, msg
        with zipfile.ZipFile(z) as zf:
            for name in zf.namelist():
                if name.startswith("comparisons/"):
                    c = json.loads(zf.read(name))
                    sim[(c["firstSubmissionId"], c["secondSubmissionId"])] = c["similarities"]["AVG"]
    else:
        out = os.path.join(d, "out")
        r = subprocess.run([DOLOS, "run", "-l", "python", "-f", "csv", "-o", out] + [os.path.join(sub, fname(i)) for i in ids],
                           capture_output=True, text=True, timeout=1800)
        pc = os.path.join(out, "pairs.csv")
        if not os.path.exists(pc):
            return tool, split, ci, None, r.stdout[-2000:] + r.stderr[-2000:]
        for row in csv.DictReader(open(pc)):
            a, b = os.path.basename(row["leftFilePath"]), os.path.basename(row["rightFilePath"])
            sim[(a, b)] = float(row["similarity"])
    res = []
    for p in pairs:
        a, b = fname(p["id_a"]), fname(p["id_b"])
        s = sim.get((a, b), sim.get((b, a)))
        res.append({"id_a": p["id_a"], "id_b": p["id_b"], "score": float(s) if s is not None else 0.0, "scored": s is not None})
    shutil.rmtree(sub)
    return tool, split, ci, res, None


def main():
    tools = [a for a in sys.argv[1:] if a in ("jplag", "dolos")] or ["jplag", "dolos"]
    splits = [a for a in sys.argv[1:] if a in ("val", "test")] or ["val", "test"]
    src = {}
    for l in open(os.path.join(EXP, "data", "programs.jsonl")):
        p = json.loads(l)
        src[p["id"]] = p["src"]
    os.makedirs(os.path.join(EXP, "eval", "scores"), exist_ok=True)
    cov = json.load(open(os.path.join(EXP, "baselines", "coverage.json"))) if os.path.exists(os.path.join(EXP, "baselines", "coverage.json")) else {}
    errors = []
    for tool in tools:
        for split in splits:
            pairs = [json.loads(l) for l in open(os.path.join(EXP, "data", f"pairs_{split}.jsonl"))]
            chunks = [(tool, split, i // CHUNK, pairs[i:i + CHUNK], src) for i in range(0, len(pairs), CHUNK)]
            out = {}
            with ThreadPoolExecutor(4) as ex:
                for t, s, ci, res, err in ex.map(run_chunk, chunks):
                    if res is None:
                        # retry once
                        t, s, ci, res, err = run_chunk(chunks[ci])
                    if res is None:
                        errors.append(f"{t} {s} chunk {ci}: {err}")
                        res = [{"id_a": p["id_a"], "id_b": p["id_b"], "score": 0.0, "scored": False} for p in chunks[ci][3]]
                    out[ci] = res
            rows = [r for ci in sorted(out) for r in out[ci]]
            with open(os.path.join(EXP, "eval", "scores", f"{tool}_{split}.jsonl"), "w") as f:
                for r in rows:
                    f.write(json.dumps(r) + "\n")
            cov[f"{tool}_{split}"] = {"pairs": len(rows), "scored": sum(r["scored"] for r in rows),
                                      "unscored_set_to_0": sum(not r["scored"] for r in rows)}
            print(tool, split, cov[f"{tool}_{split}"], flush=True)
    json.dump(cov, open(os.path.join(EXP, "baselines", "coverage.json"), "w"), indent=1)
    json.dump({"jplag": {"version": "6.3.0", "language": "python3", "min_tokens": JPLAG_T, "metric": "AVG similarity",
                         "java": JAVA}, "dolos": {"version": "2.10.0", "language": "python", "metric": "similarity",
                                                   "note": "default -M 0.9 fingerprint filter, applied within each 150-pair chunk"},
               "chunk_pairs": CHUNK, "moss": "skipped: no user ID"},
              open(os.path.join(EXP, "configs", "baselines.json"), "w"), indent=1)
    if errors:
        with open(os.path.join(EXP, "ERRORS.md"), "a") as f:
            f.write("\n## Step 5 baseline chunk failures (after 1 retry)\n" + "\n".join(f"- {e[:500]}" for e in errors) + "\n")
    print("errors:", len(errors))


if __name__ == "__main__":
    main()
