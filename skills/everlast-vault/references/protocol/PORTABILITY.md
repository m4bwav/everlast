<!-- Copy of protocol/PORTABILITY.md, written by scripts/sync-skill-refs.py. Edit protocol/PORTABILITY.md and run the script. -->
# Portability: everlast in every agent product

Part of the [Everlast Protocol](PROTOCOL.md). Verified 2026-09-13 against each vendor's docs (sources in [../RESEARCH.md](https://github.com/m4bwav/everlast/blob/master/RESEARCH.md)); re-verified on the plugin's refresh schedule.

## The two repositories

- Plugin: `https://github.com/m4bwav/everlast` (private; may be shared later, it holds no personal data). Clone it under a local marketplace root (under a local marketplace root, for example `~/claude-plugins/everlast`).
- Vault: your own private repository. Either create it empty on any host and give its URL to `everlast.py vault remote <url>` after `vault init`, or let `everlast.py vault remote --create` make a private one with `gh`. Clone it to the path `everlast.config.json` names for the OS (default `~/everlast-vault`) or set `EVERLAST_VAULT`.

The vault is private: `gh auth login` once per machine, or SSH keys. The plugin is public and needs no account to clone.

## Per tool

| Tool | Skills | Hooks | Install |
|---|---|---|---|
| Claude Code | plugin `skills/` | `hooks/hooks.json`: SessionStart, Stop, SessionEnd (plugin hooks run wherever the plugin is enabled; user scope by default) | `claude plugin marketplace add <clone dir>` (or `update` when a marketplace already lists it), `claude plugin install everlast-protocol@everlast --scope user`. A local-clone install loads in place in the CLI and VS Code (verified on 2.1.281, 2026-09-29), though `claude plugin list --json` shows a cache `installPath` regardless; the Desktop app's Code tab runs the cache copy (anthropics/claude-code#96223; everlast-vault L-001). Check a skill's base directory or `CLAUDE_PLUGIN_ROOT`: only when that is under `cache/` does a source edit need marketplace update, uninstall (`--keep-data`), install. A git-URL install is cached per version: bump it, then `claude plugin update` |
| Cowork (desktop) | same, from the packed `.plugin` | `hooks/hooks.json` loads (platform-support table, read 2026-09-27); whether SessionEnd reaches the vault from Cowork is untested, so keep Step 0 and a `vault sync` / `project sync` by hand | `everlast.py pack`, Customize > Plugins > Add > Upload plugin (`everlast-protocol.plugin` is a zip); an account install also syncs into Claude Code as `@synced` |
| Copilot CLI, VS Code Copilot | reads `~/.agents/skills`, `~/.copilot/skills`, repo `.github/skills`, `.claude/skills`, `.agents/skills` | `.github/hooks/*.json` (`sessionStart`, `sessionEnd`, `agentStop`); `adapters/copilot/hooks.json` is the everlast set | `everlast.py export ~` (junctions into `~/.agents/skills`), paste `templates/copilot-instructions.md.snippet` |
| Codex CLI | reads `.agents/skills` up to the repo root and `~/.agents/skills`; not `.claude/skills` | `~/.codex/hooks.json` or a Codex plugin's `hooks/hooks.json` (same events as Claude; SessionEnd budget 1 s) | `everlast.py export ~`; hooks optional, not yet adapted |
| OpenCode, Windsurf | read `~/.agents/skills` and repo `.agents/skills` | none (OpenCode: TS plugins only) | `everlast.py export ~` |
| Cursor | reads `.cursor/skills`, `~/.cursor/skills` and `~/.agents/skills`; Agent Skills native since 2.4 | `~/.cursor/hooks.json` (`sessionStart`, `stop`) | `everlast.py export ~`; link into `~/.cursor/skills` only for Cloud Agents, which sync that folder alone |
| Gemini CLI | reads `.gemini/skills`, `~/.gemini/skills`, with `~/.agents/skills` as an alias that wins within a tier | `settings.json` hooks or an extension's `hooks/hooks.json` | `everlast.py export ~`; a second link into `~/.gemini/skills` would list the skills twice |

`npx skills@1.7.0 add m4bwav/everlast -g -a codex -a github-copilot -a cursor -a gemini-cli -a opencode` is the community installer (vercel-labs/skills); it symlinks from `~/.agents/skills`. Verify the Claude Code link afterwards (open issue #851 sometimes skips it); the plugin install covers Claude Code anyway.

## The always-on pointer per tool

- Claude Code: `CLAUDE.md` imports it with an `@AGENTS.md` line. Since 2.1.277 Claude Code reads `AGENTS.md` by itself only when no `CLAUDE.md` or `CLAUDE.local.md` exists, and a pointer written in prose loads nothing, so the import line is what makes the block load whenever a `CLAUDE.md` is present (and on older versions). In `excluded` mode the block goes into `CLAUDE.local.md` (gitignored), whose first line is `@AGENTS.md` when the repository has an `AGENTS.md` (creating a `CLAUDE.local.md` switches the native reading off), or into `~/.claude/<project>.md` imported from there. Claude Code's `--worktree` copies gitignored files listed in `.worktreeinclude`.
- Copilot: `AGENTS.md` is read natively; `.github/copilot-instructions.md` may hold the same block.
- Codex: `AGENTS.md` (32 KiB cap) plus `~/.codex/AGENTS.md` (keep under 5 KiB).
- Gemini: `GEMINI.md`, or `.gemini/settings.json` with `{"context": {"fileName": "AGENTS.md"}}`.
- Cursor: `.cursor/rules` or `AGENTS.md`.

The block is `templates/AGENTS.md.snippet`, eight lines, unchanged across tools.

## Native memory: pointers only

Each product's memory (Claude auto-memory `MEMORY.md`, Codex `~/.codex/memories/` (generated after a chat idles; `memories.disable_on_external_context` keeps them out of shared contexts), Gemini `~/.gemini/GEMINI.md`) gets one line: where the vault is and that the record lives there. Copilot Memory is server-side with no file to write; rely on the AGENTS.md block. Claude Code `/import` (2.1.213+) and Codex `/import` can migrate settings one time; the vault does not need them.

## Hooks: what the harness gives

Claude Code hook stdin: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active` (Stop). Env: `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_DATA` (survives updates). SessionStart stdout reaches the model; SessionEnd stdout does not and the event shares a 1.5 s budget by default, so the vault sync and the project docs sync are detached processes (`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` lengthens it since 2.1.271, a per-hook `timeout` does too). Do not point `autoMemoryDirectory` at the vault from a repository's settings: with `blockReadsOutsideWorkingDirectories` on, a repo-chosen memory directory is neither read nor written (2.1.273). Stop can block once with `{"decision": "block", "reason": ...}` and must check `stop_hook_active`. Copilot and Cursor hook payloads carry `transcript_path` too; Codex's `SessionEnd` has 1 s.

## A machine with no Python

Every command in this protocol can be done by hand: the layout is folders and markdown, the index is one line per file, the exclusion is one line in `.git/info/exclude`, the sync is `git add -A && git commit && git pull --rebase && git push` in the vault and `git add ai-docs && git commit -- ai-docs && git push` in a mode `repo` project. A recheck is reading the entry's `## Verified by`, `git log --since=<verified> -- <each backticked path>`, re-running the command when it is safe, then editing `verified` and `stale_after` (or adding a `Recheck failed YYYY-MM-DD:` line) and appending a `verify` line to `log.md`; search is `grep -ril` over the entries, aliases included. The script is a convenience.
