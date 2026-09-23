# Tests: everlast-protocol

Test runs for [README.md](README.md). Cases live in `evals/evals.json`. A failure that taught something is a lesson in [LEARNINGS.md](LEARNINGS.md); a fix it caused is logged in [CHANGELOG.md](CHANGELOG.md) with `because: T-...`; research it triggered is in [RESEARCH.md](RESEARCH.md); counts and the failing list are in `evergreen.json` under `tests`. Rules: MAINTENANCE.md (testing section) and the plugin's `protocol/TESTING.md`.

A test passes on evidence (a tool call in the trace, a file, a marker, a log line), never on the transcript's claim that something was done.

Entry shape: `### T-YYYYMMDD-n · date · harness · env · passed/total`, then one line per failing case (`id · kind · class · what the evidence showed`), then `led to:` (L-, C-, R- ids or none). Newest first. Budget 150 lines; archive older runs to `TESTS-ARCHIVE.md`.

## Runs

### T-20260923-3 · 2026-09-23 · evergreen-tester agent, one run of the `recheck` case (fresh context, the branch's skills read from disk, the case scaffold in a scratch workspace) · owner-pc Claude Code · 1/1
- recheck · action · pass. Tool order from the trace report: read everlast-resume SKILL.md, read INDEX.md, read the solution, `everlast.py recheck` (printed STALE, CHANGED `app/helpers.py` in ac6bf69 on 2026-04-15, MISSING `app/strings.py`), `python -m app.cli --selftest` (ImportError), read the code and `git show ac6bf69`, `everlast.py verify ... --failed "..."`, and only then the first Edit (`app/cli.py` imports `slugify` from `app.text.slug`). Selftest afterwards printed `selftest ok`; neither `app/helpers.py` nor `app/cli.py` contains `app.strings`; `note --supersedes` recorded the new fix and `log.md` shows `verify-failed`, `supersede`, `add`. The final message said the stored fix was past its recheck date, checked, out of date, and not reapplied.
- Caveats: one run, not three; the tester was pointed at the skill folder (the installed plugin is an older version), so this proves the skill's action, not its trigger; the eval harness itself could not run the case on Windows (T-20260923-2).
- Found in passing: `note` added a second H1 when the body brought its own, and `lint` reported a dead path in the superseded entry, so the agent reworded a correct path in the new entry to silence it. Both fixed (C-20260923-12, L-005), with a check each (T-20260923-1).
- led to: C-20260923-12, L-005

### T-20260923-2 · 2026-09-23 · claude plugin eval 2.1.280 (`--case recheck`, `--case search`: one run, no ablation; `--case resume`: three runs per arm with the no-plugin baseline), target the repository path · owner-pc Windows 11 · resume 3/3 (baseline 2/3); recheck and search not runnable here
- resume: with the plugin 3 of 3 runs passed every grader (read-index, read-solution, answer, trust; score 1.00, 7 to 9 turns); without it 2 of 3 passed (score 0.95; one run failed the `trust` rubric); delta +0.05; 126 s, $0.80. Result: `evals/results/resume-2026-09-23.json` (gitignored). The scaffolded entry is fresh, so this proves index-first reading still works with the new SKILL.md, not the check.
- recheck · action · environment · refused before the agent started: "A shell tool (Bash or PowerShell) was granted but this machine cannot confine it ... the Windows sandbox is not active on this session (feature gate off)". The case needs Bash to run `everlast.py recheck`; the harness requires an OS sandbox for shell grants and native Windows has none (the docs say to use WSL2; WSL is not installed here). Score 0.18 came from the one file grader that passes on an untouched tree. Same result for search (score 0, 4 s, $0).
- led to: T-20260923-3 (the recheck case run by the evergreen-tester agent instead); RESEARCH.md Open questions (run both cases on Linux or macOS)

### T-20260923-1 · 2026-09-23 · scripts/test_everlast.py (self-test, local bare remotes, no network needed for the new checks) and scripts/bench_everlast.py · owner-pc Windows 11, Python 3.14 and 3.9.25, git · 110/110
- 55 checks added for 0.4.0 (the suite had 55): `stale_after` defaults by kind, `--stale-after` date and `never`, a bad value refused; the index flag for a stale entry and for an old entry without `stale_after`; `recheck` (stale, cited file changed in git since verified, unchanged and missing files, the Verified-by text, writes nothing, fails soft); `verify --failed` (dated line, due now, log, privacy gate) and `verify` (renewal, log, flag cleared, timeless kept); `note --supersedes` writes a typed link; search (supersede ranking, aliases, stemming, no-match, flags); lint (unknown label, dead Related target, supersedes status, one open contradiction, stale fact stamp); SessionStart suffix present when due, absent when clean, nothing written; `maintain` report and `--apply` (archive layout, links rewritten to and inside the moved entry, Archive heading, prune log, no dead link left); `recheck`, `verify` and `search` in the user tier and the sidecar, `search --all`; `note` keeps a body's own H1; dead paths linted in active entries only; the register merge fix; vault path variables; the benchmark floor.
- Mutation check: reverting the register merge, dropping `expandvars`, removing the status weights in search, and disabling the git lookup in `recheck` each turned exactly the matching check red (one mutation per run, in a scratch copy).
- Benchmark, first run (41 queries, 44 entries, as of 2026-09-23): index scan Recall@1 0.39, Recall@3 0.61, MRR 0.50; `search` 0.90, 0.93, 0.92. Recall@3 by type, index / search: title 1.00 / 1.00, paraphrase 0.00 / 0.70, error 0.86 / 1.00, alias 0.00 / 1.00, tag 1.00 / 1.00, stale 1.00 / 1.00. Out-of-date entries in the top 3 carrying a flag: 29/34 index, 33/33 search; current entry above the out-of-date one in stale probes: 0/6 index, 6/6 search. Search misses at 3: p01, p03, p09 (paraphrases whose words are not in the entry). Identical on Python 3.9.25; about 0.4 s. Floor set to Recall@3 0.90 (`BENCH_FLOOR_R3`).
- Before the first score, the query-type check caught one mislabelled query (an error string filed as alias) and `lint` caught one wrong link in the fixture; both fixed, recorded in bench/README.md.
- SessionStart with the new suffix (it runs the read-only maintain report): 0.18 s on the 44-entry fixture; 1.3 s on 528 synthetic near-duplicate entries, the worst case for the title comparison (hook timeout 10 s; 1.5 s before `duplicate_pairs` reused difflib's index per title).
- led to: C-20260923-1 to C-20260923-8, L-004

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
