# Learnings: everlast-protocol

Procedural lessons for [README.md](README.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-005 · 2026-09-23 · A lint finding on history makes agents rewrite correct text to silence it
- Trigger: in the first `recheck` test run (T-20260923-3) the lint reported a dead backticked path in the superseded entry (the file it named had been deleted, which was the point of the entry) and in the agent's new entry that described the deletion; the agent reworded `app/strings.py` to "the module `app.strings`" in the new entry to clear the finding and left the old one flagged.
- Hypothesis: agents treat every lint finding as something to fix before finishing; a check that is wrong for a class of entries (history, or text about a removal) trades accuracy for a clean lint.
- Rule: a lint check must hold for every entry it runs on; scope it (dead backticked paths only in active entries) instead of expecting agents to ignore findings. When a check can be wrong by design, say so in its message.
- Evidence: T-20260923-3; C-20260923-12; scripts/test_everlast.py "lint reports dead paths in active entries only, not in history".
- helpful: 1 · harmful: 0 · promoted: no

### L-004 · 2026-09-23 · The shipped Windows vault path `%USERPROFILE%\everlast-vault` was never expanded, so the vault resolved under the current directory
- Trigger: `everlast.py vault where` in a clone of the public repository, with no `EVERLAST_VAULT` set, printed `<clone>\%USERPROFILE%\everlast-vault` (2026-09-23). `vault init` there would have created a literal `%USERPROFILE%` folder in whatever directory the shell was in; the owner's fork never showed it because its config holds a real path.
- Hypothesis: `vault_path()` applied `os.path.expanduser`, which expands only `~`; Windows-style `%VAR%` (and `$VAR`) need `os.path.expandvars`. The public default was written for the placeholder commit and never run without an override.
- Rule: expand variables (`os.path.expandvars`) and then `~` on every configured or environment path, and give each shipped default one test run with no override set.
- Evidence: C-20260923-1; scripts/test_everlast.py "vault paths expand environment variables" (fails without `expandvars`, passes with it).
- helpful: 1 · harmful: 0 · promoted: no

### L-003 · 2026-09-20 · A `DETACHED_PROCESS` child on Windows has no console, so every console program it runs (git, ssh, the credential helper) opens its own visible window
- Trigger: closing VS Code on the owner's Windows PC flashed a dozen console windows (2026-09-20). SessionEnd hands the vault and project sync to a detached python; that python ran `git status`, `add`, `commit`, `pull --rebase`, `push` through `run()` with no creation flags, and Windows allocated a fresh console for each one because the parent had none to inherit. In a terminal session nothing shows because the terminal's console is inherited.
- Hypothesis: `DETACHED_PROCESS` removes the console but does not stop children from creating one; only `CREATE_NO_WINDOW` (a hidden console that children inherit) does. Windows ignores `CREATE_NO_WINDOW` when it is combined with `DETACHED_PROCESS` (Process Creation Flags, Microsoft Learn), so on the launcher it changes nothing; the flag on each child call is what hides the windows.
- Rule: every `subprocess` call in a hook path on Windows passes `creationflags=CREATE_NO_WINDOW` (0x08000000); keeping it on the detached launcher too is harmless. evergreen_sync.py had this from the start; copy the pattern, do not rediscover it.
- Evidence: the vault's `.sync.log` shows a sync at every session end with no windows after the fix; evergreen's `detach_self` and its git runner carry the flag and produce no windows; C-20260920-1; ai-docs/solutions/2026-09-20-console-windows-flash-at-session-end-on-windows-detached-git.md.
- helpful: 1 · harmful: 0 · promoted: no

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
