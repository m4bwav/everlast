# Handoff

## Current state
Plugin 0.5.1 on `master` (2026-09-27): the research refresh of everlast-capture and everlast-vault (first real pass for vault) plus three new privacy-scan patterns (`github_pat_`, `npm_`, `AIza`) with a test (C-20260927-1; skills C-20260927-1). `python scripts/test_everlast.py` passes 123 checks. Suite cases `capture` and `privacy` 3/3 under WSL2 (T-20260927-1). Install docs now say: Cowork loads plugin hooks (upload via Customize > Plugins > Add > Upload plugin); `export ~` alone covers Codex, Copilot, OpenCode, Windsurf, Cursor and Gemini CLI; a local-clone install loads in place (no reinstall after a source edit). 0.5.0 before that: entities, `--since/--until`, evidence and proof_count, merge candidates ([Hindsight note](notes/2026-09-26-hindsight-comparison.md)).

## In progress
- Eval runner: `scripts/eval-wsl.sh` under WSL2 from PowerShell (from Git Bash set `MSYS_NO_PATHCONV=1`), summary with `scripts/eval_summary.py`.
- everlast-vault has no case in the plugin suite and its own evals.json has never run (audit shows `untested`).
- External score (LongMemEval-V2 or a STALE-style probe): planned, not built.

## Decisions made this session
- `retire_when` (compound-engineering v3.29.0) adopted as a `Retire when:` body line in capture's writing rules; a frontmatter field that `note` writes and `recheck` runs is left open (capture RESEARCH.md Open questions).
- The regex scan stays the privacy gate; Betterleaks is named only as an optional credential pass.
- Earlier: search is lexical first ([decision](decisions/2026-09-23-search-is-lexical-bm25-plus-aliases-first-embeddings-deferre.md)); `maintain --apply` only archives and relinks; `recheck` stays read-only.

## Dead ends hit
- Bash heredocs collapse `\\` in Python patch scripts (hit again 2026-09-27 on a regex patch): write patch scripts with the editor and build backslashes with `chr(92)`.

## Next single action
Run the everlast-vault suite (trigger and decoy cases natively, the sync action case under WSL) and add a vault case to `evals/`; then decide on `retire_when` as a field, and the untested question whether Cowork's SessionEnd hook can reach the vault.
