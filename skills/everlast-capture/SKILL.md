---
name: everlast-capture
description: "Write down what a work session learned so no future agent, model or tool relearns it: dead ends and their fix with the verified command (solutions), design decisions with reasons and rejected alternatives (decisions), living plans, a short HANDOFF for the next session, and lessons about the user or their machines (user tier), each as its own small file, routed to the project's doc set, its private sidecar (anything naming people, politics, credentials or internal names), or the user tier of the private vault. Use whenever the user says 'document what we learned', 'write that down', 'handoff', 'wrap up', 'before you finish', 'record this decision', 'note the dead end', 'update the plan', 'remember that', 'note that for next time', or when a hook line starting [everlast] appears; also use it unprompted at the end of any task that hit a dead end, verified a non-obvious command, made a design choice, or taught you something about the user. Also for 'refresh everlast-capture' and 'is everlast-capture stale'. Setting up a project is everlast-setup; reading at task start is everlast-resume; the vault and other machines are everlast-vault; skill lessons go to that skill's LEARNINGS.md."
---

# everlast capture (never relearn what a session already paid for)

Outcome: the non-derivable knowledge from this session exists as small files in the right tier, listed in that tier's `INDEX.md`, logged in its `log.md`, with the project `HANDOFF.md` telling the next session where to start. Nothing naming people, politics or credentials is in a shared repository. Evidence: the paths the script prints.

## Step 0: freshness (every use, one read)

Read `evergreen.json` next to this file. If `verify_at_use` is true, re-check the listed `volatile_claims` first. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then run `evergreen-refresh` in the same session. If `tests.failing` is non-empty, say so and run `evergreen-tune` after the task.

`EVERLAST` means `python "<plugin>/scripts/everlast.py"` with an absolute path (`python` on Windows, `python3` on macOS and Linux; stdlib, 3.9+) (`${CLAUDE_PLUGIN_ROOT}/scripts/everlast.py`; from a skill, `${CLAUDE_SKILL_DIR}/../../scripts/everlast.py`). Formats: [../../protocol/DOC-TYPES.md](../../protocol/DOC-TYPES.md). Privacy rules: [../../protocol/PRIVACY.md](../../protocol/PRIVACY.md).

## Step 1: where does this project write?

