# Portability: everlast in every agent product

Part of the [Everlast Protocol](PROTOCOL.md). Verified 2026-09-13 against each vendor's docs (sources in [../RESEARCH.md](../RESEARCH.md)); re-verified on the plugin's refresh schedule.

## The two repositories

- Plugin: `https://github.com/m4bwav/everlast-protocol` (private; may be shared later, it holds no personal data). Clone it under a local marketplace root (Mark's machines: `D:\m4bwa\Claude\Projects\Ai\everlast-protocol`, listed in the `mark-local` marketplace; elsewhere `~/claude-plugins/everlast-protocol`).
- Vault: `https://github.com/m4bwav/everlast-vault` (always private). Clone it to the path `everlast.config.json` names for the OS (Mark's Windows machines: `D:\m4bwa\Documents\Everlast\vault`; posix default `~/everlast-vault`) or set `EVERLAST_VAULT`.

Both are private repositories: `gh auth login` once per machine, or SSH keys.

## Per tool

| Tool | Skills | Hooks | Install |
|---|---|---|---|
| Claude Code | plugin `skills/` | `hooks/hooks.json`: SessionStart, Stop, SessionEnd (plugin hooks run wherever the plugin is enabled; user scope by default) | `claude plugin marketplace add <clone dir>` (or `update` when a marketplace already lists it), `claude plugin install everlast-protocol@everlast --scope user`. After a source edit: marketplace update, uninstall, install |
| Cowork (desktop) | same, from the packed `.plugin` | none run in Cowork; Step 0 in each skill and `vault sync` by hand | `everlast.py pack`, Customize > Plugins > upload `everlast-protocol.plugin` |
| Copilot CLI, VS Code Copilot | reads `~/.agents/skills`, `~/.copilot/skills`, repo `.github/skills`, `.claude/skills`, `.agents/skills` | `.github/hooks/*.json` (`sessionStart`, `sessionEnd`, `agentStop`); `adapters/copilot/hooks.json` is the everlast set | `everlast.py export ~` (junctions into `~/.agents/skills`), paste `templates/copilot-instructions.md.snippet` |
| Codex CLI | reads `.agents/skills` up to the repo root and `~/.agents/skills`; not `.claude/skills` | `~/.codex/hooks.json` or a Codex plugin's `hooks/hooks.json` (same events as Claude; SessionEnd budget 1 s) | `everlast.py export ~`; hooks optional, not yet adapted |
| OpenCode, Windsurf | read `~/.agents/skills` and repo `.agents/skills` | none (OpenCode: TS plugins only) | `everlast.py export ~` |
| Cursor | reads `.cursor/skills`, `~/.cursor/skills`; Agent Skills native since 2.4 | `~/.cursor/hooks.json` (`sessionStart`, `stop`) | link `~/.agents/skills/everlast-*` into `~/.cursor/skills`, or `npx skills add m4bwav/everlast-protocol -g -a cursor` |
| Gemini CLI | reads `.gemini/skills`, `~/.gemini/skills` | `settings.json` hooks or an extension's `hooks/hooks.json` | link into `~/.gemini/skills`, or `npx skills add ... -a gemini-cli` |

`npx skills add m4bwav/everlast-protocol -g -a codex -a github-copilot -a cursor -a gemini-cli -a opencode` is the community installer (vercel-labs/skills); it symlinks from `~/.agents/skills`. Verify the Claude Code link afterwards (open issue #851 sometimes skips it); the plugin install covers Claude Code anyway.

## The always-on pointer per tool

- Claude Code: `CLAUDE.md` imports `@AGENTS.md`; in `excluded` mode use `CLAUDE.local.md` (gitignored) or `@~/.claude/<project>.md`. Claude Code's `--worktree` copies gitignored files listed in `.worktreeinclude`.
- Copilot: `AGENTS.md` is read natively; `.github/copilot-instructions.md` may hold the same block.
- Codex: `AGENTS.md` (32 KiB cap) plus `~/.codex/AGENTS.md` (keep under 5 KiB).
- Gemini: `GEMINI.md`, or `.gemini/settings.json` with `{"context": {"fileName": "AGENTS.md"}}`.
- Cursor: `.cursor/rules` or `AGENTS.md`.

The block is `templates/AGENTS.md.snippet`, eight lines, unchanged across tools.

## Native memory: pointers only

Each product's memory (Claude auto-memory `MEMORY.md`, Codex `~/.codex/memories/` (generated after a chat idles; `memories.disable_on_external_context` keeps them out of shared contexts), Gemini `~/.gemini/GEMINI.md`) gets one line: where the vault is and that the record lives there. Copilot Memory is server-side with no file to write; rely on the AGENTS.md block. Claude Code `/import` (2.1.213+) and Codex `/import` can migrate settings one time; the vault does not need them.

## Hooks: what the harness gives

Claude Code hook stdin: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `stop_hook_active` (Stop). Env: `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_DATA` (survives updates). SessionStart stdout reaches the model; SessionEnd stdout does not and the event shares a 1.5 s budget by default, so the vault sync is a detached process (`CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` lengthens it since 2.1.271, a per-hook `timeout` does too). Do not point `autoMemoryDirectory` at the vault from a repository's settings: with `blockReadsOutsideWorkingDirectories` on, a repo-chosen memory directory is neither read nor written (2.1.273). Stop can block once with `{"decision": "block", "reason": ...}` and must check `stop_hook_active`. Copilot and Cursor hook payloads carry `transcript_path` too; Codex's `SessionEnd` has 1 s.

## A machine with no Python

Every command in this protocol can be done by hand: the layout is folders and markdown, the index is one line per file, the exclusion is one line in `.git/info/exclude`, the sync is `git add -A && git commit && git pull --rebase && git push` in the vault. The script is a convenience.
