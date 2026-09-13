---
type: llm
focus: trace
weight: 2
---

PASS if a solution entry was written under ai-docs/solutions/ whose content has a Problem section naming the "no .NET SDKs were found" error, a Dead ends section mentioning PATH and global.json, a Fix naming the winget install, and a Verified by section quoting `dotnet --version` printing 9.0.317. PASS also requires that ai-docs/INDEX.md now lists the entry (the script prints "INDEX.md and log.md updated"). FAIL if the knowledge was only stated in the reply, written to an ad-hoc file outside ai-docs/, or written without the dead ends.
