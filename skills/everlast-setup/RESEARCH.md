# Research: everlast-setup

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: repository layouts, instruction-file conventions and hooks for AI-agent documentation. Tier `moderate`. Last refresh 2026-10-23 (four-track pass; the installed block gained the code-wins rule); next due per `evergreen.json`. The suite's shared findings (why layers, what auto-memory skips, the llm-wiki and compound-engineering shapes, benchmarks) live in `../everlast-capture/RESEARCH.md`; this file keeps only what this skill's own claims depend on.

## Current understanding

- Always-on instruction files should be short and rule-shaped; overviews in them are measured cost (everlast-capture:R-20260906-1). The setup block is therefore eight lines and the lint warns when AGENTS.md passes 400 lines.
- Claude Code reads CLAUDE.md (with `@imports`), `.claude/rules/*.md` (optional `paths:` frontmatter for path scoping), and its own auto-memory. Since 2.1.277 it also reads AGENTS.md natively, but only when no CLAUDE.md or CLAUDE.local.md exists in the working directory or above; with one, only the CLAUDE.md files load, a pointer in prose loads nothing, and adding a CLAUDE.local.md switches the native reading off (R-20260923-1). So a CLAUDE.md (and, in excluded mode, a CLAUDE.local.md) whose first line is `@AGENTS.md` remains the bridge on every version. Copilot reads AGENTS.md and `.github/copilot-instructions.md`; Codex and Cursor read AGENTS.md. One block in AGENTS.md reaches all of them.
- Every's compound-engineering plugin already uses `docs/solutions/` and `docs/plans/` with a configurable root; a repo running it should keep that root rather than get a second folder.
- Claude Code hooks: SessionStart stdout is injected as context; Stop receives `stop_hook_active` and can block once via JSON `decision: block`; PreCompact and SessionEnd stdout do not reach the model. Copilot CLI hooks live in `.github/hooks/*.json` but fired per prompt in interactive mode (github/copilot-cli#991, 2026-01), so the nudge stays Claude Code only until that is fixed.
- Hooks edit the user's settings; installing them is a consent step, not a default (the evergreen protocol's "never install without a yes").

## Open questions

- (resolved 2026-09-23) Copilot CLI #991 was closed on 2026-04-08 (everlast-capture:R-20260922-2); `adapters/copilot/hooks.json` already carries `sessionStart` and `sessionEnd`, and the Stop-style nudge stays Claude Code only until someone asks for it there.
- Does `.claude/rules/` with `paths:` make a better home for path-scoped ai-docs pointers in large monorepos than one AGENTS.md block? Try on the next monorepo. Since Copilot CLI 1.0.89 also reads `.claude/rules` (R-20261011-1), one rules file would reach both tools.
- Whether Claude Code's plugin path-traversal checks (2.1.251+) affect junctioned skill folders (evergreen:open question); this suite is junctioned.

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `code.claude.com/docs/en/memory` (rules dir, imports, what loads when) and `code.claude.com/docs/en/hooks` (Stop, SessionStart, PreCompact)
- `agents.md` adopters and spec changes <year>; `docs.github.com copilot custom instructions AGENTS.md <year>`
- `monorepo AGENTS.md per directory scoping agents <year>`

Tooling (skills, plugins, MCP servers, scripts, knowledge graphs built for this subject):

- `path:SKILL.md "docs/solutions" OR "ai-docs" OR "agent docs" setup` on GitHub sorted by recently updated; compound-engineering-plugin releases (`docs_root`)
- `docs.github.com copilot cli hooks` and github/copilot-cli#991; `cclint` and `ctxlint` releases (init or scaffold commands)

Practice (how others use AI agents on this goal, and everything in between):

- `"how I structure" OR "my setup" docs folder "claude code" OR codex OR cursor <year>`; hn.algolia.com `CLAUDE.md size` by date
- `r/ClaudeAI CLAUDE.md too long OR bloated <year>`

Testing (how work on this subject is verified, and how skills for it are tuned):

- `cclint OR ctxlint context file lint rules <year>`; `"file_exists" grader claude plugin eval` (harness support for scaffold checks)
- `path:SKILL.md scaffold test OR eval` on GitHub

Best sources (primary first): code.claude.com/docs, docs.github.com (Copilot CLI hooks, custom instructions), agents.md, github.com/EveryInc/compound-engineering-plugin, github.com/YawLabs/ctxlint. Noisy: SEO "CLAUDE.md template" posts.

