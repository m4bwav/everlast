# Handoff

## Current state
Plugin 0.4.3, protocol 1.5 on `master` (2026-09-26). 0.4.3 tidied the four skill descriptions with skill-tidy (all under the 1,024-character spec limit, at most 12 quoted phrases; C-20260926-3); 0.4.2 fixed the vault lookup for a named repo and the recheck undertrigger (C-20260926-2). `python scripts/test_everlast.py` passes 112 checks. Trigger routing for all four skills: 21/21 in a native Windows `claude plugin eval` run on a scratch copy with trigger and decoy cases built from each skill's evals.json (T-20260926-2). 0.4.0 and 0.4.1 went out through pull requests and tags; 0.4.2 was committed straight to master without a tag.

## In progress
- The eval suite runs under WSL2 with `scripts/eval-wsl.sh` (from PowerShell), summarized by `scripts/eval_summary.py`; 5/5 cases at 3/3 on 2026-09-26 (T-20260926-1). Native Windows cannot run the Bash cases (no sandbox backend).
- The external score (LongMemEval-V2 or a STALE-style probe) is planned, not built (RESEARCH.md Open questions).

## Decisions made this session
- Search is lexical first; embeddings wait for a trigger: [the decision](decisions/2026-09-23-search-is-lexical-bm25-plus-aliases-first-embeddings-deferre.md).
- `--stale-after never` writes the literal `never`; omitting the field would make the entry fall back to its kind's window.
- `maintain --apply` only archives and relinks; merging and contradictions stay a judgment call.
- `recheck` stays read-only; the agent re-runs a stored proof only when it is safe.

## Dead ends hit
- A benchmark query filed as alias leaked through camel-case splitting ("SteamAPI" gives "steam"); the query-type check in `bench_everlast.py` caught it before any score.
- Shell heredocs through the agent's Bash tool collapsed `\\` in Python patch scripts once (a `\b` became a backspace in evals.json); edit files with the editor, not heredoc-built Python.

## Next single action
Consider adding the trigger and decoy cases of T-20260926-2 to `evals/` (prompt.md plus a `tool_used: Skill` grader, no scaffold) so routing can be re-checked natively on Windows without the WSL runner; then the external score (RESEARCH.md Open questions).
