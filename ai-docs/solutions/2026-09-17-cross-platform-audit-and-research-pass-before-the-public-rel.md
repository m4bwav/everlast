---
title: Cross-platform audit and research pass before the public release
kind: solution
status: active
date: 2026-09-17
verified: 2026-09-17
tags: [portability, research, release]
agent: claude-code
---

# Cross-platform audit and research pass before the public release

## Problem
Before the 2026-09-17 public release, everlast's scripts had only ever run on the owner's Windows PC. A portability audit (subagent, checklist from the Evergreen Protocol's PORTABILITY.md) and a research pass on self-documenting plugins were run; neither was recorded anywhere an agent would find again.

## Fix
Audit findings applied in C-20260917-1: exclude pattern `/ai-docs` without trailing slash (a symlink is a file to git, so `/ai-docs/` never matched on macOS/Linux and excluded mode failed there); git identity fallback for the vault commit; UTF-8 on stdin/stdout/subprocess; junctions recognised as links on Python 3.12+ (`os.path.isjunction`); junction via PowerShell `New-Item` with `mklink` fallback and the error surfaced; exclude file via `git rev-parse --git-path`; `.sync.log` opened as bytes and ignored in the vault; deterministic slug suffix; `python` before the `py` launcher, each candidate probed with `-c "import sys"`; Copilot adapter points at the sh hook with a `<plugin root>` placeholder. Not applied: backslash normalisation in the dead-path lint (pattern not found; revisit), zip permission bits.
Research (R-20260917-1..3): inline `<private>` blocks stripped from repo-safe writes; `--agent`/`--model` provenance; Codex path `~/.codex/memories/`; `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`; do not set `autoMemoryDirectory` from repo settings.

## Verified by
`python scripts/test_everlast.py` all checks passed on Windows; `.github/workflows/tests.yml` runs it on ubuntu, macos and windows (3.9 and 3.13) on every push. No Mac or Linux box was reachable from the development machine, so CI is the second-platform proof.
