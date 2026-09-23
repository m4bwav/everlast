# Changelog: everlast-setup

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20260923-2 · 2026-09-23 · Changelog header repaired
- because: evergreen L-021 (an insert before the first `### C-` landed inside the Entry shape template); everlast-capture C-20260922-1 fixed the same fault
- files: CHANGELOG.md (Entry shape line restored; the stray template heading removed; C-20260913-1 moved below C-20260918-1)
- No entry's content changed; the entries are newest first again.

### C-20260923-1 · 2026-09-23 · Step 5: CLAUDE.md, and excluded mode's CLAUDE.local.md, import AGENTS.md with an `@AGENTS.md` line; the contradiction is cleared
- because: R-20260923-1; everlast-capture R-20260922-3; the contradiction flagged 2026-09-22 in `evergreen.json`
- files: SKILL.md Step 5, RESEARCH.md (Current understanding; Open questions; R-20260923-1), evergreen.json (contradiction cleared by the check); plugin C-20260923-9 (templates/CLAUDE.md.snippet, protocol/PORTABILITY.md)
- Step 5 used to say `CLAUDE.md` "should only import or point at" AGENTS.md; a prose pointer loads nothing, and a new `CLAUDE.local.md` switches Claude Code's own reading of AGENTS.md off, so both files now start with the import line (in excluded mode, when the repository has an AGENTS.md).

### C-20260918-1 · 2026-09-18 · Step 3 also chooses how mode `repo` docs reach the remote: `--sync push|pr|off`
- because: the owner's request ("really it should just be pushing commits, if it's not sure then a pull request instead") after a project's docs sat in unpushed commits; plugin C-20260918-2
- files: SKILL.md Step 1 (vault without a remote), Step 3 (sync choice and its signals), Step 4 (register flag), Step 6 (hooks), Step 7 (report)
- `push` is the default: the SessionEnd hook commits `ai-docs/` alone and pushes when sure, else opens a docs-only pull request; `pr` always the pull request; `off` leaves git to the user.

### C-20260913-1 · 2026-09-13 · Absorbed into the everlast-protocol plugin as `everlast-setup` (from `ai-docs-setup`)
- because: user request (everlast protocol: two tiers, privacy split, excluded mode, cross-tool install); R-20260913-1 to R-20260913-8 in the plugin's RESEARCH.md
- files: SKILL.md (rewritten for the vault, the private sidecar, the user tier and `everlast.py`), evals/evals.json (prompts renamed; capture gained trigger-3 and privacy-1), companions renamed in place
- The skill's history before this entry belongs to `ai-docs-setup` (2026-09-06). `aidocs.py` became `scripts/everlast.py` at the plugin root; its `note`, `handoff`, `index`, `lint`, `log`, `promote-scan`, `skill-budget` and `hook` commands are unchanged in behaviour, with `--private` and `--user` added.

### C-20260906-1 · 2026-09-06 · Created as an evergreen unit (pointer mode)
- because: user request; R-20260906-1; everlast-capture:R-20260906-1, everlast-capture:R-20260906-3
- files: SKILL.md (all sections), RESEARCH.md, LEARNINGS.md, TESTS.md, evals/evals.json, evergreen.json
- Initial version. Tier `moderate`, interval 30d. Reads the repo's existing conventions first, scaffolds through `everlast.py init` (idempotent, adopts loose files), adds an eight-line AGENTS.md block, offers the Stop/SessionStart nudge hook behind explicit consent, lints.
