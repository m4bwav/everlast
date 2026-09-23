# Research: everlast-resume

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: how agents retrieve and consolidate prior session knowledge from repo docs (progressive disclosure, index-first loading, memory consolidation passes). Tier `fast` (moderate until the 2026-09-23 check moved it). Last refresh 2026-09-23 (a correction, check before use and search, from the research behind plugin 0.4.0); next due per `evergreen.json`. The suite's shared findings live in `../everlast-capture/RESEARCH.md`; this file keeps what this skill's own claims depend on.

## Current understanding

- Index-first, entries on demand is the pattern every current source converges on: Claude Code loads MEMORY.md's first 200 lines and topic files on demand; Karpathy's llm-wiki queries through `index.md`; skill folders themselves are progressive disclosure (description, then body, then references). Loading more than the matching two or three entries is the measured cost without the benefit (everlast-capture:R-20260906-1).
- Doc sets that nobody re-verifies decay. The 391-session study (arXiv 2606.19121) shows agent-kept indexes drifting and the agent trusting its own earlier notes over the code, and 2026 studies measured how rarely agents check on their own: about one source check in five, superseded constraints acted on about three times in four, and 61 to 74 points gained when the check is forced (R-20260923-2). Hence Step 3: before acting on a stale entry, `recheck` it (read-only: stale or not, cited files changed in git, its proof), re-run the proof only when that is safe, and record `verify`, or `verify --failed` and supersede. GitHub Copilot Memory does the same with code citations.
- Consolidation is a defined operation now (Anthropic Dreams, the Managed Agents research preview: merge duplicates, replace contradicted entries with the latest value, absolute dates, rebuild the index, write a new store and leave the input for review; ACE-style delta updates with helpful/harmful tagging in the evergreen plugin's own research). Claude Code's "Auto Dream" never shipped (R-20260923-1). The prune pass copies that vocabulary and the "entry by entry, never regenerate" rule; its deterministic, reversible part (archive and relink) is `everlast.py maintain --apply`, and the judgment items stay with the agent.
- An index line matches only the words its author chose. When none matches, `everlast.py search` (BM25 over title, aliases, tags, summary and body) finds what the index words differently; lexical search held up against vector search in 2026 tests at this scale (R-20260923-2).
- Handoff files work when they are replaced, not appended, and end in one next action (the handoff skill family, everlast-capture:R-20260906-3). A SessionStart hook can inject HANDOFF.md so the resume skill does not read it twice.
- No benchmark measures doc reuse for coding agents in general (VibeMemBench, everlast-capture R-20260922-5, is the first neutral memory benchmark); this skill's evidence is the file reads in the trace, a `recheck` before the first edit, and the changed index and log after a prune. The plugin's `bench/` scores the retrieval step (index scan against search) as a regression floor.

## Open questions

- (resolved 2026-09-23) Claude Code's Auto Dream never shipped (R-20260923-1); there is nothing to defer to. `maintain` covers the deterministic part of the prune pass.
- What lint threshold (five findings, 25 log entries) actually triggers a useful prune rather than churn? Adjust from use.
- Whether a repeat-task probe (same failing command in two fresh sessions) can be run cheaply enough to become a standing eval.
- Does Step 3 hold up in use: how often does an agent run `recheck` on a `(recheck due)` entry without being told, and how often does a safe re-run of a stored proof turn up a stale fix? The `recheck` eval case measures the first; it needs a sandboxed (Linux or macOS) runner for `claude plugin eval`.

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `code.claude.com/docs/en/memory` (MEMORY.md load rules, AGENTS.md loading); `platform.claude.com managed agents dreams`; `docs.github.com copilot memory` (validation before use, expiry)
- `stale memory OR "superseded constraint" OR revocation agent benchmark <year>` (follow-ups to 2605.06527, 2608.25553, 2609.11060)
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

### R-20260923-2 · 2026-09-23 · Subject: check before use and search change how a task starts
- Summary: From the plugin's R-20260923-2 and R-20260923-3. GitHub Copilot Memory re-validates every memory against the current code before use and expires unused ones (pull-request merge rate 90% with memory, 83% without). Agents checked a memory's source about one episode in five and acted on a superseded constraint 74.7 to 77.3% of the time; forcing the check added 61 to 74 points (2608.25553). Probing the environment with read-only tools to re-check stored memories lifted a pass rate from 39% to 73% (2609.11060); the best system in STALE recognised 55.2% of invalid memories (2605.06527). On retrieval, grep beat vector search in 8 of 8 harness and model pairs when results came back inline (2605.15184), and semantic search helps most added on top of grep (Cursor, +12.5%). Applied: Step 2 runs `search` before concluding nothing was recorded; Step 3 checks a stale entry before acting on it, re-running its proof only when that is safe; Step 4 records with `verify`; Step 5 starts with `maintain`.
- Track: subject, testing
- Sources: https://docs.github.com/en/copilot/concepts/agents/copilot-memory, https://arxiv.org/abs/2608.25553, https://arxiv.org/abs/2609.11060, https://arxiv.org/abs/2605.06527, https://arxiv.org/abs/2605.15184, https://cursor.com/blog/semsearch
- Magnitude: 0.6 (the skill trusted a `verified:` date and told the agent to judge it; the evidence says the check has to be forced)
- Applied: C-20260923-1

### R-20260923-1 · 2026-09-23 · Subject: correction, Claude Code "Auto Dream" never shipped
- Summary: This file named "Anthropic Dreams / Auto Dream" as the source of the consolidation vocabulary and asked whether Auto Dream was GA. A `/memory` toggle appeared in Claude Code 2.1.81 (2026-03-20); `/dream` returned "Unknown skill: dream" (anthropics/claude-code#38461, 2026-03-24); "dream" is absent from the changelog through 2.1.280 and from the memory docs. Dreams is the Managed Agents research preview (beta header `dreaming-2026-04-21`, blog 2026-05-19) and works on Managed Agents memory stores. The vocabulary stands; the attribution and the open question were wrong.
- Track: subject
- Sources: https://github.com/anthropics/claude-code/issues/38461, https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md, https://code.claude.com/docs/en/memory, https://platform.claude.com/docs/en/managed-agents/dreams, https://claude.com/blog/new-in-claude-managed-agents
- Magnitude: 0.3
- Applied: C-20260923-1 (RESEARCH.md Current understanding, Open questions, Search plan)

### R-20260906-1 · 2026-09-06 · Initial research (all four tracks, shared with the suite)
- Summary: The pass that created the suite is logged in everlast-capture:R-20260906-1 to everlast-capture:R-20260906-4. Specific to this skill: index-first loading with a cap of two or three entries, the re-verify/supersede feedback loop as the answer to index sickness, the Dreams-shaped prune pass, HANDOFF injected by SessionStart so it is not read twice, and the absence of any benchmark for doc reuse (evidence is trace reads and changed files).
- Track: subject
- Sources: https://code.claude.com/docs/en/memory, https://platform.claude.com/docs/en/managed-agents/dreams, https://arxiv.org/abs/2606.19121, https://github.com/cablate/llm-atomic-wiki
- Magnitude: n/a (initial)
- Applied: C-20260906-1
