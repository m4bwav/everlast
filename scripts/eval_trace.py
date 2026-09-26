"""Print the tool calls of one eval run in order, from the trace a regex or tool grader kept in the result JSON.

python scripts/eval_trace.py evals/results/<RUN>/<case>.json [with|without] [RUN_NUMBER]

Uses the longest grader evidence of the run (regex and tool graders see every message; an llm judge's evidence is elided
in the middle, L-009). Prints each tool call's name and the start of its input, and the start of each result.
"""
import json
import sys

path = sys.argv[1]
arm = sys.argv[2] if len(sys.argv) > 2 else "with"
n = int(sys.argv[3]) if len(sys.argv) > 3 else 1
r = json.load(open(path, encoding="utf8"))["cases"][0]["arms"][arm][n - 1]
print("score %.2f, failing: %s" % (r["score"], [g["name"] for g in r["graders"] if not g.get("passed")]))
for g in r["graders"]:
    if not g.get("passed"):
        print("  %s: %s" % (g["name"], (g.get("explanation") or "")[:200]))
ev = max((g.get("evidence") or "" for g in r["graders"]), key=len)
for line in ev.splitlines():
    try:
        o = json.loads(line)
    except ValueError:
        print("   ..", line[:100])
        continue
    m = o.get("message") or {}
    content = m.get("content") if isinstance(m.get("content"), list) else []
    for c in content:
        if c.get("type") == "tool_use":
            print(">> %s %s" % (c["name"], json.dumps(c["input"])[:300]))
        elif c.get("type") == "tool_result":
            t = c.get("content")
            t = t if isinstance(t, str) else json.dumps(t)
            print("<< %s" % t[:200].replace("\n", " | "))
        elif c.get("type") == "text" and o.get("type") == "assistant":
            print("-- %s" % c["text"][:300].replace("\n", " "))
