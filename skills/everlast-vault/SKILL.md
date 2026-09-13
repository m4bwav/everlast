---
name: everlast-vault
description: "Run the Everlast Protocol's private vault, the one git repository that carries everything AI agents have learned for and about the user across machines, models and tools: create it (vault init), check it (status, where), commit and push it (sync), scan a repo-safe doc set for content that must stay private (people, politics, credentials, internal names), bring everlast to a new machine or a new agent product (clone the plugin and the vault, install in Claude Code, pack the .plugin for Cowork, export the skills to ~/.agents/skills for Copilot, Codex and others), and list the registered projects. Use whenever the user says 'set up everlast here', 'install everlast', 'new machine', 'sync the vault', 'push the learnings', 'is the vault behind', 'scan for private info', 'privacy check', 'export the skills to Copilot', 'pack the plugin for Cowork', 'where is the vault', 'what projects are registered', or when a session-start line says the vault is missing or behind. Also for 'refresh everlast-vault' and 'is everlast-vault stale'. Per-project setup is everlast-setup; writing entries is everlast-capture; reading is everlast-resume."
---

# everlast vault (one private repository, every machine, every tool)

Outcome: the vault exists, is a git repository with a private remote, is current on this machine, and the plugin is installed in every agent product the user runs here. Evidence: `everlast.py vault status` output, `git log` in the vault, `claude plugin list`, the exported skill folders.

## Step 0: freshness (every use, one read)

Read `evergreen.json` next to this file. If `verify_at_use` is true, re-check the listed `volatile_claims` first. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then run `evergreen-refresh` in the same session. If `tests.failing` is non-empty, say so and run `evergreen-tune` after the task.

`EVERLAST` means `python "<plugin>/scripts/everlast.py"` with an absolute path. Portability details per tool: [../../protocol/PORTABILITY.md](../../protocol/PORTABILITY.md).

## Create or find the vault

```
EVERLAST vault where                       # plugin root, vault path, registry, config
EVERLAST vault init [--path P] [--owner N] # scaffold user/ (INDEX, HANDOFF, log, layers, PROFILE.md, ENVIRONMENTS.md), registry.json, config/redact.txt, git init
```

The path comes from `EVERLAST_VAULT`, then `everlast.config.json` at the plugin root (a string or a per-OS map), then `~/everlast-vault`. Keep it off the OS drive when the user has said so. An existing vault on another machine: `git clone <private remote> <path>` instead of `init`, then set the config. The remote is always private (`gh repo create <owner>/everlast-vault --private`); the vault names people and machines by design.

## Keep it current

```
EVERLAST vault status                      # projects, user-tier entries, remote, dirty, ahead/behind, redact patterns
EVERLAST vault sync [--if-changed] [--message M]   # add, commit, pull --rebase, push; fails soft, never force-pushes
```

The SessionEnd hook runs `sync --if-changed --detach` in Claude Code. Other tools: run `sync` at the end of a session that wrote to the vault, or rely on the next Claude Code session. A rebase conflict is left for a human (`git status` in the vault); the append-only logs merge by union so conflicts are rare.

## Privacy scan

```
EVERLAST scan <repo>            # scans <repo>/ai-docs (or a file or folder) for emails, tokens, credentials, @handles, phone numbers, people by role, opinions about people, and every pattern in <vault>/config/redact.txt
```

Run it before a commit that includes a repo-safe doc set, and when the user asks. A hit is moved to the private sidecar (`everlast-capture`, `--private`) or redacted; the lint runs the same scan. Add names of coworkers, customers, internal hostnames and codenames to `config/redact.txt` (one regex per line) the first time they come up; that file lives only in the vault. Rules: [PRIVACY.md](../../protocol/PRIVACY.md).

## A new machine or a new agent product

1. Clone both repositories: the plugin (`git clone https://github.com/<owner>/everlast-protocol` under the local marketplace root, `~/claude-plugins` or the user's projects folder) and the vault to the path the config names. Private repositories need `gh auth login` once.
2. Claude Code: `claude plugin marketplace add <plugin clone dir>` (the repo carries its own `.claude-plugin/marketplace.json`; a marketplace that already lists it just needs `claude plugin marketplace update`), then `claude plugin install everlast-protocol@everlast --scope user`, `claude plugin list`. Hooks come with it. After editing the source, `claude plugin marketplace update`, uninstall, install (a same-version update does not recopy).
3. Cowork: `EVERLAST pack` writes `everlast-protocol.plugin`; Customize > Plugins > upload. Hooks do not run in Cowork; Step 0 in each skill and this skill's `sync` are the mechanism.
4. Copilot CLI and VS Code, Codex, OpenCode, Windsurf: `EVERLAST export ~` puts the four skills under `~/.agents/skills/` (junctions on Windows, symlinks elsewhere; `--copy` for a real copy), which those tools read. Cursor and Gemini CLI: also link `~/.cursor/skills` and `~/.gemini/skills`, or use `npx skills add <owner>/everlast-protocol -g -a cursor -a gemini-cli`. Then paste `templates/AGENTS.md.snippet` into the repo's `AGENTS.md` (`templates/copilot-instructions.md.snippet` for Copilot) so the always-on pointer exists there too.
5. Verify: `EVERLAST vault status` (remote set, clean), `EVERLAST project list`, one `everlast-resume` in a project.
6. Record the machine: a section in `<vault>/user/ENVIRONMENTS.md` (what is installed, paths, what works), logged `--user`.

The one-paste prompt for all of this is `templates/INSTALL-PROMPT.txt`.

## Projects

`EVERLAST project list` shows every registered project with its mode and path; `EVERLAST project status <repo>` shows one. Registering is `everlast-setup`. A project that moved: re-run register from the new path (the slug is kept when the old path is gone).

## Later: encryption and other backups

Not built yet, by decision (see the plugin's `ai-docs/decisions/`). When needed: `sops` with `age` recipients for per-file encryption that still diffs, or `gocryptfs` for a whole-folder mount agents read transparently; `git-crypt` is stagnant. The vault's layout does not change either way.

## Output

The command outputs named above; for a new machine, a five-line report: plugin installed where, vault path and remote, projects registered, skills exported to which tools, ENVIRONMENTS.md updated.

## While working: capture learnings

If the user corrects you, the same error happens twice, a workaround is found, or an environment fact is discovered, write it to `LEARNINGS.md` now (check existing entries first). If a learning proves a claim above wrong, fix it here, log it in `CHANGELOG.md`, and set `contradiction` in `evergreen.json`.

## Maintenance

This skill is evergreen (topic: cross-tool installation of agent skills and plugins, private git-backed knowledge stores, redaction and encryption at rest for agent notes; tier `fast`). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) with `evals/evals.json`. Protocol: the installed evergreen plugin ([MAINTENANCE.md](MAINTENANCE.md)).
