# Log

Append-only. One line per operation: `## [YYYY-MM-DD] op | title` where op is one of add, update, supersede, prune, handoff, index. Newest at the bottom. Never edited, only appended; this is the history the entries themselves do not carry.

## [2026-09-13] init | scaffolded
## [2026-09-13] add | decision: Absorb the ai-docs skills into everlast
## [2026-09-13] add | decision: Separate private vault repository for user-level data
## [2026-09-13] add | decision: Excluded mode: junction from the vault plus git info exclude
## [2026-09-13] add | decision: Privacy classification: rules first, ask when unsure
## [2026-09-13] add | decision: Encryption and off-git backup deferred
## [2026-09-13] add | plan: Everlast rollout
## [2026-09-13] add | note: Research summary behind the plugin design
## [2026-09-13] handoff | 18 lines
## [2026-09-13] update | first eval runs logged; plan and handoff updated
## [2026-09-17] add | solution: Cross-platform audit and research pass before the public release
## [2026-09-18] add | decision: Project docs: push when sure, pull request when not; vault remote asked once
## [2026-09-18] handoff | 18 lines
## [2026-09-20] add | solution: Console windows flash at session end on Windows: detached git needs CREATE_NO_WINDOW
## [2026-09-23] add | decision: Search is lexical (BM25 plus aliases) first; embeddings deferred
## [2026-09-23] add | solution: Vault resolved under the working directory on Windows: %USERPROFILE% was never expanded
## [2026-09-23] index | rebuilt (12 entries)
## [2026-09-23] handoff | 21 lines
## [2026-09-26] update | research refresh C-20260926-1 (R-20260926-1, -2): Claude Code Projects and Cursor Projects memory, handoff comparables (mattpocock handoff 872K installs, temp-dir only), skill-creator's trigger eval does not measure routing (#6253) so recheck tuning uses plugin eval; plugin eval 2.1.283 needs git 2.31 (WSL2 has 2.53.0)
## [2026-09-26] update | tune T-20260926-1 / C-20260926-2 (plugin 0.4.2): suite 5/5 at 3/3 under WSL2; fixes: vault lookup honours the repo argument (L-011, regression test), everlast-resume description for recurring errors, capture/recheck/privacy graders measure the property (L-009, L-010), scripts/eval-wsl.sh + eval_summary.py + eval_trace.py (L-008)
