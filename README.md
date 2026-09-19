# Everlast Protocol

Nothing an AI session learned is lost when you change model, session, tool or vendor. Everlast keeps what agents learn in plain markdown you own, in two tiers, with a privacy split, installed as one plugin in every agent product you use.

- Project tier: an `ai-docs/` doc set per project (solutions with dead ends and the verified command, decisions with reasons and rejected alternatives, living plans, a 50-line HANDOFF, a generated INDEX, an append-only log), committed with the repository, or, when the repository must not carry it, kept in the vault and junctioned into the project as an excluded folder.
- User tier: a private vault repository holding your profile (how you want agents to work, each rule with its reason), your environments (machines, tools, paths, what works where), and lessons that span projects.
- Privacy split: anything naming a person, an opinion about people, a credential, an internal name or a customer goes to a private sidecar in the vault, never to a shared repository. The script scans and refuses; a human can override with a recorded decision.
- Cross-tool: a Claude Code plugin with hooks; a `.plugin` for Cowork; skills exported to `~/.agents/skills` for Copilot, Codex, OpenCode and Windsurf; one link more for Cursor and Gemini.
- Evergreen: every skill and the plugin itself re-research their subject on a schedule, capture learnings, and carry evals that pass on evidence (pointer mode to the installed evergreen plugin).

The spec is [protocol/PROTOCOL.md](protocol/PROTOCOL.md); which documents pay and why is [protocol/DOC-TYPES.md](protocol/DOC-TYPES.md); the privacy rules are [protocol/PRIVACY.md](protocol/PRIVACY.md); per-tool install is [protocol/PORTABILITY.md](protocol/PORTABILITY.md). The evidence behind the design is [RESEARCH.md](RESEARCH.md). This repository is its own everlast project: see [ai-docs/INDEX.md](ai-docs/INDEX.md).

## What you get

| Piece | What it does |
|---|---|
| `skills/everlast-setup` | Register a project in the vault in mode `repo` or `excluded`, scaffold its doc set and private sidecar, add the eight-line AGENTS.md pointer, lint. |
| `skills/everlast-capture` | End of task: harvest what was learned, route it (project, private sidecar, user tier, or elsewhere), classify for privacy, write with the script, rewrite HANDOFF, lint. Promotes recurring procedures to skills, conservatively. |
| `skills/everlast-resume` | Start of task: read the user tier once per new environment, then the index, open only matching entries, take HANDOFF's next action, prune when stale. |
| `skills/everlast-vault` | The vault: init, remote (name a private repository or create one with gh), status, sync (commit, pull --rebase, push), privacy scan, new-machine install, export to other tools, pack for Cowork. |
| `scripts/everlast.py` | Everything deterministic, stdlib only: docs roots, index, lint, privacy scan, project registry, junction and git exclusion, vault remote and sync, project docs sync (push when sure, pull request when not), export, pack, hooks. `scripts/test_everlast.py` is the self-test. |
| `hooks/hooks.json` | Claude Code: SessionStart prints one orientation line and the project HANDOFF; Stop nudges once per session when the tree changed and nothing was written; SessionEnd syncs the vault and the project's doc root in detached processes. |
| `adapters/copilot/hooks.json` | The same SessionStart and SessionEnd for Copilot's `.github/hooks/`. |
| `templates/` | The AGENTS.md block, CLAUDE.md and copilot-instructions snippets, the one-paste install prompt. |
| `evals/` | Cases for `claude plugin eval` (file and regex graders); each skill also carries `evals/evals.json` for trigger tests. |

## Releases and contribution

Official releases are on the Releases page of https://github.com/m4bwav/everlast: each `vX.Y.Z` tag runs the self-test and publishes a zip of the tree, the `.plugin` for Cowork and the install prompt. The self-test also runs on Linux, macOS and Windows on every push. Updates flow in with `git pull`; the other way is opt-in: at install the agent asks once whether this install may open draft pull requests with the plugin's own learnings (four log file kinds, never your vault or project docs), and `everlast.py contribute yes|no` records or changes the answer. `no` means nothing ever leaves the machine.

