# Learnings: everlast-vault

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-001 · 2026-09-27 · A local-marketplace plugin install is still a cached copy on Claude Code 2.1.281, whatever the docs say
- Trigger: after R-20260927-3 (the loading docs: relative-path plugins in a local-directory marketplace load in place), `everlast-protocol@mark-local` was still running `cache/mark-local/everlast-protocol/0.4.3` while the source was at 0.5.1; a fresh uninstall and install on 2026-09-27 wrote `cache/.../0.5.1`, and a line appended to the source did not appear in that copy
- Hypothesis: the docs describe a newer Claude Code (2.1.283 at the time) than the installed 2.1.281, or the behaviour needs a marketplace added after the change; docs read on the day are not proof of what the local binary does
- Rule: after a source edit, check `installPath` in `claude plugin list --json`; if it is under `cache/`, marketplace update, uninstall with `--keep-data`, install. Verify a doc-derived install claim against the local binary before writing it into the skill
- Evidence: C-20260927-2; `claude plugin list --json` before and after the reinstall
- Scope: env:owner-pc
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-27

<!-- Example (delete once you have a real entry):
### L-001 · 2026-09-13 · One-line lesson in plain words
- Trigger: what happened, with dates or counts
- Hypothesis: why
- Rule: the shortest instruction that prevents the trigger
- Evidence: C-20260913-1, T-20260913-1, confirmed 2026-09-13
- Scope: skill | repo:<slug> | env:<name> | global
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-13
-->
