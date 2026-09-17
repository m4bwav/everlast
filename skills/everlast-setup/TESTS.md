# Tests: everlast-setup

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20260906-1 · 2026-09-06 · evergreen-tester subagent (one run per case, not three) · home-pc Claude Code · 2/2
- action-1 pass (Skill(everlast-setup) invoked; `everlast.py init` and `lint` in the trace; repo2/ai-docs/{INDEX,HANDOFF,log,README}.md and four folders exist; AGENTS.md block written; no hook, settings untouched)
- decoy-2 pass (everlast-setup not invoked; everlast-capture handled the note)
- Not run: trigger-1, trigger-2, decoy-1, outcome-1. Subagent trigger results are a proxy for the main loop.
- led to: none
