---
title: Everlast rollout
kind: plan
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [rollout]
---

# Everlast rollout

## Goal
Everlast installed and in daily use on every machine and agent product the user runs, with the vault current everywhere.

## Status
2026-09-13: plugin 0.1.0 built, self-test passing, vault created and seeded from the evergreen profile, repositories pushed, plugin installed in Claude Code on the home PC.

## Steps
- [x] Protocol, four skills, script, hooks, templates, evals scaffold
- [x] Vault with user tier; evergreen profile moved in; evergreen points there
- [x] GitHub repositories created and pushed
- [x] Installed in Claude Code (mark-local marketplace); old ai-docs skills parked
- [x] First eval runs logged (resume via plugin eval 4/4; privacy-1 via tester); remaining skill cases still to run
- [ ] Run the rest of the skill evals (setup, vault, capture trigger cases) with evergreen-test
- [ ] Install on the work laptop (Claude Code and Copilot) with `templates/INSTALL-PROMPT.txt`; register work repos in excluded mode
- [ ] Codex hooks adapter (does Codex's plugin hooks.json share Claude's schema?)
- [ ] Encryption at rest and an off-git backup route (deferred; see decisions/)
- [ ] Register the other repos in the Ai workspace

## Open questions
- Should the user-tier HANDOFF.md (what the user is doing across projects) be printed at session start too? Not yet; watch whether it gets written.

## Next single action
Install on the work laptop with `templates/INSTALL-PROMPT.txt` and register one work repo in excluded mode.
