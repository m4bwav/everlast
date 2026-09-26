"""Summarize claude plugin eval result JSON files, one line per run: python scripts/eval_summary.py evals/results/<RUN> [case ...]

A run with cost 0 and an ERR line never started (see LEARNINGS L-008)."""
import json
import os
import sys

d = sys.argv[1]
cases = sys.argv[2:] or [f[:-5] for f in sorted(os.listdir(d)) if f.endswith(".json")]
total = 0.0
for c in cases:
    r = json.load(open(os.path.join(d, c + ".json"), encoding="utf8"))
    total += r["costUsd"]
    for cs in r["cases"]:
        a = cs["aggregates"]
        print("== %s cost %.2f score %.2f pass %.2f | without %.2f pass %.2f | delta %+.2f" % (
            cs["name"], r["costUsd"], a["score"], a["passRate"], a["scoreWithout"], a.get("passRateWithout", 0), a["delta"]))
        for arm, runs in cs["arms"].items():
            for i, run in enumerate(runs):
                fails = [g["name"] for g in run.get("graders", []) if not g.get("passed")]
                err = (run.get("error") or "")[:80]
                print("   %s#%d %.2f turns %s%s%s" % (arm, i + 1, run["score"], run["turns"],
                                                     " fails=" + ",".join(fails) if fails else "", " ERR " + err if err else ""))
print("total cost %.2f" % total)
