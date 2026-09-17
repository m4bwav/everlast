---
title: Research summary behind the plugin design
kind: note
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [research]
---

# Research summary behind the plugin design

## Summary
Where the research behind the plugin lives and what it concluded, so a session does not redo it. The dated findings with sources are in the plugin's RESEARCH.md (R-20260913-1 to R-20260913-8); the doc-type verdicts are in `protocol/DOC-TYPES.md`.

## Details
- Three 2026 studies: always-on repository overviews do not raise success (ETH Zurich 2602.11988; 2605.10039; 2607.27250). On-demand distilled procedures do (BootstrapAgent 2605.15815; Codified Context 2602.20478).
- Vendor memories converged on user-level plus private project-level markdown; none portable (Claude, Codex, Copilot, Gemini; Cursor removed Memories).
- Cross-agent handoff designs converge on HANDOFF plus decisions plus tasks (ESAA 2606.23752).
- Packaging: Claude Code plugin from a repo; Cowork .plugin; ~/.agents/skills read by Codex, Copilot, OpenCode, Windsurf; npx skills add for the rest; claude plugin eval graders file_exists, regex, tool_used.
- Existing tools ranked: claude-mem 94k stars (transcript memory), compound-engineering 25k (docs/solutions), MemPalace, agentmemory. None splits private from repo-safe or offers an excluded mode.
- Privacy: vendors redact tokens only; sops plus age or gocryptfs for encryption later; git-crypt stagnant.
