---
name: everlast-vault
description: "Run the everlast vault, the git repository holding what AI agents learned for and about the user across machines, models and tools: create it, back it up to a private remote (named, or created with gh), check and sync it (status, commit, push the learnings, pull), run the privacy check before notes reach a shared repository (people, politics, credentials, internal names), bring everlast to a new machine or agent product (Claude Code, Cowork, Copilot, Codex), and list the registered projects. Use whenever the user says 'set up everlast here', 'install everlast on a new machine', 'back up the vault', 'create a repo for the notes', 'sync the vault', 'is the vault behind', 'scan for private info', 'export the skills to Copilot', 'pack the plugin for Cowork', 'where is the vault', or the session-start line says it is missing or behind. Also for 'refresh everlast-vault' and 'is everlast-vault stale'. Setting up one codebase is everlast-setup; writing entries is everlast-capture; reading is everlast-resume."
---

# everlast vault (one private repository, every machine, every tool)

Outcome: the vault exists, is a git repository with a private remote, is current on this machine, and the plugin is installed in every agent product the user runs here. Evidence: `everlast.py vault status` output, `git log` in the vault, `claude plugin list`, the exported skill folders.

## Step 0: freshness (every use, one read)

Read `evergreen.json` next to this file. If `verify_at_use` is true, re-check the listed `volatile_claims` first. If `contradiction` is set or today is on or after `next_due`, say so in one line, do the task, then run `evergreen-refresh` in the same session. If `tests.failing` is non-empty, say so and run `evergreen-tune` after the task.

`EVERLAST` means `python "<plugin>/scripts/everlast.py"` with an absolute path (`python` on Windows, `python3` on macOS and Linux; stdlib, 3.9+). Portability details per tool: [../../protocol/PORTABILITY.md](../../protocol/PORTABILITY.md).

## Create or find the vault

```
EVERLAST vault where                       # plugin root, vault path, registry, config
EVERLAST vault init [--path P] [--owner N] # scaffold user/ (INDEX, HANDOFF, log, layers, PROFILE.md, ENVIRONMENTS.md), registry.json, config/redact.txt, git init
```

The path comes from `EVERLAST_VAULT`, then `everlast.config.json` at the plugin root (a string or a per-OS map), then `~/everlast-vault`. Keep it off the OS drive when the user has said so. An existing vault on another machine: `git clone <private remote> <path>` instead of `init`, then set the config.

## Back it up (ask once)

```
EVERLAST vault remote                      # the remote, or none plus the question to ask
EVERLAST vault remote <url>                # a private repository the user already has: set origin, push
EVERLAST vault remote --create [name]      # gh repo create --private in the user's account, push, re-check that it is private
```

A vault on one disk is a single point of loss, and the remote's commit history is where the user sees what agents have been writing. So when `vault init` or the SessionStart line says the vault is local only, ask once, in one sentence: the URL of a private repository they already have, or permission to create one (default name `everlast-vault`, always private, `gh auth login` first if `gh` is not signed in). Push nothing until the user answers. Never accept a public remote: the vault names people and machines by design. If the host cannot make a private repository, leave the vault local and say so. Evidence: the `push: ok` line, then `vault status` showing the remote and `ahead 0`.

## Keep it current

```
EVERLAST vault status                      # projects, user-tier entries, remote, dirty, ahead/behind, redact patterns
EVERLAST vault sync [--if-changed] [--message M]   # add, commit, pull --rebase, push; fails soft, never force-pushes
```

The SessionEnd hook runs `sync --if-changed --detach` in Claude Code, and `project sync` for a mode `repo` project (commits its `ai-docs/` alone, pushes the branch when it is sure, opens a pull request when it is not; the rule is in [PROTOCOL.md](../../protocol/PROTOCOL.md) section 2 and the choice is made in `everlast-setup`). Other tools: run `sync` at the end of a session that wrote to the vault, or rely on the next Claude Code session. A rebase conflict is left for a human (`git status` in the vault); the append-only logs merge by union so conflicts are rare. Commit subjects list the files changed (`+new ~changed -gone`), so `git log --oneline` in the vault or the project reads as a record of what was written.

## Privacy scan

```
EVERLAST scan <repo>            # scans <repo>/ai-docs (or a file or folder) for emails, tokens, credentials, @handles, phone numbers, people by role, opinions about people, and every pattern in <vault>/config/redact.txt
```

