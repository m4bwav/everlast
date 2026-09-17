# Research: everlast-setup

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: repository layouts, instruction-file conventions and hooks for AI-agent documentation. Tier `moderate`. Last refresh 2026-09-06; next due 2026-10-06. The suite's shared findings (why layers, what auto-memory skips, the llm-wiki and compound-engineering shapes, benchmarks) live in `../everlast-capture/RESEARCH.md`; this file keeps only what this skill's own claims depend on.

## Current understanding

- Always-on instruction files should be short and rule-shaped; overviews in them are measured cost (everlast-capture:R-20260906-1). The setup block is therefore eight lines and the lint warns when AGENTS.md passes 400 lines.
- Claude Code reads CLAUDE.md (with `@imports`), `.claude/rules/*.md` (optional `paths:` frontmatter for path scoping), and its own auto-memory; it does not read AGENTS.md natively, so `CLAUDE.md` importing `AGENTS.md` remains the bridge. Copilot reads AGENTS.md and `.github/copilot-instructions.md`; Codex and Cursor read AGENTS.md. One block in AGENTS.md reaches all of them.
- Every's compound-engineering plugin already uses `docs/solutions/` and `docs/plans/` with a configurable root; a repo running it should keep that root rather than get a second folder.
- Claude Code hooks: SessionStart stdout is injected as context; Stop receives `stop_hook_active` and can block once via JSON `decision: block`; PreCompact and SessionEnd stdout do not reach the model. Copilot CLI hooks live in `.github/hooks/*.json` but fired per prompt in interactive mode (github/copilot-cli#991, 2026-01), so the nudge stays Claude Code only until that is fixed.
- Hooks edit the user's settings; installing them is a consent step, not a default (the evergreen protocol's "never install without a yes").

## Open questions

- Copilot CLI #991 status; if fixed, add the `sessionEnd` nudge.
- Does `.claude/rules/` with `paths:` make a better home for path-scoped ai-docs pointers in large monorepos than one AGENTS.md block? Try on the next monorepo.
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

### R-20260906-1 · 2026-09-06 · Initial research (all four tracks, shared with the suite)
- Summary: The four-track pass that created the suite is logged in everlast-capture:R-20260906-1 to everlast-capture:R-20260906-4. Specific to this skill: the eight-line AGENTS.md block (instructions are followed, overviews are not); root reuse when compound-engineering's `docs/solutions/` exists; the Claude Code hook semantics behind `everlast.py hook` (Stop blocks once with `stop_hook_active` guard, SessionStart stdout injected); the Copilot CLI hook caveat (#991); consent before installing hooks. Tooling track found no scaffold skill for this layout; ctxlint's path cross-check shaped the lint.
- Track: subject
- Sources: https://code.claude.com/docs/en/memory, https://code.claude.com/docs/en/hooks, https://github.com/github/copilot-cli/issues/991, https://github.com/EveryInc/compound-engineering-plugin, https://github.com/YawLabs/ctxlint
- Magnitude: n/a (initial)
- Applied: C-20260906-1
