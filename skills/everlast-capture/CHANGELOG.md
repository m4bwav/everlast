# Changelog: everlast-capture

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-20260913-1 · 2026-09-13 · Absorbed into the everlast-protocol plugin as `everlast-capture` (from `ai-docs-capture`)
- because: user request (everlast protocol: two tiers, privacy split, excluded mode, cross-tool install); R-20260913-1 to R-20260913-8 in the plugin's RESEARCH.md
- files: SKILL.md (rewritten for the vault, the private sidecar, the user tier and `everlast.py`), evals/evals.json (prompts renamed; capture gained trigger-3 and privacy-1), companions renamed in place
- The skill's history before this entry belongs to `ai-docs-capture` (2026-09-06). `aidocs.py` became `scripts/everlast.py` at the plugin root; its `note`, `handoff`, `index`, `lint`, `log`, `promote-scan`, `skill-budget` and `hook` commands are unchanged in behaviour, with `--private` and `--user` added.

### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20260906-1 · 2026-09-06 · Created as an evergreen unit (pointer mode) with the shared format reference and everlast.py
- because: user request; R-20260906-1, R-20260906-2, R-20260906-3, R-20260906-4
- files: SKILL.md (all sections), references/AI-DOCS-FORMAT.md, scripts/everlast.py, RESEARCH.md, LEARNINGS.md, TESTS.md, evals/evals.json, evergreen.json
- Initial version. Tier `fast`, interval 14d. Harvest table, routing rule with the derivable gate, `note`/`handoff`/`lint` procedure with file evidence, the three-layer prod mechanism (AGENTS.md line, description, optional Stop hook). The script is stdlib-only and fail-soft so it can run inside hooks; it ships in this skill and the siblings call it by relative path.

### C-20260906-2 · 2026-09-06 · `everlast.py handoff` accepts `--stdin` as its help text promised
- because: T-20260906-1 (trigger-1 run hit "unrecognized --stdin" and fell back to --body-file)
- files: scripts/everlast.py (handoff parser)
- Added the flag; behaviour otherwise unchanged. Found by the creation-time suite, not by a user, which is the point of running it.

### C-20260906-3 · 2026-09-06 · Routing rule 6: skill research goes to the owning skill's RESEARCH.md, only the repo conclusion to ai-docs
- because: L-002 (first real use, the pipeline study)
- files: SKILL.md §Step 3 (new rule 6, old 6 renumbered 7)
- Out-of-cycle edit; description unchanged so only the trigger cases would need re-running, none were.

### C-20260906-4 · 2026-09-06 · Automatic, conservative skill promotion (Step 4b) with promote-scan and skill-budget
- because: user request (no asking each time an obvious skill is warranted); R-20260906-5, R-20260906-6, R-20260906-7
- files: SKILL.md §Step 4b and §Step 5, scripts/everlast.py (`promote-scan`, `skill-budget`), references/AI-DOCS-FORMAT.md §Promotion, evals/evals.json (promote-1, promote-decoy-1), RESEARCH.md
- Evidence-gated (three steps, three distinct dates, or three solutions per tag), overlap-gated (extend, never duplicate), budget-gated (1% listing cap), repo-scoped, trial until tested, one per session, report not ask. Rollback lives in everlast-resume Step 3.
