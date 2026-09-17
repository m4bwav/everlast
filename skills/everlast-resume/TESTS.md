# Tests: everlast-resume

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20260906-1 · 2026-09-06 · evergreen-tester subagent (one run per case, not three) · home-pc Claude Code · 1/1
- action-1 pass (Skill(everlast-resume) invoked; INDEX.md read before any entry; only the matching solutions/ entry opened; answer cited its verified command; no writes)
- Not run: trigger-1, trigger-2, decoys, outcome-1 (prune). Subagent trigger results are a proxy for the main loop.
- led to: none
