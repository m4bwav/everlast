# Learnings: everlast-capture

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-001 · 2026-09-06 · Windows junctions for skill folders must be made from PowerShell, not cmd via Git Bash
- Trigger: creating the suite's six junctions with `cmd //c mklink /J` from the Bash tool failed six times with "filename, directory name, or volume label syntax is incorrect" (quoting mangled by the Bash-to-cmd hop); `New-Item -ItemType Junction` from the PowerShell tool worked first time.
- Hypothesis: Git Bash rewrites the quoted Windows paths before cmd sees them.
- Rule: on Windows, create skill junctions with PowerShell `New-Item -ItemType Junction -Path <link> -Target <source>`; skip Bash for mklink.
- Evidence: this session, 2026-09-06 (six links created)
- Scope: env:owner-pc
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-06

### L-002 · 2026-09-06 · Research findings were about to land in ai-docs instead of the owning skill's RESEARCH.md
- Trigger: the first real use (a Unity + ComfyUI pipeline study run as a test) produced findings about ComfyUI models and MCP servers; the routing table had no row for "a finding about a subject with its own evergreen skill", so the natural move was one big ai-docs note holding everything.
- Hypothesis: the table listed rules, layout, preferences, skill lessons and environment facts but not skill research, because the suite was designed around session incidents rather than research sessions.
- Rule: route subject findings to the owning skill's RESEARCH.md (R- entries, SKILL.md edits, `checked`); write to ai-docs only the repo-specific conclusion, and link the R- ids from it.
- Evidence: C-20260906-3 (SKILL.md §Step 3 rule 6); an image-generation skill's R-20260906-2 to R-20260906-4 and a game project's note written that way
- Scope: skill
- Status: promoted (C-20260906-3) · helpful 1 · harmful 0 · last_confirmed 2026-09-06
