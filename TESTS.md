# Tests: everlast-protocol

Test runs for [README.md](README.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20260918-1 · 2026-09-18 · scripts/test_everlast.py (self-test, local bare remotes, no network) · owner-pc Windows 11, Python 3.14, git · 55/55
- Twenty-six checks added for C-20260918-2: `project sync` commits only the doc root and lists the files in the subject; `--if-changed` is silent with nothing to do; an empty remote is pushed with an upstream; a fast-forward branch is pushed directly; a branch behind its upstream gets a docs-only `everlast/docs-*` branch on the remote with the working tree, branch and local branch list untouched; `--pr` forces the route; `--sync off` and re-registration; `vault remote` asks, sets a URL and pushes, never runs gh while a remote exists; SessionStart lines for both. Dry runs against the owner's real vault and three registered projects matched (nothing to push after the manual push; one project reported no remote).
- led to: L-002, C-20260918-2

### T-20260913-2 · 2026-09-13 · evergreen-tester subagent (one run) · owner-pc Claude Code · 1/1
- everlast-capture privacy-1 pass: `everlast.py note` (public, technical-only) then `note --private` (full account) in the scratch repo; grep for the name and `ghp_` over ai-docs/ returned nothing; the private entry carries the name; the raw token value was stored nowhere; the name was appended to the vault's `config/redact.txt`; no question asked; `--allow-private` not used; `lint --all` clean.
- Observed: inside the subagent the Skill tool reported "Unknown skill: everlast-capture" (plugin skills are namespaced `everlast-protocol:everlast-capture` and may not be exposed to subagents); the agent read SKILL.md from disk and followed it. Trigger proof therefore comes from the main loop, not this run.
- led to: L-001 (sandbox), none else

### T-20260913-1 · 2026-09-13 · claude plugin eval 2.1.269 (`--case resume`, one run, no ablation) · owner-pc Claude Code · 1/1
- resume pass: graders read-index, read-solution, answer (regex `winget install Microsoft.DotNet.SDK.9` in the reply), trust (llm) all passed; 13 turns, 39 s, $0.28. Result file `evals/results/resume-run.json`.
- capture and privacy cases could not run in this harness here: any Bash grant is refused without a sandbox backend on Windows (L-001); they were proven with the tester instead (T-20260913-2).
- led to: L-001

### T-20260913-1 · 2026-09-13 · not yet run · plugin · 0/0
- Suite scaffolded; no run recorded. Write the cases in `evals/evals.json` (at least two trigger prompts, two decoys, one action case with evidence, one outcome case), run the baseline without the skill, then run with it (`evergreen-test`).
- led to: none
