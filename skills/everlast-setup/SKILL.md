---
name: everlast-setup
description: "Give a project the Everlast Protocol's knowledge layer so nothing a session learns is lost: an ai-docs/ doc set (generated INDEX, 50-line HANDOFF, append-only log, decisions/ solutions/ plans/ notes/), registered in the private vault in one of two modes, committed with the repo or kept in an excluded folder junctioned from the vault when the repo must not hold it, plus a private sidecar for anything naming people, politics or credentials, an eight-line AGENTS.md pointer, and the lint. Use whenever the user asks to 'set up everlast', 'set up ai-docs', 'add agent docs to this repo', 'register this project', 'keep the notes out of the repo', 'make the docs private', 'stop the AI from relearning things', or when everlast-capture finds no doc set in a repo. Also for 'refresh everlast-setup' and 'is everlast-setup stale'. Writing entries is everlast-capture; reading them at task start is everlast-resume; the vault itself, a new machine, or export to other tools is everlast-vault."
---

# everlast setup (one small always-on pointer, everything else on demand)

Outcome: the project is registered in the vault in the right mode, its doc set exists (idempotent, existing files adopted), an eight-line block in AGENTS.md tells every agent when to read and write it, and the lint runs clean. Evidence: `everlast.py project status` shows the mode, the files exist, `everlast.py lint` prints its result.

## Step 0: freshness (every use, one read)

Read `evergreen.json` next to this file. If `verify_at_use` is true, re-check the listed `volatile_claims` with one or two searches before relying on them. If `contradiction` is set or today is on or after `next_due`, tell the user in one line, do the task with the current content, then run the refresh (`evergreen-refresh`) in the same session. If `tests.failing` is non-empty, say so in one line and run `evergreen-tune` after the task.

`EVERLAST` below means `python "<plugin>/scripts/everlast.py"` with an absolute path (in Claude Code `${CLAUDE_PLUGIN_ROOT}/scripts/everlast.py`; from a skill, `${CLAUDE_SKILL_DIR}/../../scripts/everlast.py`). Protocol: [../../protocol/PROTOCOL.md](../../protocol/PROTOCOL.md).

## Step 1: is there a vault?

