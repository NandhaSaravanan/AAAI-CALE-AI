"""Step 2: correctness check by execution.
Selects originals from Python800, keeps only those that reproduce the expected output on every
sample, generates variants per family, and keeps a variant only if it (1) parses and (2) matches
the expected output on every sample (5 s timeout each, separate subprocess).
Outputs: work/programs.jsonl (originals + verified variants), verify_report.csv."""
import zlib, argparse, ast, csv, json, os, random, subprocess, sys, tempfile, warnings
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
warnings.filterwarnings("ignore")
from transforms import deadcode, rename, reorder  # noqa: E402

EXP = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PY800 = os.path.abspath(os.path.join(EXP, "..", "data", "raw", "Project_CodeNet_Python800"))
FAMILIES = {"rename": rename.transform, "reorder": reorder.transform, "deadcode": deadcode.transform}
TIMEOUT = 5


def norm(s):
    return "\n".join(l.rstrip() for l in s.strip().splitlines())


def run_all(src, samples):
    """Return 'pass', 'mismatch', 'timeout', or 'error' over all samples."""
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "prog.py")
        with open(p, "w", encoding="utf-8") as f:
            f.write(src)
        for s in samples:
            try:
                r = subprocess.run([sys.executable, "-I", "-W", "ignore", p], input=s["input"].encode(),
                                   capture_output=True, timeout=TIMEOUT, cwd=d)
            except subprocess.TimeoutExpired:
                return "timeout"
            if r.returncode != 0:
                return "error"
            if norm(r.stdout.decode("utf-8", "replace")) != norm(s["output"]):
                return "mismatch"
    return "pass"


def job(args):
    pid, sid, samples, n_var = args
    src = open(os.path.join(PY800, pid, sid + ".py"), encoding="utf-8", errors="replace").read()
    out = {"pid": pid, "sid": sid, "orig_status": None, "variants": [], "log": []}
    try:
        ast.parse(src)
    except Exception:
        out["orig_status"] = "parse_fail"
        return out
    out["orig_status"] = run_all(src, samples)
    if out["orig_status"] != "pass":
        return out
    out["src"] = src
    for fam, fn in FAMILIES.items():
        seen = set()
        for k in range(n_var):
            try:
                t = fn(src, seed=zlib.crc32(f"{sid}|{fam}|{k}".encode()))
            except Exception as e:  # transform crashed -> not applicable
                t = None
            if t is None:
                out["log"].append((fam, "not_applicable"))
                continue
            if t in seen:
                out["log"].append((fam, "duplicate"))
                continue
            seen.add(t)
            try:
                ast.parse(t)
            except Exception:
                out["log"].append((fam, "parse_fail"))
                continue
            st = run_all(t, samples)
            out["log"].append((fam, st))
            if st == "pass":
                out["variants"].append({"family": fam, "k": k, "src": t})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--problems", type=int, default=320)
    ap.add_argument("--per_problem", type=int, default=8)
    ap.add_argument("--variants", type=int, default=2)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--workers", type=int, default=9)
    a = ap.parse_args()
    samples = json.load(open(os.path.join(EXP, "data", "samples.json")))
    rng = random.Random(a.seed)
    pids = sorted(samples)
    rng.shuffle(pids)
    pids = pids[: a.problems]
    jobs = []
    for pid in sorted(pids):
        sids = sorted(f[:-3] for f in os.listdir(os.path.join(PY800, pid)) if f.endswith(".py"))
        rng.shuffle(sids)
        # draw extra candidates so that per_problem remain after failures; keep first per_problem passing
        for sid in sids[: a.per_problem * 2]:
            jobs.append((pid, sid, samples[pid], a.variants))
    os.makedirs(os.path.join(EXP, "work"), exist_ok=True)
    results = []
    with ProcessPoolExecutor(a.workers) as ex:
        for i, r in enumerate(ex.map(job, jobs, chunksize=4)):
            results.append(r)
            if i % 500 == 0:
                print(f"{i}/{len(jobs)}", flush=True)
    kept_per_pid, programs = {}, []
    orig_status = {}
    fam_counts = {f: {"originals_attempted": 0, "not_applicable": 0, "duplicate": 0, "parse_fail": 0,
                      "pass": 0, "mismatch": 0, "error": 0, "timeout": 0} for f in FAMILIES}
    for r in results:
        orig_status[r["orig_status"]] = orig_status.get(r["orig_status"], 0) + 1
        if r["orig_status"] != "pass":
            continue
        if kept_per_pid.get(r["pid"], 0) >= a.per_problem:
            continue
        kept_per_pid[r["pid"]] = kept_per_pid.get(r["pid"], 0) + 1
        gid = f'{r["pid"]}/{r["sid"]}'
        programs.append({"id": gid, "pid": r["pid"], "sid": r["sid"], "family": "original", "source_group": gid, "src": r["src"]})
        for f in FAMILIES:
            fam_counts[f]["originals_attempted"] += 1
        for fam, st in r["log"]:
            fam_counts[fam][st] += 1
        for v in r["variants"]:
            programs.append({"id": f'{gid}#{v["family"]}{v["k"]}', "pid": r["pid"], "sid": r["sid"], "family": v["family"],
                             "source_group": gid, "src": v["src"]})
    with open(os.path.join(EXP, "work", "programs.jsonl"), "w") as f:
        for p in programs:
            f.write(json.dumps(p) + "\n")
    with open(os.path.join(EXP, "verify_report.csv"), "w", newline="") as f:
        w = csv.writer(f)
        cols = ["originals_attempted", "not_applicable", "duplicate", "parse_fail", "pass", "mismatch", "error", "timeout"]
        w.writerow(["family", "variant_attempts_per_original"] + cols + ["pass_rate_of_applied"])
        for fam, c in fam_counts.items():
            applied = c["pass"] + c["mismatch"] + c["error"] + c["timeout"] + c["parse_fail"]
            w.writerow([fam, a.variants] + [c[k] for k in cols] + [f"{c['pass'] / applied:.4f}" if applied else "nan"])
    with open(os.path.join(EXP, "work", "originals_status.json"), "w") as f:
        json.dump({"candidates_run": len(results), "status_counts": orig_status, "kept_originals": len(kept_per_pid and programs and [p for p in programs if p["family"] == "original"]),
                   "problems_with_kept": len(kept_per_pid), "args": vars(a)}, f, indent=1)
    print(orig_status, len(programs))
    print(open(os.path.join(EXP, "verify_report.csv")).read())


if __name__ == "__main__":
    main()
