# Tests: everlast-vault

Test runs for [SKILL.md](SKILL.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20261011-1 · 2026-10-11 · claude plugin eval 2.1.281 `--ablation none` (trigger, decoy) · dev-machine, Windows 11 native · 4/4
- Regression run after the plugin's 2026-10-11 refresh (0.6.4), from a worktree of origin/master. Cases exported from this skill's evals.json by `evergreen.py eval-export --out evals/everlast-vault` (plugin eval refuses an eval dir inside skills/), three runs per case, with-plugin arm only (no baseline arm, to hold cost).
- trigger-1, trigger-2: invoked 6/6 ($0.68). decoy-1, decoy-2: invoked 0/6 ($0.35). First run of this skill's cases.
- Action and outcome cases not run (they grant Bash; native Windows has no sandbox for them).
- led to: none

### T-20260913-1 · 2026-09-13 · not yet run · skill · 0/0
- Suite scaffolded; no run recorded. Write the cases in `evals/evals.json` (at least two trigger prompts, two decoys, one action case with evidence, one outcome case), run the baseline without the skill, then run with it (`evergreen-test`).
- led to: none