`EVERLAST vault where`. No vault: run `everlast-vault` first (`vault init`, one command) or, on a machine that already has one elsewhere, point `everlast.config.json` or `EVERLAST_VAULT` at it. Do not register projects into a missing vault. A vault with no remote (`vault remote` says local only): ask the one-line back-up question from `everlast-vault` (an existing private repository's URL, or permission to create one) and push nothing until it is answered.

## Step 2: read what the repo already has

Look at the root for `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `CODEMAP.md`, `docs/`, `ai-docs/`, `.claude/rules/`, and any `docs/solutions` or `docs/plans` (Every's compound-engineering layout). Repo conventions win: a repo already running compound-engineering keeps `docs/solutions/` as its root (`--root docs`); say so.

## Step 3: choose the mode and the sync (ask once)

Ask the user one question (two in mode `repo`) unless the answers are already known from the vault registry or the conversation:

- `repo`: the doc set is committed with the project (`<repo>/ai-docs/`). Right for personal repos and teams that want shared agent memory. Private entries still go to the vault sidecar.
- `excluded`: the repo must not carry it (a work repo, a client's, an open-source project, a monorepo with its own rules). The doc set lives in the vault (`<vault>/projects/<slug>/ai-docs/`), is junctioned into the project as `ai-docs/` so paths stay local, and `/ai-docs/` is written to `.git/info/exclude` so it never shows in `git status`. `--no-link` keeps it in the vault only.

Signals for `excluded` without asking: a remote on a company host, a `CODEOWNERS` file, more than one committer in `git shortlog -sn`, or the user has said the repo is work. When in doubt, ask; the cost of a wrong `repo` choice is a leak.

In mode `repo`, also ask how the docs reach the remote (`--sync`):

- `push` (default): at session end everlast commits `ai-docs/` alone, pushes the branch when it is sure (upstream set, not behind after a fetch, every unpushed commit the user's own, push accepted) and opens a pull request from a docs-only `everlast/docs-*` branch when it is not. Right for a personal repo.
- `pr`: always the pull request, never a push of the user's branch. Right for a shared repo, a protected default branch, or a user who reviews everything.
- `off`: git stays the user's; the SessionStart line reports uncommitted or unpushed docs instead.

No remote yet: say so; `push` still commits locally, and the first push happens once a remote exists (an empty remote is pushed to directly).

## Step 4: register and scaffold (the action)

```
EVERLAST project register <repo> --mode repo|excluded [--sync push|pr|off] [--root ai-docs] [--no-link]
EVERLAST project status <repo>
```

Register creates the doc set (or moves an existing `ai-docs/` into the vault store in `excluded` mode), the private sidecar, the junction and the exclusion. Read the printed lines back; they are the evidence. Then `EVERLAST lint <repo>` and fix findings. Claude Code rewrites `.git/info/exclude` on some versions (anthropics/claude-code#84954); the lint checks `git check-ignore` every time and says when to re-run register.

## Step 5: the always-on pointer

Add the block from `templates/AGENTS.md.snippet` to `AGENTS.md` (or the file the repo's agents actually read). Eight lines; do not add more. Claude Code: make sure `CLAUDE.md` holds the import line `@AGENTS.md` (when there is no `CLAUDE.md`, create it from `templates/CLAUDE.md.snippet`, whose first line is that import). Since 2.1.277 Claude Code reads `AGENTS.md` by itself only when no `CLAUDE.md` or `CLAUDE.local.md` exists, and a pointer written in prose loads nothing, so the import line is the one form that loads the block on every version. `.github/copilot-instructions.md` may point at `AGENTS.md` in prose (Copilot reads `AGENTS.md` natively). In `excluded` mode the block goes into a file the repo does not track and `AGENTS.md` stays untouched: `CLAUDE.local.md` (gitignored by Claude Code), starting with the line `@AGENTS.md` when the repository has an `AGENTS.md` (a `CLAUDE.local.md` switches Claude Code's own reading of `AGENTS.md` off, so without the import the repository's rules stop loading), then the block; or `~/.claude/<project>.md` imported from `CLAUDE.local.md`. Record it: `EVERLAST log <repo> --op update --title "AGENTS.md pointer added"`.

## Step 6: hooks (Claude Code only)

Installed as a plugin, the hooks are already active: SessionStart orientation and HANDOFF (with the project's uncommitted or unpushed docs count in mode `repo`), one Stop nudge, SessionEnd vault sync and project docs sync (`project sync`, unless `--sync off`). Running from a bare clone: `EVERLAST hook install` adds them to `~/.claude/settings.json` (ask first; hooks edit the user's settings). Copilot: copy `adapters/copilot/hooks.json` into the repo's `.github/hooks/` only if the user wants the nudge there.

## Step 7: report

Three lines: mode, sync and slug, files created or adopted (public root and sidecar paths), whether AGENTS.md got the block, lint result.

## Output

A registered project, its doc set, the pointer block, lint; a three-line summary.

## While working: capture learnings

If the user corrects you, the same error happens twice, a workaround is found, or an environment fact is discovered, write it to `LEARNINGS.md` now (format in MAINTENANCE.md; check existing entries first: add, update, retire, or nothing). An environment fact also goes to the vault's `user/ENVIRONMENTS.md`. If a learning proves a claim above wrong, fix it here, log it in `CHANGELOG.md`, and set `contradiction` in `evergreen.json`.

## Maintenance

This skill is evergreen (topic: repository layouts, instruction-file conventions, git exclusion mechanics and hooks for AI-agent documentation; tier `moderate`). Files: `evergreen.json` (state), [RESEARCH.md](RESEARCH.md) (findings and search plan), [CHANGELOG.md](CHANGELOG.md) (every change, with reasons), [LEARNINGS.md](LEARNINGS.md) (lessons), [TESTS.md](TESTS.md) with `evals/evals.json` (the cases that prove it). Protocol: the installed evergreen plugin ([MAINTENANCE.md](MAINTENANCE.md) says how to find it). Descended from `ai-docs-setup` (absorbed 2026-09-13; its history is kept in the companions).
