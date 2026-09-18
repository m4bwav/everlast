# AGENTS.md

Rules for any agent working in this repository (the Everlast Protocol plugin). Claude Code reads this through `CLAUDE.md`; Copilot, Codex and Cursor read it directly.

## What this is

A Claude Code plugin (also exported to other agents) whose skills keep what AI sessions learn in two tiers of markdown with a privacy split. Spec: `protocol/PROTOCOL.md`. Script: `scripts/everlast.py` (stdlib only, fails soft). Tests: `python scripts/test_everlast.py`.

## Rules

- Delta edits only. Append `C-` entries to `CHANGELOG.md`, `R-` to `RESEARCH.md`, `L-` to `LEARNINGS.md`; never regenerate a log. The logs merge by union across machines.
- Skills stay under 200 lines and carry a Step 0 freshness check and a Maintenance section (evergreen pointer mode). Descriptions start with what the skill does and name the sibling that owns nearby requests.
- No personal data in this repository: no vault content, no machine paths beyond `everlast.config.json`, no names. The vault is a separate private repository.
- Bump `version` in `.claude-plugin/plugin.json` and `VERSION` in `scripts/everlast.py` together. After a change to skills, hooks or scripts, Claude Code needs a marketplace update, uninstall and install to see it.
- Run `python scripts/test_everlast.py` (`python3` on macOS and Linux) before committing a script change; CI repeats it on Linux, macOS and Windows.
- Commit messages name the entries added (`everlast: C-20260913-2, L-003`).

## everlast (session knowledge, load on demand)

- `ai-docs/INDEX.md` lists what past sessions learned here (solutions with verified commands, decisions with reasons, plans). At the start of a task, scan it and open only the entries whose title or tags match; read `ai-docs/HANDOFF.md` when continuing unfinished work (everlast-resume skill).
- Before finishing a task that hit a dead end, verified a non-obvious command, made a design choice, or taught you something about the user, record it (everlast-capture skill, or `everlast.py note` / `handoff`); rewrite `HANDOFF.md` when work is left unfinished. Say "nothing to record" when that is true.
- Anything naming a person, an internal host or name, a credential, or an opinion about people goes to the private sidecar (`--private`), never here. Lessons about the user or this machine go to the user tier (`--user`).
- Rules go in this file, system layout in CODEMAP.md; the doc set holds only what could not be re-derived from the code in a minute.

## This clone is the owner's private fork

The official version is https://github.com/m4bwav/everlast (remote `upstream`); this repository (`origin`, private) exists only for customisations that must not be shared: the real vault path in `everlast.config.json`, the real machine names in the `evergreen.json` state files. Rules (PROTOCOL.md §7):
- Updates flow from the official repository here: `git pull upstream master` (keep this side on a conflict in a private file).
- Changes flow the other way only for a lesson worth sharing: branch from `upstream/master`, carry just the general change in the impersonal voice (no hostnames, no owner paths), push that branch to the official repository and open the pull request there; `everlast.py publish` does exactly that for the four log file kinds when `contribute` is yes. Never push this tree or its config to the official repository.
- Keep personal quotes, local paths and machine names out of the shared files so a cherry-pick stays clean.