Run it before a commit that includes a repo-safe doc set, before the vault's first push to a new remote, and when the user asks. It also reports hidden text (invisible characters and tags imitating agent markup, the injection shape in [PRIVACY.md](../../protocol/PRIVACY.md), Hidden text); after a `sync` that pulled another machine's commits, `EVERLAST lint <repo> --user` checks the user tier, and `EVERLAST clean <folder>` removes what it finds. A hit is moved to the private sidecar (`everlast-capture`, `--private`) or redacted; the lint runs the same scan. Add names of coworkers, customers, internal hostnames and codenames to `config/redact.txt` (one regex per line) the first time they come up; that file lives only in the vault. Rules: [PRIVACY.md](../../protocol/PRIVACY.md). The scan is the gate because no credential scanner looks for people, opinions or internal names; for credentials alone, Betterleaks (the Gitleaks author's successor; Gitleaks now takes security fixes only) is an optional second pass where it is installed: `betterleaks dir <path>`. Pattern scanners share blind spots at token boundaries, such as a key ending in a hyphen or wrapped in backticks (arXiv 2609.02983).

## A new machine or a new agent product

1. Clone both repositories: the plugin (`git clone https://github.com/<owner>/everlast-protocol` under the local marketplace root, `~/claude-plugins` or the user's projects folder) and the vault to the path the config names. Private repositories need `gh auth login` once.
2. Claude Code: `claude plugin marketplace add <plugin clone dir>` (the repo carries its own `.claude-plugin/marketplace.json`; a marketplace that already lists it just needs `claude plugin marketplace update`), then `claude plugin install everlast-protocol@everlast --scope user`, `claude plugin list`. Hooks come with it. A plugin installed from a local clone like this loads in place in the CLI and the VS Code extension (edits apply at the next session or `/reload-plugins`), but `installPath` in `claude plugin list --json` shows a `cache/` copy either way, and the Desktop app's Code tab runs that cache copy (anthropics/claude-code#96223; L-001). So after a source edit, check what the session actually loaded, not `installPath`: the "Base directory" line a skill prints when it loads, or `CLAUDE_PLUGIN_ROOT` inside a hook. If that is the clone, nothing to do; if it is under `cache/`, run `claude plugin marketplace update <marketplace>`, `claude plugin uninstall everlast-protocol@<marketplace> --keep-data`, `claude plugin install everlast-protocol@<marketplace> --scope user`. An install from a git URL is always a cached copy; update it with `claude plugin update` after a version bump.
3. Cowork: `EVERLAST pack` writes `everlast-protocol.plugin` (a zip of the plugin folder); Customize > Plugins > Add > Upload plugin. Cowork loads plugin hooks (claude.com/docs/plugins/platform-support, read 2026-09-27), but whether the SessionEnd `sync` reaches the vault from Cowork's environment is untested, so Step 0 in each skill and a `sync` at the end of a session that wrote to the vault stay the mechanism there. A plugin installed on the claude.ai account also loads in Claude Code as `everlast-protocol@synced`; where a local install exists, the local one wins.
4. Copilot CLI and VS Code, Codex, OpenCode, Windsurf, Cursor and Gemini CLI: `EVERLAST export ~` puts the four skills under `~/.agents/skills/` (junctions on Windows, symlinks elsewhere; `--copy` for a real copy), which all six read (each tool's skills docs, 2026-09-27). Do not also link them into `~/.cursor/skills` or `~/.gemini/skills`, which can list each skill twice; the one exception is Cursor's Cloud Agents, which sync only `~/.cursor/skills`. `npx skills@1.7.0 add <owner>/everlast-protocol -g -a <agent>` is the community alternative. Then paste `templates/AGENTS.md.snippet` into the repo's `AGENTS.md` (`templates/copilot-instructions.md.snippet` for Copilot) so the always-on pointer exists there too.
5. Verify: `EVERLAST vault status` (remote set, clean; none: the back-up question above), `EVERLAST project list`, one `everlast-resume` in a project.
6. Record the machine: a section in `<vault>/user/ENVIRONMENTS.md` (what is installed, paths, what works), logged `--user`.

The one-paste prompt for all of this is `templates/INSTALL-PROMPT.txt`.

## Projects

`EVERLAST project list` shows every registered project with its mode and path; `EVERLAST project status <repo>` shows one. Registering is `everlast-setup`. A project that moved: re-run register from the new path (the slug is kept when the old path is gone).

## Later: encryption and other backups

Not built yet, by decision (see the plugin's `ai-docs/decisions/`). When needed: `git-crypt` (slow-moving, 0.8.0 in 2025-09) encrypts chosen paths transparently in git; `sops` with `age` recipients is active but treats markdown as binary, so encrypted notes no longer diff; `gocryptfs` mounts a whole folder agents read transparently but has had no release since 2024-08 and needs `cppcryptfs` on Windows. The vault's layout does not change either way.

## Output

The command outputs named above; for a new machine, a five-line report: plugin installed where, vault path and remote, projects registered, skills exported to which tools, ENVIRONMENTS.md updated.

## While working: capture learnings

If the user corrects you, the same error happens twice, a workaround is found, or an environment fact is discovered, write it to `LEARNINGS.md` now (check existing entries first). If a learning proves a claim above wrong, fix it here, log it in `CHANGELOG.md`, and set `contradiction` in `evergreen.json`.

## Maintenance

This skill is evergreen (topic: cross-tool installation of agent skills and plugins, private git-backed knowledge stores, redaction and encryption at rest for agent notes; tier `fast`). Files: `evergreen.json`, [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md) with `evals/evals.json`. Protocol: the installed evergreen plugin ([MAINTENANCE.md](MAINTENANCE.md)).