`EVERLAST project status <repo>` (one call). Unregistered and no `ai-docs/`: run `everlast-setup` first (one question, one command). Unregistered but `ai-docs/` exists: register it in `repo` mode unless the repo looks like work (see setup's signals), then continue. The user tier needs no project: `--user` always resolves to `<vault>/user/`.

## Step 2: harvest candidates from the session

Go through the session once and list every item of these kinds. Be concrete; the reader is a different model in a different tool with no chat history.

| Signal in the session | Candidate | Tier |
|---|---|---|
| Something failed, a cause was suspected and ruled out, then something worked | solution (problem, dead ends, fix, verified command) | project |
| A command or procedure ran and its output confirmed it works here | solution, or a `## Verified by` line on the entry it belongs to | project |
| Two or more options were weighed and one chosen | decision (context, decision, reasons, rejected alternatives, consequences) | project |
| Work stopped part-way, or a plan changed | plan (status, steps, next single action) | project |
| A belief about the code turned out false | solution if it recurs; else a line in HANDOFF "Dead ends hit" | project |
| The session ends with anything unfinished | HANDOFF.md (always, when work is unfinished) | project |
| The user corrected you, stated a preference, or said "I told you before" | `user/PROFILE.md` rule with its reason (edit in place), plus a pointer in native memory | user |
| A fact about this machine or tool: path, port, quirk, what works where | `user/ENVIRONMENTS.md` line under that machine's section | user |
| A lesson that will apply in other projects (a tool's behaviour, a workflow that worked) | user-tier solution or note (`--user`) | user |
| Anything that names a coworker, a customer, an internal hostname or codename, an opinion about a person or team, a credential | the same kind of entry, written `--private` | private sidecar |

## Step 3: route each candidate (most specific home wins)

1. A rule every future session must obey in this repo: `AGENTS.md`, short, with its reason. Not here.
2. Where a system lives, who calls whom: `CODEMAP.md` or the evergreen map. Not here.
3. A lesson about how a skill performs: that skill's `LEARNINGS.md` (`evergreen-learn`). Not here.
4. A research finding about a subject with its own evergreen skill: that skill's `RESEARCH.md`; only the project's conclusion comes here.
5. Everything else that is not derivable from the code in ten seconds of grep: everlast, this skill, at the tier the table gives.

The derivable gate: if a fresh session could get it by reading one file or running one grep, do not write it (three 2026 studies measured always-on repository overviews as pure cost; on-demand, hard-won procedures are what pays). Write what took experimentation, failure, or a conversation to learn.

## Step 4: classify for privacy before writing

Apply [PRIVACY.md](../../protocol/PRIVACY.md) to each candidate. Private by default: any named person other than the user; opinions about people, teams or management; anything from a private conversation; credentials, tokens, internal hostnames, codenames, customer names; salary, HR, legal, health. Repo-safe: technical facts about the code, tools and commands, decisions and their technical reasons, plans. Borderline: ask once, in one line, listing the entries in question; default to private while waiting. The script runs the same scan and refuses a repo-safe write that trips it; `--allow-private` records that a human reviewed it. Never rewrite a sensitive entry into a vague public one; write the full version privately and, if useful, a technical-only public one that names no one.

## Step 5: write it (the action, with evidence)

For each surviving candidate, check the tier's `INDEX.md` for an entry on the same problem or decision. Same topic: update that file (bump `verified:`, add the new dead end or command, tighten the fix) and log `update`. Contradicted: write the new entry with `--supersedes <old relpath>`. Otherwise write the body to a temp file with the required headings, then:

```
EVERLAST note <repo> --kind solution|decision|plan|note --title "<short, searchable>" --tags a,b --body-file <tmp> [--private | --user]
EVERLAST handoff <repo> --body-file <tmp>          # replace, never append; under 50 lines; sections Current state, In progress, Decisions made this session, Dead ends hit, Next single action
```

User-tier profile and environment facts are edits in place to `user/PROFILE.md` and `user/ENVIRONMENTS.md` (a line with its reason under the right heading), logged with `EVERLAST log <repo> --user --op update --title "..."`. Then leave a one-line pointer in the agent's native memory (Claude auto-memory, Codex memories) so the lesson is found even when everlast is not loaded; pointer, never a copy.

Finished work with nothing pending: leave HANDOFF as it is, or reset it if it describes work now done. Then `EVERLAST lint <repo> --all` and fix what it reports.

Writing rules: one entry per problem or decision, not per session. Title is what a future agent would search for. Absolute dates. Paths in backticks. Commands copy-pasteable with the output that proved them. Plain markdown, no tool-specific syntax, because the next reader may be Copilot or Codex.

## Step 5b: promote to a skill, conservatively and without asking

`EVERLAST promote-scan <repo>` lists candidates from evidence (an entry with three or more steps touched on three or more dates, or three solutions sharing a tag) with an overlap and listing-budget verdict. `extend <skill>`: add the procedure to that skill. `blocked`: report it, retire nothing. `eligible`: a one-line invariant becomes an AGENTS.md rule; a multi-step procedure becomes a repo-scoped skill via `evergreen-new` (pointer mode, `"trial": true`), suite written and run with `evergreen-test`. At most one promotion per session; say what was made and that deleting the folder is the undo.

## Step 6: report

Two or three lines: entries added, updated or superseded (paths, with tier), whether HANDOFF was rewritten, anything routed private and why, lint status. "Nothing worth recording" with the reason is a valid outcome and the hook accepts it.

## Prod mechanism (why this fires without being asked)

Cheapest first: the repo's AGENTS.md pointer block names this skill; this description matches end-of-task phrasing; the plugin's Stop hook blocks once per session when the tree changed and no doc was written in eight hours (`[everlast]` line); the SessionEnd hook commits and pushes the vault and, in mode `repo`, the project's doc root (push when sure, pull request when not; `EVERLAST project sync <repo>` does it now, `--dry-run` shows what it would do).

## While working: capture learnings

If the user corrects you, the same error happens twice, a workaround is found, or an environment fact is discovered, write it to `LEARNINGS.md` now (check existing entries first: add, update, retire, or nothing). If a learning proves a claim above wrong, fix it here, log it in `CHANGELOG.md`, and set `contradiction` in `evergreen.json`.

## Maintenance

This skill is evergreen (topic: how AI coding agents capture session knowledge in modular, on-demand documentation across tools, and how sensitive content is kept out of shared repositories; tier `fast`). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) with `evals/evals.json`. Protocol: the installed evergreen plugin ([MAINTENANCE.md](MAINTENANCE.md)). Descended from `ai-docs-capture` (absorbed 2026-09-13).
