"""Step 0: audit Python800 for per-problem sample inputs/expected outputs.
Samples are parsed from Project_CodeNet/problem_descriptions/<pid>.html.
Writes data/samples.json and dataset_audit.md."""
import html, json, os, re, sys
ROOT = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw")
PY800 = os.path.join(ROOT, "Project_CodeNet_Python800")
DESC = os.path.join(ROOT, "Project_CodeNet", "problem_descriptions")
OUT = os.path.join(os.path.dirname(__file__), "..")

HDR = re.compile(r"<h[1-6][^>]*>\s*(Sample\s*Input|Sample\s*Output|入力例|出力例)\s*(\d*)\s*</h[1-6]>\s*(?:<p>\s*</p>\s*)?<pre[^>]*>(.*?)</pre>", re.S | re.I)

def clean(t):
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t).replace("\r", "")
    return t.strip("\n") + "\n"

def parse(pid):
    p = os.path.join(DESC, pid + ".html")
    if not os.path.exists(p):
        return None, "no_description"
    s = open(p, encoding="utf-8", errors="replace").read()
    ins, outs = {}, {}
    for kind, num, body in HDR.findall(s):
        k = kind.lower().replace(" ", "")
        is_in = "input" in k or "入力" in kind
        num = num or "1"
        d = ins if is_in else outs
        d.setdefault(num, clean(body))  # first occurrence wins (EN/JA duplicates)
    keys = sorted(set(ins) & set(outs), key=int)
    if not keys:
        return None, "no_samples_parsed"
    return [{"input": ins[k], "output": outs[k]} for k in keys], "ok"

def main():
    pids = sorted(os.listdir(PY800))
    samples, reasons = {}, {}
    for pid in pids:
        r, why = parse(pid)
        reasons[why] = reasons.get(why, 0) + 1
        if r:
            samples[pid] = r
    json.dump(samples, open(os.path.join(OUT, "data", "samples.json"), "w"), indent=0)
    nsol = sum(len(os.listdir(os.path.join(PY800, p))) for p in pids)
    with open(os.path.join(OUT, "dataset_audit.md"), "w") as f:
        f.write("# Dataset audit (Step 0)\n\n")
        f.write("**Requested dataset** `verifiers-for-code/CodeNet-16K` (Hugging Face): NOT AVAILABLE — Hub API returns 401 / not found "
                "and it does not appear in Hub search. Per the user's fallback, Project CodeNet (IBM) was used instead.\n\n")
        f.write("**Used**: `Project_CodeNet_Python800.tar.gz` (Python solutions) + `Project_CodeNet_metadata.tar.gz` "
                "(problem descriptions containing sample I/O), from the official download links in the IBM/Project_CodeNet README.\n\n")
        f.write("**License**: Project CodeNet repository is Apache-2.0 (LICENSE file in IBM/Project_CodeNet). Dataset is "
                "published by IBM for research use; we do not redistribute it.\n\n")
        f.write(f"- Problems in Python800: {len(pids)}\n- Solutions in Python800: {nsol}\n")
        f.write(f"- Problems with >=1 parsed (sample input, expected output) pair: **{len(samples)}**\n")
        f.write(f"- Parse outcome counts: {reasons}\n")
        f.write(f"- Total sample pairs: {sum(len(v) for v in samples.values())}\n\n")
        f.write("Sample I/O comes from problem-description HTML (\"Sample Input k\"/\"Sample Output k\" blocks). "
                "Problems whose answers allow multiple correct outputs or float tolerance are filtered later because the "
                "original program must reproduce the expected output exactly (Step 2).\n")
    print(len(pids), len(samples), reasons)

if __name__ == "__main__":
    main()
