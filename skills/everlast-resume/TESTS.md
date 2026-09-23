# Tests: everlast-resume

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20260923-1 · 2026-09-23 · claude plugin eval 2.1.280 (`resume`, three runs per arm with the no-plugin baseline) and the evergreen-tester agent (`recheck` case, one run) · owner-pc Claude Code · 2/2
- resume (plugin case, index first) · pass: 3 of 3 runs with the plugin passed read-index, read-solution, answer and trust (score 1.00); the baseline passed 2 of 3 (0.95); plugin T-20260923-2.
- recheck (plugin case; action-2 here) · pass: `everlast.py recheck` and the Verified-by command ran before the first edit, `verify --failed` was recorded, the stale fix was not reapplied, `note --supersedes` captured the new one, and the selftest passed (plugin T-20260923-3). The tester read this SKILL.md from disk, so the trigger was not tested; `claude plugin eval` refused the case on native Windows (no sandbox for Bash).
- Not run: trigger-1 to trigger-4, decoy-1 to decoy-3, outcome-1 (prune with `maintain`); trigger-3, trigger-4 and decoy-3 are new with the changed description.
- led to: plugin C-20260923-12 (two fixes found in the recheck run)

### T-20260906-1 · 2026-09-06 · evergreen-tester subagent (one run per case, not three) · owner-pc Claude Code · 1/1
- action-1 pass (Skill(everlast-resume) invoked; INDEX.md read before any entry; only the matching solutions/ entry opened; answer cited its verified command; no writes)
- Not run: trigger-1, trigger-2, decoys, outcome-1 (prune). Subagent trigger results are a proxy for the main loop.
- led to: none
