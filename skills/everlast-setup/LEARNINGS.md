# Learnings: everlast-setup

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-20261027-1 · 2026-10-27 · `${CLAUDE_SKILL_DIR}/../../scripts/everlast.py` does not resolve from the `~/.agents/skills` copy
- Trigger: running everlast-setup from Copilot CLI (skill loaded from `~/.agents/skills/everlast-setup`) on 2026-10-27; `~/.agents/scripts/everlast.py` does not exist (that `scripts/` holds evergreen.py), so every EVERLAST command failed until the plugin clone was found by search.
- Hypothesis: the `~/.agents` tree is the evergreen export, and everlast's skills were copied into it without their plugin's `scripts/`.
- Rule: when the relative path is missing, resolve the plugin root through `everlast.config.json` or the vault registry before searching the disk; consider exporting `scripts/everlast.py` beside the skills.
- Evidence: `python C:\Users\<you>\.agents\scripts\everlast.py` -> Errno 2 on 2026-10-27; worked from the plugin clone.
- Scope: skill
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-27

### L-20261027-2 · 2026-10-27 · The privacy scan treats npm scopes like `@minecraft/server` as social handles
- Trigger: `everlast.py note` refused, and `lint` kept flagging, a decision that named the `@minecraft/server` package inside backticks (2026-10-27).
- Hypothesis: the `@handle` pattern does not skip inline code or a following `/` (npm scope syntax).
- Rule: until the pattern skips `@scope/name` and code spans, reword package names (or write with `--allow-private` and expect lint findings).
- Evidence: three `privacy: @handle (@minecraft)` lint findings on minewright's ai-docs, 2026-10-27.
- Scope: plugin
- Status: active · helpful 0 · harmful 0 · last_confirmed 2026-10-27

### L-20260918-1 · 2026-09-18 · Register in `excluded` mode nested an existing `ai-docs/plans/` as `plans/plans/`
- Trigger: registering a project whose `ai-docs/` already had `plans/` and `decisions/` (2026-09-18); the store was scaffolded first, so `shutil.move` put each folder inside its namesake.
- Hypothesis: `shutil.move(src_dir, existing_dir)` moves into, not onto; the loop did not check for an existing target folder.
- Rule: when a source folder and a store folder share a name, merge the files (fixed in `everlast.py`, plugin everlast-protocol:C-20260918-5); after any register of a folder that already had docs, list the store and look for `x/x` nesting.
- Evidence: the nested folders in the vault store on 2026-09-18, flattened by hand; scripts/test_everlast.py "register --mode excluded merges an existing ai-docs/ into the store instead of nesting plans/plans" (fails without the merge).
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-23
