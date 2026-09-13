# Research: everlast-resume

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: how agents retrieve and consolidate prior session knowledge from repo docs (progressive disclosure, index-first loading, memory consolidation passes). Tier `moderate`. Last refresh 2026-09-06; next due 2026-10-06. The suite's shared findings live in `../everlast-capture/RESEARCH.md`; this file keeps what this skill's own claims depend on.

## Current understanding

- Index-first, entries on demand is the pattern every current source converges on: Claude Code loads MEMORY.md's first 200 lines and topic files on demand; Karpathy's llm-wiki queries through `index.md`; skill folders themselves are progressive disclosure (description, then body, then references). Loading more than the matching two or three entries is the measured cost without the benefit (everlast-capture:R-20260906-1).
- Doc sets that nobody re-verifies decay. The 391-session study (arXiv 2606.19121) shows agent-kept indexes drifting and the agent trusting its own earlier notes over the code. Hence: bump `verified:` when an entry works again, supersede when it fails, and treat a solution older than the last toolchain change as a lead.
- Consolidation is a defined operation now (Anthropic Dreams / Auto Dream: merge duplicates, drop contradicted facts, absolute dates, rebuild the index, touch only memory files; ACE-style delta updates with helpful/harmful tagging in the evergreen plugin's own research). The prune pass copies that vocabulary and the "entry by entry, never regenerate" rule.
- Handoff files work when they are replaced, not appended, and end in one next action (the handoff skill family, everlast-capture:R-20260906-3). A SessionStart hook can inject HANDOFF.md so the resume skill does not read it twice.
- No benchmark measures doc reuse for coding agents; this skill's evidence is the file reads in the trace and the changed index and log after a prune.

## Open questions

- Is Claude Code's Auto Dream GA, and could it be pointed at `ai-docs/` instead of a hand-run prune? If so, this skill should defer.
- What lint threshold (five findings, 25 log entries) actually triggers a useful prune rather than churn? Adjust from use.
- Whether a repeat-task probe (same failing command in two fresh sessions) can be run cheaply enough to become a standing eval.

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `code.claude.com/docs/en/memory` (auto dream, MEMORY.md load rules); `platform.claude.com managed agents dreams`
- `"progressive disclosure" agent context loading <year>`; `agent memory consolidation dedupe supersede <year>` (ACE, MemSkill follow-ups)

Tooling (skills, plugins, MCP servers, scripts, knowledge graphs built for this subject):

- `path:SKILL.md resume OR "pick up" OR consolidate OR prune memory` on GitHub sorted by recently updated; jl-cmd/claude-dream and grandamenium/dream-skill releases
- compound-engineering-plugin `ce-plan` recall behaviour (how it reads `docs/solutions`)

Practice (how others use AI agents on this goal, and everything in between):

- `site:arxiv.org agent notes OR memory "self-referential" OR drift longitudinal coding <year>` (follow-ups to 2606.19121)
- `"claude code" resume session handoff workflow <year>`; hn.algolia.com `agent memory decay` by date

Testing (how work on this subject is verified, and how skills for it are tuned):

- `"context file" ablation repeat task agent docs <year>`; `LongMemEval OR MemoryAgentBench code <year>` (still conversational only?)
- `path:SKILL.md memory consolidation test OR eval` on GitHub

Best sources (primary first): code.claude.com/docs, platform.claude.com (Dreams), arxiv.org 2606.19121 and citing papers, github.com/EveryInc/compound-engineering-plugin, the evergreen plugin's RESEARCH.md (memory consolidation literature). Noisy: vendor memory benchmarks read alone.

## Findings log

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20260906-1 · 2026-09-06 · Initial research (all four tracks, shared with the suite)
- Summary: The pass that created the suite is logged in everlast-capture:R-20260906-1 to everlast-capture:R-20260906-4. Specific to this skill: index-first loading with a cap of two or three entries, the re-verify/supersede feedback loop as the answer to index sickness, the Dreams-shaped prune pass, HANDOFF injected by SessionStart so it is not read twice, and the absence of any benchmark for doc reuse (evidence is trace reads and changed files).
- Track: subject
- Sources: https://code.claude.com/docs/en/memory, https://platform.claude.com/docs/en/managed-agents/dreams, https://arxiv.org/abs/2606.19121, https://github.com/cablate/llm-atomic-wiki
- Magnitude: n/a (initial)
- Applied: C-20260906-1
