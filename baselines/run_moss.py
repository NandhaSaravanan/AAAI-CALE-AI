"""Moss baseline on the same val/test pair files as JPlag and Dolos (same 150-pair chunks, same
whitespace normalization of inputs). The Moss user ID is read from the MOSS_USERID environment
variable and is never written to any file. Python client for the documented Moss socket protocol
(moss.stanford.edu:7690), equivalent to the official Perl submission script.
Settings: language python; -m 1000000 (no passage is ignored for being frequent, so a pair's score does
not depend on which other programs share its chunk); -n large so every matched pair is listed.
Pair score = mean of Moss's two "percent of file matched" values / 100 (analogous to JPlag AVG).
Pairs Moss does not list have no matching passage and get score 0 (Moss accepts every file, so every
pair counts as scored). Writes eval/scores/moss_{val,test}.jsonl, work/baselines/moss/<split>/cNNNN.json
(per-chunk cache incl. result URL), and adds moss to baselines/coverage.json and configs/baselines.json."""
import json, os, re, socket, subprocess, sys, time

from run_baselines import CHUNK, EXP, fname

HOST, PORT = "moss.stanford.edu", 7690
MAXMATCHES, SHOW = 1000000, 100000
WORK = os.path.join(EXP, "work", "baselines", "moss")


def norm(s):
    return "\n".join(l.rstrip() for l in s.splitlines()).rstrip("\n") + "\n"


def query(files, comment):
    uid = os.environ["MOSS_USERID"]
    s = socket.create_connection((HOST, PORT), timeout=900)
    f = s.makefile("rb")
    send = lambda b: s.sendall(b if isinstance(b, bytes) else b.encode())
    send(f"moss {uid}\ndirectory 0\nX 0\nmaxmatches {MAXMATCHES}\nshow {SHOW}\nlanguage python\n")
    if f.readline().strip() != b"yes":
        raise RuntimeError("language rejected")
    for k, (name, text) in enumerate(files, 1):
        data = text.encode()
        send(f"file {k} python {len(data)} {name}\n".encode() + data)
    send(f"query 0 {comment}\n")
    url = f.readline().decode().strip()
    send("end\n")
    s.close()
    if not url.startswith("http"):
        raise RuntimeError(f"bad response: {url[:200]}")
    return url


def fetch(url):
    for _ in range(5):
        r = subprocess.run(["curl", "-sL", "--max-time", "120", url], capture_output=True, text=True)
        if r.returncode == 0 and "</HTML>" in r.stdout.upper():
            return r.stdout
        time.sleep(10)
    raise RuntimeError(f"could not fetch {url}")


ROW = re.compile(r'<A HREF="[^"]*match\d+\.html">\s*([^<]+?) \((\d+)%\)\s*</A>', re.I)


def parse(html):
    cells = ROW.findall(html)
    sim = {}
    for (a, pa), (b, pb) in zip(cells[0::2], cells[1::2]):
        sim[(os.path.basename(a.strip()), os.path.basename(b.strip()))] = (int(pa) + int(pb)) / 200
    return sim


def run_chunk(split, ci, pairs, src):
    cache = os.path.join(WORK, split, f"c{ci:04d}.json")
    if os.path.exists(cache):
        return json.load(open(cache))["rows"]
    ids = sorted({p["id_a"] for p in pairs} | {p["id_b"] for p in pairs})
    url = query([(fname(i), norm(src[i])) for i in ids], f"{split}-c{ci:04d}")
    sim = parse(fetch(url))
    rows = []
    for p in pairs:
        a, b = fname(p["id_a"]), fname(p["id_b"])
        s = sim.get((a, b), sim.get((b, a), 0.0))
        rows.append({"id_a": p["id_a"], "id_b": p["id_b"], "score": float(s), "scored": True})
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    json.dump({"url": url, "n_files": len(ids), "n_listed_pairs": len(sim), "rows": rows}, open(cache, "w"))
    return rows


def main():
    splits = [a for a in sys.argv[1:] if a in ("val", "test")] or ["val", "test"]
    limit = next((int(a.split("=")[1]) for a in sys.argv[1:] if a.startswith("--chunks=")), None)
    src = {p["id"]: p["src"] for p in map(json.loads, open(os.path.join(EXP, "data", "programs.jsonl")))}
    covp = os.path.join(EXP, "baselines", "coverage.json")
    cov = json.load(open(covp))
    errors = []
    for split in splits:
        pairs = [json.loads(l) for l in open(os.path.join(EXP, "data", f"pairs_{split}.jsonl"))]
        chunks = [(i // CHUNK, pairs[i:i + CHUNK]) for i in range(0, len(pairs), CHUNK)][:limit]
        out = []
        for ci, P in chunks:
            for attempt in (1, 2):
                try:
                    out += run_chunk(split, ci, P, src)
                    break
                except Exception as e:  # retry once, then log
                    if attempt == 2:
                        errors.append(f"moss {split} chunk {ci}: {e}")
                        out += [{"id_a": p["id_a"], "id_b": p["id_b"], "score": 0.0, "scored": False} for p in P]
                    else:
                        time.sleep(30)
            print(split, ci, len(out), flush=True)
        if limit is None:
            with open(os.path.join(EXP, "eval", "scores", f"moss_{split}.jsonl"), "w") as f:
                for r in out:
                    f.write(json.dumps(r) + "\n")
            cov[f"moss_{split}"] = {"pairs": len(out), "scored": sum(r["scored"] for r in out),
                                    "unscored_set_to_0": sum(not r["scored"] for r in out)}
    if limit is None:
        json.dump(cov, open(covp, "w"), indent=1)
        cp = os.path.join(EXP, "configs", "baselines.json")
        c = json.load(open(cp))
        c["moss"] = {"server": f"{HOST}:{PORT}", "language": "python", "maxmatches(-m)": MAXMATCHES, "show(-n)": SHOW,
                     "metric": "mean of the two percent-matched values / 100; unlisted pair = 0",
                     "user_id": "read from MOSS_USERID environment variable (not stored)", "chunk_pairs": CHUNK}
        json.dump(c, open(cp, "w"), indent=1)
    if errors:
        with open(os.path.join(EXP, "ERRORS.md"), "a") as f:
            f.write("\n## Moss chunk failures (after 1 retry)\n" + "\n".join(f"- {e[:500]}" for e in errors) + "\n")
    print("errors:", len(errors))


if __name__ == "__main__":
    main()
