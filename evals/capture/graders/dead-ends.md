---
type: regex
target: trace
pattern: "## Dead ends(?:(?!## )[\\s\\S])*global\\.json"
weight: 1
---

The entry the agent wrote has a Dead ends section naming global.json (the dead ends were kept, not just the fix). A regex over the whole trace, because an llm judge sees only the first and last 12 messages (L-009).
