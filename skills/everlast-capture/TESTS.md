# Tests: everlast-capture

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

Case added 2026-09-22 and not yet run: selectivity-1 (at most two entries from a session with five candidates); action-1 and promote-1 matchers now match `everlast.py` (C-20260922-2).

## Runs

### T-20260906-2 · 2026-09-06 · evergreen-tester subagent (one run per case) · owner-pc Claude Code · 2/2
- promote-1 pass (promote-scan verdict `eligible` on a three-date entry; repo-scoped `.claude/skills/rotate-save-fixtures/` created via `evergreen.py init --pointer` with `trial: true`; entry marked `status: promoted`; log has a `promote` line; no question asked)
- promote-decoy-1 pass (promote-scan found no candidate; nothing created; "nothing worth recording")
- Observed: the promoted skill's eval suite was written but not run (cost); `trial` stays true as designed. Not run: trigger-2, decoy-2, action-1, outcome-1.
- led to: none

### T-20260906-1 · 2026-09-06 · evergreen-tester subagent (one run per case, not three) · owner-pc Claude Code · 2/2
- trigger-1 pass (Skill(everlast-capture) invoked; wrote solutions/ and plans/ entries and replaced HANDOFF.md through everlast.py; INDEX.md and log.md updated: file evidence)
- decoy-1 pass (no skill invoked; the preference went to Claude auto-memory, matching the routing rule)
- also observed in everlast-setup decoy-2: capture updated the existing CS0103 entry instead of duplicating it (write-time gate works)
- trigger-1 surfaced a script bug (`handoff --stdin` missing); fixed as C-20260906-2. Not run: trigger-2, decoy-2, action-1, outcome-1. Subagent trigger results are a proxy for the main loop.
- led to: C-20260906-2
