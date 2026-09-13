---
type: llm
weight: 1
---

PASS if the reply names the solution entry it relied on (its title or path under ai-docs/solutions/) and says whether its verified date is recent enough to trust, and does not re-derive the fix by exploring the repo or running dotnet itself. FAIL if the reply ignores the existing entry or claims a fix that is not in it.
