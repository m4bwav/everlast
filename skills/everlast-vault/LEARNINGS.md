# Learnings: everlast-vault

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-001 · 2026-09-27 · `installPath` says cache even when the plugin loads in place; probe what the session loaded
- Trigger: after R-20260927-3 (the loading docs: relative-path plugins in a local-directory marketplace load in place), `everlast-protocol@mark-local` showed `installPath` `cache/mark-local/everlast-protocol/0.4.3` while the source was at 0.5.1; a fresh uninstall and install on 2026-09-27 wrote `cache/.../0.5.1`, and a line appended to the source did not appear in that copy, so the skill said the owner's PC ran a cached copy. On 2026-09-29, on the same PC (Claude Code 2.1.281, VS Code extension), `installPath` still said `cache/mark-local/everlast-protocol/0.5.1`, but the everlast-capture skill loaded with the base directory the clone's `skills/everlast-capture`, the clone; anthropics/claude-code#96223 (open, has repro, 2.1.278 CLI and 2.1.280 Desktop) reports the same split: the CLI loads in place, Desktop's Code tab keeps the cache copy, and `installPath` names the cache in both.
- Hypothesis: the 2026-09-27 check read the cache copy's contents, not what the session loaded; the cache copy exists and goes stale, but the CLI and VS Code extension do not run it. Desktop does.
- Rule: after a source edit, check the loaded path (a skill's "Base directory" line at load, or `CLAUDE_PLUGIN_ROOT` in a hook), never `installPath`; reinstall (marketplace update, uninstall with `--keep-data`, install) only when the loaded path is under `cache/`, which is expected in the Desktop app. Verify a doc-derived install claim against the local binary before writing it into the skill
- Evidence: C-20260927-2, C-20260929-1; `claude plugin list --json` on 2026-09-29 (installPath under cache) against the skill's base directory the same session; anthropics/claude-code#96223
- Scope: env:owner-pc
- Status: active · helpful 1 · harmful 1 · last_confirmed 2026-09-29

<!-- Example (delete once you have a real entry):
### L-001 · 2026-09-13 · One-line lesson in plain words
- Trigger: what happened, with dates or counts
- Hypothesis: why
- Rule: the shortest instruction that prevents the trigger
- Evidence: C-20260913-1, T-20260913-1, confirmed 2026-09-13
- Scope: skill | repo:<slug> | env:<name> | global
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-13
-->
