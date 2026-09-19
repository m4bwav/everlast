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

## [2026-09-18] fix | register --mode excluded merged instead of nested (0.3.3)
Registering indie-ai-scout with a pre-written ai-docs/ produced plans/plans/ and decisions/decisions/ in the vault store (C-20260918-5, everlast-setup L-20260918-1). Fixed in scripts/everlast.py; self-test passes. Candidate for a pull request to m4bwav/everlast.