Comparable tools worth knowing: agentmemory's `handoff` skill (session resume keyed by working directory, an inline `<private>` marker everlast now honours too), `/memory-doctor` and AgentMemora (memory inspectors), and each vendor's own memory (Claude auto-memory, Codex memories, Copilot Memory), which stay machine- or account-local; everlast is the portable layer beside them.

## Install

Paste `templates/INSTALL-PROMPT.txt` into any agent. By hand, Claude Code:

```
git clone https://github.com/m4bwav/everlast <plugins root>/everlast-protocol
git clone <your private vault repository> <vault path from everlast.config.json>   # or: everlast.py vault init, then vault remote <url> | --create
claude plugin marketplace add <plugins root>/everlast-protocol     # or `marketplace update` when one already lists it
claude plugin install everlast-protocol@everlast --scope user
claude plugin list
```

Then in a project: "set up everlast for this repo" (two questions: commit the docs with the repo or keep them out of it; and, when committed, push them at session end, always open a pull request, or leave git to you). At the end of work: "write down what we learned". At the start: "pick up where we left off".

`python` is `python3` on macOS and Linux (the hook probes for whichever runs). Other tools: `python scripts/everlast.py export ~` (skills into `~/.agents/skills`), then the AGENTS.md block. Cowork: `python scripts/everlast.py pack`, upload the `.plugin`. Details: [protocol/PORTABILITY.md](protocol/PORTABILITY.md).

## Using the script

```
python scripts/everlast.py vault where | status | init | sync [--if-changed]
python scripts/everlast.py vault remote [<url> | --create [name]]   # back the vault up: a private repository you name, or one gh creates
python scripts/everlast.py project register <repo> --mode repo|excluded [--sync push|pr|off] [--no-link]
python scripts/everlast.py project status <repo> | list
python scripts/everlast.py project sync <repo> [--dry-run] [--pr]    # mode repo: commit the doc root only, push when sure, pull request when not
python scripts/everlast.py note <repo> --kind solution|decision|plan|note --title "..." --tags a,b [--summary "when to read it"] --body-file f [--private | --user]
python scripts/everlast.py handoff <repo> --body-file f
python scripts/everlast.py lint <repo> [--all]      # budgets, headings, dead paths, stale, duplicates, privacy, exclusion
python scripts/everlast.py scan <repo>              # privacy scan only
python scripts/everlast.py export <target> | pack
python scripts/everlast.py pull [--dry-run]         # update from the official repository; the SessionStart line says when this clone is behind
python scripts/everlast.py contribute [yes|no]      # asked once at install; publish is a no-op until yes
python scripts/everlast.py publish [--dry-run]      # consent-gated draft pull request with the plugin's own learnings
python scripts/test_everlast.py
```

Run it by absolute path; the shell's working directory is usually the project. Every command fails soft unless `--strict` precedes the subcommand, so hooks never break a session.

## Design notes

Five principles settle most edge cases: plain files the user owns (native memories hold pointers only); two tiers, one layout; private by default at the boundary; on demand, not always-on; evidence, not narration. The evidence: three 2026 studies found always-on repository overviews cost tokens without raising success, while distilled setup procedures, solutions with dead ends, and decisions with reasons help when loaded on demand; every vendor's memory is now user-level and private but none survives a product switch, so the only portable layer is markdown in a repository you control. Sources and magnitudes are in [RESEARCH.md](RESEARCH.md).

Deferred by decision: encryption at rest and an off-git backup route (`ai-docs/decisions/`). The layout does not change when they arrive.

## Maintenance

This plugin is an evergreen unit (tier `fast`), in pointer mode to the installed evergreen plugin: [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evergreen.json`, [MAINTENANCE.md](MAINTENANCE.md). Each skill carries the same set. Lineage: the three `ai-docs-*` skills (2026-09-06) were absorbed on 2026-09-13 with their histories.
