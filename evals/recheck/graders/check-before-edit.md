---
type: regex
target: trace
pattern: "^(?:(?!\"name\":\"Edit\"|\"name\":\"Write\"|\"name\":\"MultiEdit\"|sed -i|perl -pi)[\\s\\S])*(?:everlast\\.py[^\\n]{0,400}?\\brecheck\\b|app\\.cli[^\\n]{0,120}?--selftest)"
weight: 3
---

From the start of the trace, a check of the stored fix (`everlast.py ... recheck`, or the selftest) comes before the first code change, whether that change is made with Edit, Write or `sed -i`/`perl -pi` in Bash. Replaces a `tool_order` grader whose `after: Edit` failed a correct run that edited with sed (T-20260926-1). A regex sees every message of the trace.
