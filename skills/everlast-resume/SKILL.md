---
name: everlast-resume
description: "Start a task from what earlier sessions, models and tools already learned instead of re-exploring: read the vault's user tier (PROFILE.md, ENVIRONMENTS.md) when new to a machine or environment, read the project's ai-docs/INDEX.md and its private sidecar index, open only the solutions, decisions and plans whose title or tags match, pick up HANDOFF.md when continuing unfinished work, and run the prune pass when the docs have gone stale. Use whenever the user says 'pick up where we left off', 'continue', 'resume', 'what do we already know about X', 'did we try this before', 'check the notes first', 'what was decided about', 'what do you know about me / this machine', 'prune / consolidate the docs', or at the start of any non-trivial task in a repo that has an ai-docs/ folder or is registered in the vault. Also for 'refresh everlast-resume' and 'is everlast-resume stale'. Writing new entries is everlast-capture; creating the doc set is everlast-setup; the vault itself is everlast-vault."
---

# everlast resume (read what was paid for before paying again)

Outcome: the task starts with the two or three entries that matter loaded and nothing else, the user's profile honoured, HANDOFF's next single action taken when work continues, and a stale doc set pruned. Evidence: the entries opened appear as file reads in the trace; a prune leaves `log.md` and the index changed.

## Step 0: freshness (every use, one read)

Read `evergreen.json` next to this file. If `verify_at_use` is true, re-check the listed `volatile_claims` first. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then run `evergreen-refresh` in the same session. If `tests.failing` is non-empty, say so and run `evergreen-tune` after the task.

`EVERLAST` means `python "<plugin>/scripts/everlast.py"` with an absolute path (`${CLAUDE_PLUGIN_ROOT}/scripts/everlast.py`; from a skill, `${CLAUDE_SKILL_DIR}/../../scripts/everlast.py`).

## Step 1: the user tier, once per environment

If this is a new tool, machine or vendor for the user (no `[everlast]` line at session start, or the user says so), read `<vault>/user/PROFILE.md` and the section of `<vault>/user/ENVIRONMENTS.md` for this machine and tool, then `<vault>/user/INDEX.md`. `EVERLAST vault where` prints the path. That is how a fresh Copilot or Codex session inherits what Claude learned. Say in one line that you did it. Otherwise skip: the SessionStart hook already printed the orientation.

## Step 2: index first, entries second (the action)

1. `EVERLAST project status <repo>` for the roots. Read the project `INDEX.md` (one read, under 120 lines) and, when the sidecar has entries, its `INDEX.md` too (`EVERLAST resolve <repo> --private`). No doc set: say so and offer `everlast-setup`; do not go looking for notes elsewhere.
2. Match the task against titles and tags. Open the matching entries, at most three to start; open more only when the task reaches that ground. Entries marked `(superseded)` or `(done)` are history: open only when the task is about why something changed.
3. Continuing work: read `HANDOFF.md`. Its "Next single action" is where to start; its "Dead ends hit" is what not to retry. If the hook already printed HANDOFF into context, do not read it again.
4. Before proposing an approach the docs cover, say which entry you rely on and whether its `verified:` date is recent enough to trust. A solution older than the repo's toolchain change is a lead, not a fact: re-verify its command before building on it.
5. Do not load CODEMAP.md, AGENTS.md sections, or plans the task does not touch. The point of the layers is that most of them stay closed.
6. Private entries stay private: quote them to the user, never into a repo-safe file, a commit message, a pull request, or a message to anyone else.

## Step 3: use, then feed back

When an entry's fix or command works again, bump its `verified:` date (edit the frontmatter, `EVERLAST log <repo> --op update --title "<title> re-verified"`, `EVERLAST index <repo>`). When it fails, that is a new dead end: hand it to `everlast-capture` with `--supersedes`. A doc set nobody confirms decays into the indexed equivalent of a stale wiki.

## Step 4: prune when due

Run `EVERLAST lint <repo> --all` when starting substantial work. More than five findings, or `log.md` past 25 entries since the last `prune` line, or the user asks: run the prune pass from [../../protocol/DOC-TYPES.md](../../protocol/DOC-TYPES.md) (merge duplicates, mark contradictions superseded, absolute dates, archive `done`/`abandoned`/`superseded` entries older than 90 days to `archive/`, rebuild the index, log `prune`). The user tier gets the same pass (`--user`) when its index passes 120 lines. Edit entries individually; never regenerate a file.

Trial skills (promoted by `everlast-capture`, `trial: true` under `<repo>/.claude/skills/`): zero uses after ten sessions (`evergreen.py uses --skill <name> --days 30`, or `/skill-doctor`) means move the folder to `<repo>/.claude/skills-retired/`, set the source entry back to `status: active`, log `retire`. Passing suite and real uses: clear `trial`.

## Output

For a resumed task: the entries relied on (paths) and the next action taken. For a new environment: one line saying the profile was read. For a prune: entries merged, superseded, archived; lint before and after.

## While working: capture learnings

If the user corrects you, the same error happens twice, a workaround is found, or an environment fact is discovered, write it to `LEARNINGS.md` now (check existing entries first). If a learning proves a claim above wrong, fix it here, log it in `CHANGELOG.md`, and set `contradiction` in `evergreen.json`.

## Maintenance

This skill is evergreen (topic: how agents retrieve and consolidate prior session knowledge from layered docs across tools: progressive disclosure, index-first loading, memory consolidation passes; tier `moderate`). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) with `evals/evals.json`. Protocol: the installed evergreen plugin ([MAINTENANCE.md](MAINTENANCE.md)). Descended from `ai-docs-resume` (absorbed 2026-09-13).
