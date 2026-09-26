---
type: regex
target:
  source: file
  path: ai-docs/INDEX.md
pattern: "solutions/[^)]*(dotnet|net-sdk|sdk)"
flags: i
weight: 1
---

The script's `note` added the new solution to ai-docs/INDEX.md (an index line linking solutions/...dotnet or sdk...).
