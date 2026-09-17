# Changelog: everlast-setup

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-20260913-1 · 2026-09-13 · Absorbed into the everlast-protocol plugin as `everlast-setup` (from `ai-docs-setup`)
- because: user request (everlast protocol: two tiers, privacy split, excluded mode, cross-tool install); R-20260913-1 to R-20260913-8 in the plugin's RESEARCH.md
- files: SKILL.md (rewritten for the vault, the private sidecar, the user tier and `everlast.py`), evals/evals.json (prompts renamed; capture gained trigger-3 and privacy-1), companions renamed in place
- The skill's history before this entry belongs to `ai-docs-setup` (2026-09-06). `aidocs.py` became `scripts/everlast.py` at the plugin root; its `note`, `handoff`, `index`, `lint`, `log`, `promote-scan`, `skill-budget` and `hook` commands are unchanged in behaviour, with `--private` and `--user` added.

### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20260906-1 · 2026-09-06 · Created as an evergreen unit (pointer mode)
- because: user request; R-20260906-1; everlast-capture:R-20260906-1, everlast-capture:R-20260906-3
- files: SKILL.md (all sections), RESEARCH.md, LEARNINGS.md, TESTS.md, evals/evals.json, evergreen.json
- Initial version. Tier `moderate`, interval 30d. Reads the repo's existing conventions first, scaffolds through `everlast.py init` (idempotent, adopts loose files), adds an eight-line AGENTS.md block, offers the Stop/SessionStart nudge hook behind explicit consent, lints.
