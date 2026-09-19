# Learnings: everlast-setup

Procedural lessons for [SKILL.md](SKILL.md). Research findings live in [RESEARCH.md](RESEARCH.md); every change is logged in [CHANGELOG.md](CHANGELOG.md); test runs in [TESTS.md](TESTS.md); state in `evergreen.json`. Format and write-time gate: MAINTENANCE.md (LEARNINGS-FORMAT). Retired entries go to LEARNINGS-ARCHIVE.md with a reason.

Write an entry the moment a real signal happens: a user correction, the same error twice, a discovered workaround, an environment fact, a stated preference, a failed test or a failure in use. Check existing entries first (add / update / retire / none). Trigger and Hypothesis are required. Promote after three confirmations; retire when harmful > helpful.

## Active

### L-20260918-1 · 2026-09-18 · Register in `excluded` mode nested an existing `ai-docs/plans/` as `plans/plans/`
- Trigger: registering `D:\m4bwa\Claude\Projects\Ai\indie-ai-scout` (2026-09-18) with a pre-written `ai-docs/plans/` and `ai-docs/decisions/`; the store was scaffolded first, so `shutil.move` put each folder inside its namesake.
- Hypothesis: `shutil.move(src_dir, existing_dir)` moves into, not onto; the loop did not check for an existing target folder.
- Rule: when a source folder and a store folder share a name, merge the files (fixed in `everlast.py` C-20260918-5); after any register of a folder that already had docs, list the store and look for `x/x` nesting.
- Evidence: the nested folders in the vault store on 2026-09-18, flattened by hand; the fix's self-test passes.
- Scope: skill
- Status: active · helpful 1 · harmful 0 · last_confirmed 2026-09-18

(none yet)
