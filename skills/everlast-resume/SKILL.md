---
name: everlast-resume
description: "Start a task from what earlier sessions, models and tools already learned instead of re-exploring: read the vault's user tier (PROFILE.md, ENVIRONMENTS.md) when new to a machine or environment, read the project's ai-docs/INDEX.md and its private sidecar index, open only the solutions, decisions and plans whose title or tags match (when none does, the top hits of everlast.py search), check a stale fix before acting on it (recheck, re-run its proof when safe, verify or supersede), pick up HANDOFF.md when continuing unfinished work, and run the upkeep pass (maintain) when the docs have gone stale. Use whenever the user says 'pick up where we left off', 'continue', 'resume', 'what do we already know about X', 'did we try this before', 'check the notes first', 'what was decided about', 'is that fix still good', 'we fixed this before', 'this error is back', 'it fails again', 'same problem as last time', 'search the notes', 'what do you know about me / this machine', 'prune / consolidate the docs', or at the start of any non-trivial task in a repo that has an ai-docs/ folder or is registered in the vault, above all before fixing an error the user says was fixed before (a stored fix may be stale: check it before reapplying). Also for 'refresh everlast-resume' and 'is everlast-resume stale'. Writing new entries is everlast-capture; creating the doc set is everlast-setup; the vault itself is everlast-vault."
---

# everlast resume (read what was paid for before paying again)

