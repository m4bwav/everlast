# Learnings: everlast-protocol

Procedural lessons for [README.md](README.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-002 · 2026-09-18 · `run()` strips stdout, so the first `git status --porcelain` line loses its leading space and `ln[3:]` returns a wrong path
- Trigger: the first `project sync` self-test committed `~i-docs/INDEX.md` in its subject; `shareable_changes` (publish) had the same shape since 0.2.0, silently dropping the first unstaged LEARNINGS/RESEARCH file from every pull request.
- Hypothesis: porcelain v1 encodes the unstaged-modified state as a leading space (` M path`); `str.strip()` on the whole output removes it on line one only, so every fixed-offset parse is off by one for that line.
- Rule: never parse `git status --porcelain` from `run()`; use `status_lines()` (unstripped) and keep `ln[:2]` / `ln[3:]`. The same applies to any git output where a leading space is data.
- Evidence: scripts/test_everlast.py "the commit subject lists what was added" (fails on the old parse, passes on `status_lines`).
- helpful: 1 · harmful: 0 · promoted: no

<!-- Example (delete once you have a real entry):
### L-001 · 2026-09-13 · `claude plugin eval` refuses cases that grant Bash on this Windows PC (no sandbox backend)
- Trigger: first eval run; every run with `--allow-tools Bash` exited 1: "sandbox required but unavailable: the Windows sandbox is not active on this session (feature gate off); sandbox.failIfUnavailable is set".
- Hypothesis: plugin eval confines shell tools with an OS sandbox; Windows has none here, so any case whose agent must run `everlast.py` cannot be graded by that harness on this machine.
- Rule: keep `claude plugin eval` cases read-only on Windows (Read, Glob, Grep, Skill; the `resume` case) and prove action cases (capture, privacy) with the evergreen-tester subagent or on a Linux/macOS machine with the sandbox backend installed.
- Evidence: evals/results/first-run.json (2026-09-13, cost $0.002, 4 s, error text above).
- helpful: 0 · harmful: 0 · promoted: no

### L-001 · 2026-09-13 · One-line lesson in plain words
- Trigger: what happened, with dates or counts
- Hypothesis: why
- Rule: the shortest instruction that prevents the trigger
- Evidence: C-20260913-1, T-20260913-1, confirmed 2026-09-13
- Scope: skill | repo:<slug> | env:<name> | global
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-13
-->