## Findings log

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20261023-1 · 2026-10-23 · Subject: the pointer block now says the code beats a stale instruction file; Copilot CLI applies path-specific instructions on read
- Summary: arXiv 2610.30571 (v1 2026-10-22) measured the failure this skill's always-on files can cause: with an instruction file that disagreed with the code, Claude Code and Codex CLI followed the file in 90.1% of choices, and one user-level sentence giving the code precedence moved 91.4% to the code with every conflict reported. The block Step 5 installs (templates/AGENTS.md.snippet) now carries that rule in its check-before-use bullet, same eight lines (plugin C-20261023-1); SKILL.md needs no edit because it installs the template as is. Other subject items since 10-11: Claude Code 2.1.309 loads only the start of a nested CLAUDE.md over the size limit (setup writes short files); 2.1.304 re-sends the skill list after compaction; Copilot CLI 1.0.100 (10-19) applies path-specific `.github/instructions` files automatically when the agent reads or edits a matching file; Codex 0.164, Gemini CLI 0.64/0.65, OpenCode 1.19.3/1.19.4, cursor.com/changelog and the agents.md repository (no commits since 10-11): nothing on instruction files. Tooling: ctxlint last released 0.28.0 on 10-09, compound-engineering v3.31.1/v3.32.0 nothing on `docs_root`: nothing new. Practice: secondary posts repeat the CLAUDE.md-wins-over-AGENTS.md trap the `@AGENTS.md` import already handles. Testing: nothing new.
- Track: subject, practice
- Sources: https://arxiv.org/abs/2610.30571, https://github.com/WenJing95/stale-docs-data (conditions/B_fix.md, numbers.md), https://github.com/anthropics/claude-code/releases/tag/v2.1.309, https://github.com/github/copilot-cli/releases/tag/v1.0.100, https://github.com/openai/codex/releases/tag/rust-v0.164.0, https://github.com/google-gemini/gemini-cli/releases, https://github.com/YawLabs/ctxlint/releases
- Magnitude: 0.45
- Applied: plugin C-20261023-1 (templates/AGENTS.md.snippet, the block Step 5 installs); SKILL.md unchanged

### R-20261011-1 · 2026-10-11 · Subject: the AGENTS.md setting renamed; Copilot CLI reads `.claude/rules`; other tools quiet
- Summary: Claude Code's built-in AGENTS.md plugin is now `cc-plugin-agents-md@builtin` (2.1.285; the old `agents-md@builtin` ID is still read), shown as "Project instructions" in `/config` with a new `managed-only` value; in Cowork a user-scope import that resolves outside the working directory, and a symlinked `~/.claude/CLAUDE.md`, are skipped. The `@AGENTS.md` bridge is unchanged, so Step 5 stands. Copilot CLI 1.0.89 reads `.claude/rules` files as custom instructions (1.0.92 fires one sessionEnd after Stop-hook continuations), which widens the open question on path-scoped pointers. Codex 0.162, Cursor (10-06), Gemini CLI 0.63 and the AGENTS.md spec: no memory or instruction changes. Tooling, practice, testing: nothing new for setup (see the plugin's R-20261011-1 to 3).
- Track: subject
- Sources: https://code.claude.com/docs/en/memory, https://raw.githubusercontent.com/github/copilot-cli/main/changelog.md, https://github.com/openai/codex/releases, https://cursor.com/changelog, https://github.com/google-gemini/gemini-cli/releases
- Magnitude: 0.25
- Applied: RESEARCH.md only (Current understanding, Open questions)

### R-20260923-1 · 2026-09-23 · Subject: Claude Code 2.1.277+ loads AGENTS.md only without a CLAUDE.md or CLAUDE.local.md; an `@AGENTS.md` import is the bridge
- Summary: The memory docs (read 2026-09-22 for everlast-capture:R-20260922-3): with an AGENTS.md and a CLAUDE.md or CLAUDE.local.md in the working directory or above, only the CLAUDE.md files load (default `claude-md-or-agents-md`); a CLAUDE.md that imports `@AGENTS.md` includes it; a pointer written in prose loads nothing; adding a CLAUDE.local.md switches AGENTS.md reading off. Step 5 said CLAUDE.md "should only import or point at" AGENTS.md, and excluded mode wrote a bare CLAUDE.local.md, which silently stops a repository's own AGENTS.md from loading. Both now start with the import line.
- Track: subject
- Sources: https://code.claude.com/docs/en/memory, https://github.com/anthropics/claude-code/releases/tag/v2.1.277
- Magnitude: 0.5 (a recommendation changed; the contradiction flagged 2026-09-22)
- Applied: C-20260923-1

### R-20260906-1 · 2026-09-06 · Initial research (all four tracks, shared with the suite)
- Summary: The four-track pass that created the suite is logged in everlast-capture:R-20260906-1 to everlast-capture:R-20260906-4. Specific to this skill: the eight-line AGENTS.md block (instructions are followed, overviews are not); root reuse when compound-engineering's `docs/solutions/` exists; the Claude Code hook semantics behind `everlast.py hook` (Stop blocks once with `stop_hook_active` guard, SessionStart stdout injected); the Copilot CLI hook caveat (#991); consent before installing hooks. Tooling track found no scaffold skill for this layout; ctxlint's path cross-check shaped the lint.
- Track: subject
- Sources: https://code.claude.com/docs/en/memory, https://code.claude.com/docs/en/hooks, https://github.com/github/copilot-cli/issues/991, https://github.com/EveryInc/compound-engineering-plugin, https://github.com/YawLabs/ctxlint
- Magnitude: n/a (initial)
- Applied: C-20260906-1