Outcome: the task starts with the two or three entries that matter loaded and nothing else, every stale one checked before it is acted on, the user's profile honoured, HANDOFF's next single action taken when work continues, and a stale doc set pruned. Evidence: the entries opened appear as file reads in the trace; a check appears as `everlast.py recheck` (or the entry's Verified-by command) before any edit, followed by a `verify` line in `log.md`; a prune leaves `log.md` and the index changed.

## Step 0: freshness (every use, one read)

Read `evergreen.json` next to this file. If `verify_at_use` is true, re-check the listed `volatile_claims` first. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then run `evergreen-refresh` in the same session. If `tests.failing` is non-empty, say so and run `evergreen-tune` after the task.

`EVERLAST` means `python "<plugin>/scripts/everlast.py"` with an absolute path (`python` on Windows, `python3` on macOS and Linux; stdlib, 3.9+) (`${CLAUDE_PLUGIN_ROOT}/scripts/everlast.py`; from a skill, `${CLAUDE_SKILL_DIR}/../../scripts/everlast.py`).

## Step 1: the user tier, once per environment

If this is a new tool, machine or vendor for the user (no `[everlast]` line at session start, or the user says so), read `<vault>/user/PROFILE.md` and the section of `<vault>/user/ENVIRONMENTS.md` for this machine and tool, then `<vault>/user/INDEX.md`. `EVERLAST vault where` prints the path. That is how a fresh Copilot or Codex session inherits what Claude learned. Say in one line that you did it. Otherwise skip: the SessionStart hook already printed the orientation. When that line ends with `recheck due: N (titles)`, those are the entries to check (Step 3) before relying on them; `maintain: M` counts the upkeep items for Step 5.

## Step 2: index first, entries second (the action)

1. `EVERLAST project status <repo>` for the roots. Read the project `INDEX.md` (one read, under 120 lines) and, when the sidecar has entries, its `INDEX.md` too (`EVERLAST resolve <repo> --private`). No doc set: say so and offer `everlast-setup`; do not go looking for notes elsewhere.
2. Match the task against titles, tags and summaries. Open the matching entries, at most three to start; open more only when the task reaches that ground. Entries marked `(superseded)` or `(done)` are history: open only when the task is about why something changed. `(recheck due)` means Step 3 before acting on it.
3. No line matches: before concluding that nothing was recorded, run `EVERLAST search "<key terms: the exact error text, the tool, the feature>" <repo>` (add `--private` when the sidecar has entries, `--user` for cross-project lessons). It ranks every entry by title, aliases, tags, summary and body, so it finds what an index line words differently. Open at most the top two or three hits; no hit means nothing was recorded.
4. Continuing work: read `HANDOFF.md`. Its "Next single action" is where to start; its "Dead ends hit" is what not to retry. If the hook already printed HANDOFF into context, do not read it again.
5. Do not load CODEMAP.md, AGENTS.md sections, or plans the task does not touch. The point of the layers is that most of them stay closed.
6. Private entries stay private: quote them to the user, never into a repo-safe file, a commit message, a pull request, or a message to anyone else.

## Step 3: check before use

A stored fix is a claim with a date. Agents check a memory's source about one time in five unless something forces it, and act on superseded constraints about three times in four; forcing the check added 61 to 74 points in a 2026 study, and GitHub Copilot Memory re-validates every memory against the code before use. So, before acting on a solution or decision that is stale (its index line says `(recheck due)`, its `stale_after` has passed, or files it cites changed since it was verified):

1. `EVERLAST recheck <entry> <repo>` (read-only; the entry is a path, a file name or part of the title): whether it is stale, which cited files changed in git since `verified` and which are missing, and the text of its `## Verified by` section (the command and the output that proved it).
2. Re-run that command only when it is read-only or safe: a build, a test, a status or version query. Never one that deploys, deletes, pushes, sends, pays or changes shared state; for those, re-read the cited files and ask the user.
3. Record the result. It holds: `EVERLAST verify <entry> <repo>` (renews `verified` and `stale_after`, logs `verify`, rebuilds the index). It does not: `EVERLAST verify <entry> <repo> --failed "what broke"` (dated line in Verified by, due now, logs `verify-failed`), then find the fix that holds and hand it to `everlast-capture` with `--supersedes`. Do not apply the old fix in the meantime.
4. Say which entry you relied on and what the check showed: fresh, rechecked and verified, or failed and superseded.

A fresh entry needs no check. The detail is in [../../protocol/DOC-TYPES.md](../../protocol/DOC-TYPES.md) (Check before use).

## Step 4: use, then feed back

When an entry's fix or command works again during the task, record it with `EVERLAST verify <entry> <repo>` (not a hand edit of `verified:`, which would leave `stale_after` behind). When it fails, that is a new dead end: `verify --failed`, then `everlast-capture` with `--supersedes`. A doc set nobody confirms decays into the indexed equivalent of a stale wiki.

## Step 5: prune when due

Run `EVERLAST maintain <repo>` when starting substantial work: a read-only report of entries due for a recheck, archive candidates, near-duplicate titles, open contradictions, dead links and other lint findings (the SessionStart `maintain: M`). More than five items, or `log.md` past 25 entries since the last `prune` line, or the user asks: run `EVERLAST maintain <repo> --apply`, which does only the deterministic part (moves `done`/`abandoned`/`superseded` entries older than 90 days to `archive/`, rewrites every link to them, rebuilds the index, logs `prune`; it never merges, deletes or edits content). Then do the judgment items from the report by hand, per [../../protocol/DOC-TYPES.md](../../protocol/DOC-TYPES.md) (Prune pass): merge duplicate candidates, resolve open contradictions (supersede one, or relabel the link `see also` once both hold), decide each proposed archive (verify, supersede, or mark done or abandoned), absolute dates. The user tier gets the same pass (`--user`) when its index passes 120 lines. Edit entries individually; never regenerate a file.

Trial skills (promoted by `everlast-capture`, `trial: true` under `<repo>/.claude/skills/`): zero uses after ten sessions (`evergreen.py uses --skill <name> --days 30`, or `/skill-doctor`) means move the folder to `<repo>/.claude/skills-retired/`, set the source entry back to `status: active`, log `retire`. Passing suite and real uses: clear `trial`.

## Output

For a resumed task: the entries relied on (paths), what each check showed, and the next action taken. For a new environment: one line saying the profile was read. For a prune: entries archived by `maintain --apply`, entries merged or superseded by hand; the `maintain` count before and after.

## While working: capture learnings

If the user corrects you, the same error happens twice, a workaround is found, or an environment fact is discovered, write it to `LEARNINGS.md` now (check existing entries first). If a learning proves a claim above wrong, fix it here, log it in `CHANGELOG.md`, and set `contradiction` in `evergreen.json`.

## Maintenance

This skill is evergreen (topic: how agents retrieve and consolidate prior session knowledge from layered docs across tools: progressive disclosure, index-first loading, memory consolidation passes; tier `fast` since 2026-09-23). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) with `evals/evals.json`. Protocol: the installed evergreen plugin ([MAINTENANCE.md](MAINTENANCE.md)). Descended from `ai-docs-resume` (absorbed 2026-09-13).
