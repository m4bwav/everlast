# Research: everlast-protocol

Current understanding, open questions, the four-track search plan, and dated findings for the plugin as a whole (the skills carry their own). Changes it caused are in [CHANGELOG.md](CHANGELOG.md); lessons in [LEARNINGS.md](LEARNINGS.md); state in `evergreen.json`; test runs in [TESTS.md](TESTS.md); the working document is [README.md](README.md) and [protocol/PROTOCOL.md](protocol/PROTOCOL.md).

## Current understanding (2026-09-13)

- Always-on repository overviews do not raise agent success and cost tokens (three independent 2026 studies); short human-written rules are at best marginal; distilled setup procedures, solutions with dead ends, and decisions with reasons help when retrieved on demand. Everlast therefore keeps an eight-line always-on block and an index.
- Every vendor's memory converged in 2026 on a user-level plus private project-level store in markdown outside the repo (Claude auto-memory, Codex `~/.codex/memory`, Copilot Memory server-side, Gemini auto-memory with a review inbox; Cursor removed Memories). None survives a product switch. The portable layer is markdown in a repository the user owns; native memories get pointers.
- Cross-agent handoff designs converge on HANDOFF plus decisions plus tasks (ESAA event-sourced projection), with provenance anchored to files and commits outlasting prose.
- Keeping docs out of a shared repo: `.git/info/exclude` works but Claude Code rewrites it on some versions (issue #84954), so the lint re-checks `git check-ignore`; a global `core.excludesFile` would exclude `ai-docs/` everywhere and is rejected; `CLAUDE.local.md` or a home-dir import carries the pointer in that mode.
- Vendors redact only narrow token patterns; people and politics need the user's own rules and a redact list. Encryption at rest, when wanted: sops with age (per-file, diffable) or gocryptfs (folder); git-crypt is stagnant.
- Packaging: a repo can be its own Claude Code plugin and marketplace; `hooks/hooks.json` is picked up automatically; SessionEnd shares a 1.5 s budget (sync must detach); `CLAUDE_PLUGIN_DATA` survives updates. `~/.agents/skills` is read natively by Codex, Copilot, OpenCode and Windsurf; Cursor and Gemini need a link; `npx skills add` is the community installer with an open Claude-symlink bug. Cowork takes a zipped `.plugin`. `claude plugin eval` (2.1.269) grades with `file_exists`, `regex`, `tool_used` and a no-plugin baseline.
- Existing tools by real use: claude-mem (94k stars, transcript memory, own SQLite), compound-engineering (25k, git-tracked `docs/solutions/`), MemPalace Cloud, agentmemory, Obsidian vaults. None does the two-tier privacy split or the excluded-folder mode; compound-engineering's solutions schema is adopted here.

## Open questions

- Does an on-demand index measurably beat auto-memory alone? No controlled study yet; watch cs.SE.
- Does Codex's plugin `hooks/hooks.json` share Claude Code's schema exactly? Untested; an adapter may be needed.
- Cross-product handoff quality has no benchmark; the plugin's own evals are the proxy.

## Search plan

- Subject: `arxiv.org cs.SE agent memory handoff 2026`; `code.claude.com/docs/en/memory`; Codex, Gemini, Copilot memory changelogs; "AGENTS.md study" follow-ups to 2602.11988.
- Tooling: GitHub `path:SKILL.md memory handoff`; skills.sh top installs for "memory", "handoff"; `registry.modelcontextprotocol.io/v0/servers?search=memory`; claude-mem, compound-engineering, agentmemory releases.
- Practice: hn.algolia.com "agent memory" by date; Simon Willison; Latent Space; vendor engineering blogs; GitHub issues on `.git/info/exclude`, `CLAUDE.local.md`, worktrees.
- Testing: `code.claude.com/docs/en/plugin-evals`; agentskills.io evaluating-skills; agent-memory-doctor and agent-memory-inspector; promptfoo assertions for file outputs.

## Findings (newest first)

### R-20260913-8 · 2026-09-13 · Testing: `claude plugin eval` ships with file, regex, tool and baseline graders
- track: testing · magnitude: 0.6 · applied: C-20260913-1 (evals/ layout)
- Claude Code 2.1.269: cases in `evals/<case>/prompt.md` plus `graders/*.md` (`regex`, `tool_used`, `tool_order`, `file_exists`, `llm`, `baseline`); three runs with and without the plugin; exit 1 below `--threshold`. `file_exists` plus `regex` over the written file is the exact check a capture plugin needs. Sources: https://code.claude.com/docs/en/plugin-evals, https://code.claude.com/docs/en/changelog

### R-20260913-7 · 2026-09-13 · Tooling: existing cross-session capture tools, ranked
- track: tooling · magnitude: 0.4 · applied: C-20260913-1 (DOC-TYPES table, README design notes)
- claude-mem 93.8k stars (hooks plus SQLite, transcript memory); compound-engineering 25.1k (`docs/solutions/`, `docs/plans/`, 14 hosts); MemPalace Cloud; rohitg00/agentmemory; obsidian-second-brain; agentcairn. All keep their own store; none writes into the vendors' memories; none splits private from repo-safe. Sources: https://github.com/thedotmack/claude-mem, https://github.com/EveryInc/compound-engineering-plugin, https://github.com/rohitg00/agentmemory

### R-20260913-6 · 2026-09-13 · Subject: Claude Code plugin manifest, hook events, env, budgets; Cowork `.plugin`; per-tool skill paths
- track: subject · magnitude: 0.5 · applied: C-20260913-1 (hooks.json, PORTABILITY.md)
- 35 hook events; SessionEnd shared 1.5 s budget; stdin carries `session_id`, `transcript_path`, `cwd`; env `CLAUDE_PLUGIN_ROOT`, `CLAUDE_PLUGIN_DATA`, `CLAUDE_PROJECT_DIR`; plugin hooks merge at the install scope (user by default); a repo can be installed as `claude plugin install owner/repo`; symlinked component paths may not escape the plugin dir (2.1.257). Cowork installs a zipped `<name>.plugin`. Codex reads `.agents/skills` and `~/.agents/skills`, not `.claude/skills`; Copilot reads `.github/skills`, `.claude/skills`, `.agents/skills`, `~/.copilot/skills`, `~/.agents/skills`; Cursor 2.4+ and Gemini read their own dirs; Copilot hooks now include `agentStop` and `sessionEnd`. Sources: https://code.claude.com/docs/en/plugins-reference, https://code.claude.com/docs/en/hooks, https://claude.com/docs/cowork/guide/plugins, https://learn.chatgpt.com/docs/build-skills, https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks, https://cursor.com/docs/hooks, https://geminicli.com/docs/hooks/writing-hooks/

### R-20260913-5 · 2026-09-13 · Tooling: `npx skills` is the de facto cross-tool installer; Claude symlink bug open
- track: tooling · magnitude: 0.4 · applied: C-20260913-1 (PORTABILITY.md, everlast-vault)
- vercel-labs/skills (31.5k stars) installs to `~/.agents/skills` and links per agent; issues #744/#851: `-g -a claude-code` sometimes skips the `~/.claude/skills` link. Alternatives: runkids/skillshare, chezmoi. Sources: https://github.com/vercel-labs/skills, https://github.com/vercel-labs/skills/issues/851

### R-20260913-4 · 2026-09-13 · Practice: keeping notes out of a shared repo; encryption at rest options
- track: practice · magnitude: 0.4 · applied: C-20260913-1 (excluded mode, lint check, PRIVACY.md "Later")
- `CLAUDE.local.md` is gitignored and not carried into worktrees (import `@~/.claude/<project>.md` instead; `.worktreeinclude`); `.git/info/exclude` is per clone but Claude Code writes its own `# claude-code-runtime` rules there and re-injects them (issue #84954). sops plus age for per-file encryption with diffs, gocryptfs for a transparent folder, git-crypt stagnant since 2025-09. Sources: https://code.claude.com/docs/en/memory, https://github.com/anthropics/claude-code/issues/84954, https://andyjakubowski.com/engineering/keeping-claude-md-out-of-shared-git-repos, https://www.pistack.xyz/posts/2026-04-23-mozilla-sops-vs-git-crypt-vs-age-self-hosted-secrets-encryption-git-guide-2026/

### R-20260913-3 · 2026-09-13 · Subject: vendor memory products converged on user-level plus private project-level markdown; none portable
- track: subject · magnitude: 0.6 · applied: C-20260913-1 (two tiers; pointers in native memory)
- Claude auto-memory (`MEMORY.md` index, first 200 lines loaded, `type:` per file, skips derivable facts, `autoMemoryDirectory`); Gemini auto-memory (global plus `.gemini/`, review inbox); Codex v0.128 `~/.codex/memory/` with a narrow secret redactor and an open exfiltration issue (#41711); Copilot Memory server-side with user and repo scopes; Cursor removed Memories. Bridges: `CLAUDE.md` importing `@AGENTS.md`, Copilot reading AGENTS.md/CLAUDE.md/GEMINI.md, one-time `/import`. Sources: https://code.claude.com/docs/en/memory, https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/auto-memory.md, https://github.blog/changelog/2026-05-26-copilot-memory-has-more-controls-for-deletion-scope-and-the-copilot-cli/, https://github.com/openai/codex/issues/41711

### R-20260913-2 · 2026-09-13 · Subject: on-demand distilled procedures help; cross-agent handoff designs converge on HANDOFF plus decisions plus tasks
- track: subject · magnitude: 0.5 · applied: C-20260913-1 (DOC-TYPES verdict table)
- BootstrapAgent (2605.15815): reused setup knowledge raises success and cuts cost. Codified Context (2602.20478, 283 sessions): on-demand cold specs work; drift is the main failure; update in the same session. ESAA-Conversational (2606.23752): append-only event log projected to `handoff.md`, `decisions.md`, `tasks.json` for Codex/Claude switches. EA-Graph (2608.04278): artifact-anchored memory beats prose under drift. Memory-lint tools (agent-memory-doctor, agent-memory-inspector) check size, provenance, staleness. Sources: https://arxiv.org/pdf/2605.15815, https://arxiv.org/html/2602.20478v1, https://arxiv.org/abs/2606.23752, https://arxiv.org/html/2608.04278v1, https://pypi.org/project/agent-memory-doctor/

### R-20260913-1 · 2026-09-13 · Subject: always-on context files do not move correctness (three studies)
- track: subject · magnitude: 0.7 · applied: C-20260913-1 (eight-line pointer; no overviews)
- ETH Zurich 2602.11988: no success gain, +20% cost, LLM-written files slightly worse. 2605.10039 (1,650 Claude Code sessions): size, position, architecture and contradictions have no detectable effect on adherence; adherence decays about 5.6% per generated function. 2607.27250 (Claude Code and Codex, 288 runs): context injection bounded to at most 10 to 15 points and never converts a near miss. Claude Code's `/doctor` now trims layouts and overviews and keeps pitfalls, rationale and non-default conventions. Sources: https://www.sri.inf.ethz.ch/publications/gloaguen2026agentsmd, https://arxiv.org/pdf/2605.10039, https://arxiv.org/abs/2607.27250, https://code.claude.com/docs/en/memory
