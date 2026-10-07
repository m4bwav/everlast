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
## [2026-09-26] update | C-20260926-3 (plugin 0.4.3): skill descriptions tidied with skill-tidy (lint, triggers, check, apply); capture 1,196 to 1,015 chars, resume 1,420 to 1,018, vault 1,313 to 1,015, setup 988 to 985; T-20260926-2 native plugin eval 21/21 trigger and decoy cases
## [2026-09-26] ingest | Hindsight comparison; plugin 0.5.0 entities, time range, evidence, merge candidates
## [2026-09-26] index | rebuilt (13 entries)
## [2026-09-26] index | rebuilt (13 entries)
## [2026-09-27] handoff | 20 lines
## [2026-09-27] update | 0.5.1: capture and vault research refresh, three scan patterns, install docs corrected (Cowork hooks, ~/.agents/skills, in-place loading)
## [2026-10-03] update | 0.6.1: prepared for the Claude plugin directory (README Hooks/git/files and Privacy sections, plugin.json documentation, support and privacy links, npx skills pinned 1.7.0, publish works from a worktree); C-20261003-2
## [2026-10-04] update | the plugin icon (icon.png in .claude-plugin) for the Claude directory, chosen from two Z-Image candidates. Z-Image Turbo bf16, 9 steps, cfg 1, res_multistep/simple, seed 816420867, prompt "flat vector app icon, bold simple shapes, minimal, centered single motif, thick clean outlines, high contrast, readable at small size, no text, no letters, no numbers, no words, no logos, square composition, an open notebook with an infinity symbol on its cover page, cream notebook and gold symbol on deep maroon background"; white corners painted to the background (95, 16, 51)
## [2026-10-06] update | 0.6.2 for GitHub Copilot and awesome-copilot: root plugin.json (Agent Plugins 1.0, keywords cut to 10), skills link generated copies in references/protocol/ (scripts/sync-skill-refs.py, --check in CI) because vally lint rejects `../../protocol/` links; Mark chose synced copies; C-20261006-1. vally-cli 0.17.0 lint 4/4
