# Handoff

## Current state
Plugin 0.4.0, protocol 1.5 on the local branch `release/0.4.0` (2026-09-23): not pushed, not tagged, not merged. New: check before use (`stale_after` by kind, `recheck`, `verify`, `(recheck due)` in the index, protocol principle 6), `search` (BM25 with `aliases`), typed `Related:` links and per-fact stamps in the lint, `maintain` (report; `--apply` archives and relinks), a SessionStart suffix (`recheck due: N (titles) · maintain: M`), `bench/` with `scripts/bench_everlast.py`. Ported from the owner's fork: C-20260918-5 (register merge) and C-20260920-1 (CREATE_NO_WINDOW). Fixed: the Windows default vault path (C-20260923-1, L-004). `python scripts/test_everlast.py` passes 110 checks on Python 3.14 and 3.9 (T-20260923-1).

## In progress
- The `recheck` and `search` eval cases need Bash, which `claude plugin eval` refuses on native Windows (no sandbox backend); run them on Linux or macOS: `claude plugin eval <clone> --case recheck --scaffold --allow-tools Bash Edit Write` (T-20260923-2). The recheck case passed once through the evergreen-tester agent (T-20260923-3).
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
Review `git diff master..release/0.4.0`, merge to `master`, tag `v0.4.0`; then pull it into the private fork (union merge will duplicate C-20260920-1, C-20260918-5, L-003 and L-20260918-1: keep one copy of each) and reinstall the plugin.
