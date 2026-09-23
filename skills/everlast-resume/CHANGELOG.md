# Changelog: everlast-resume

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20260923-2 · 2026-09-23 · Changelog header repaired
- because: evergreen L-021 (an insert before the first `### C-` landed inside the Entry shape template); everlast-capture C-20260922-1 fixed the same fault
- files: CHANGELOG.md (Entry shape line restored; the stray template heading removed; C-20260913-1 kept in date order)
- No entry's content changed; the entries are newest first again.

### C-20260923-1 · 2026-09-23 · Check before use, search when the index has no match, verify instead of hand edits, maintain first in the prune pass
- because: the owner's request (the check-before-use info for everlast solutions; no meaning-based search; upkeep depends on the agent); R-20260923-1, R-20260923-2; plugin C-20260923-3 to C-20260923-7; T-20260923-1
- files: SKILL.md (description: search, the stale-fix check, maintain, two trigger phrases; Outcome; Step 1: the SessionStart suffix; Step 2: summaries, `(recheck due)`, `search` before concluding nothing was recorded; new Step 3 Check before use; Step 4 records with `verify`; Step 5 runs `maintain`, then `--apply`, then the judgment items; Output), RESEARCH.md (header, Current understanding, Open questions, Search plan, R-20260923-1, R-20260923-2), evals/evals.json (trigger-3, trigger-4, decoy-3, action-2)
- The old Step 2 item 4 asked the agent to judge whether a `verified:` date was recent enough; the evidence says the check has to be forced, so it is now a step with a command, a safety rule for re-running a stored proof, and a record of the outcome. The body is 60 lines. The evergreen check (magnitude 0.6) moved the unit from tier `moderate` to `fast` (a major change below the moderate minimum); the Maintenance line and the RESEARCH.md header say so.

### C-20260913-1 · 2026-09-13 · Absorbed into the everlast-protocol plugin as `everlast-resume` (from `ai-docs-resume`)
- because: user request (everlast protocol: two tiers, privacy split, excluded mode, cross-tool install); R-20260913-1 to R-20260913-8 in the plugin's RESEARCH.md
- files: SKILL.md (rewritten for the vault, the private sidecar, the user tier and `everlast.py`), evals/evals.json (prompts renamed; capture gained trigger-3 and privacy-1), companions renamed in place
- The skill's history before this entry belongs to `ai-docs-resume` (2026-09-06). `aidocs.py` became `scripts/everlast.py` at the plugin root; its `note`, `handoff`, `index`, `lint`, `log`, `promote-scan`, `skill-budget` and `hook` commands are unchanged in behaviour, with `--private` and `--user` added.

### C-20260906-1 · 2026-09-06 · Created as an evergreen unit (pointer mode)
- because: user request; R-20260906-1; everlast-capture:R-20260906-1, everlast-capture:R-20260906-2
- files: SKILL.md (all sections), RESEARCH.md, LEARNINGS.md, TESTS.md, evals/evals.json, evergreen.json
- Initial version. Tier `moderate`, interval 30d. Index-first loading capped at three entries, HANDOFF next action, re-verify or supersede feedback, lint-triggered prune pass from the shared format reference.

### C-20260906-2 · 2026-09-06 · Trial-skill rollback in Step 3
- because: user request; everlast-capture:R-20260906-5, everlast-capture:R-20260906-6
- files: SKILL.md §Step 3
- Retire an auto-promoted skill with zero uses after ten sessions; clear `trial` when it earns its place.
