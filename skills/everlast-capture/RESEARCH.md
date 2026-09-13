# Research: everlast-capture

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: how AI coding agents capture session knowledge in modular, on-demand repo documentation. Tier `fast`. Last refresh 2026-09-06; next due 2026-09-20. This is the suite's research hub: `everlast-setup` and `everlast-resume` keep only the findings specific to their own claims and point here for the rest.

## Current understanding

- Always-on context has a measured cost and a narrow benefit. ETH Zurich (arXiv 2602.11988, rev. 2026-06-23; SWE-bench, several agents) found repo context files did not raise success and cost over 20% more tokens, while their *instructions* were followed well and their *repository overviews* were not useful; a Codex study of 124 PRs (arXiv 2601.20404) found AGENTS.md cut wall-clock 28.6% and output tokens 16.6%. Read together: keep always-on text short and rule-shaped, put everything else behind an index. This is the reason for the layers.
- Claude Code's auto-memory (code.claude.com/docs/en/memory, 2026-06) stores four typed notes (user, feedback, project, reference), loads the first 200 lines of MEMORY.md, and explicitly skips anything derivable from the codebase and "debugging fixes". Debugging dead ends, verified commands and decision rationale are therefore nobody's job by default; that is the gap this skill fills. `.claude/rules/` with `paths:` frontmatter gives path-scoped always-on rules; `/doctor` proposes CLAUDE.md trims; `InstructionsLoaded` hook logs which files loaded.
- Agent-maintained doc sets decay. A 391-session action study (arXiv 2606.19121) documents "index sickness": agent-kept indexes drifted from the files and the model fell back to self-referential reasoning. Hence a generated index (from frontmatter, never hand-edited) and a lint that runs at resume time.
- Shape: Karpathy's llm-wiki gist (2026-04, 5k stars in two weeks) settled the pattern of an immutable source layer, an LLM-owned wiki with `index.md`, an append-only `log.md`, and three operations (ingest, query, lint); Every's compound-engineering plugin (24.9k stars, 33 skills, 14 hosts) writes learnings to `docs/solutions/` and plans to `docs/plans/` and has its planning skill read them back. The suite's folder names follow these so files stay portable.
- Handoff files are a commodity (mattpocock/skills `handoff`, softaworks session-handoff and clones): done, in progress, decisions with reasons, failed approaches, one next action, under 50 lines. Adopted as HANDOFF.md rather than re-invented.
- Consolidation vocabulary comes from Anthropic's Dreams (Managed Agents beta `dreaming-2026-04-21`) and Claude Code's Auto Dream: merge duplicates, drop contradicted facts, absolute dates, rebuild the index, write only memory files. Adopted as the prune pass.
- Prod mechanism: Claude Code has Stop (with `stop_hook_active`), SessionStart (stdout injected as context) and PreCompact hooks; Stop can block once with `{"decision":"block","reason":...}`. Copilot CLI hooks (`.github/hooks/*.json`) fired per prompt in interactive mode as of 2026-01 (github/copilot-cli#991). The instruction-file line plus the skill description are the portable prods; the hook is a Claude Code extra.
- No neutral benchmark measures whether repo docs reduce relearning for coding agents (LoCoMo, LongMemEval, MemoryAgentBench test conversational recall; vendor memory benchmarks are self-run). Evidence for this skill is self-made: the file exists with the required headings, the index line exists, and a repeat-task probe consults `solutions/` before re-experimenting. Linters for context files exist (cclint, YawLabs/ctxlint cross-references paths against the codebase) and shaped the dead-path check.
- Nothing in the MCP registry (`search=memory`, 30 servers, mostly hosted vector stores plus Letta) does this job; claude-mem (hook-driven transcript memory, large user base, stars unverified) is complementary, not a substitute: it stores observations, this stores curated, git-tracked, human-readable entries.

- Automatic skill creation (2026-09-06 pass): no shipped product creates skills unasked; Anthropic's internal `/skillify` leaked as interactive community ports with tiny adoption, Every's `/ce-compound` writes solutions not skills, the "self-improving skills" Stop-hook pattern updates existing skills only. The literature is clear on the costs: triggering accuracy falls past roughly 64 to 128 skills (Dynamic Agent Skills survey), model-generated skills show non-trivial negative transfer without a baseline (arXiv 2605.23899), skills evolved in one context lose 4.8 to 7.5 points when moved (arXiv 2606.23127), and SkillOps-style merge/repair/retire keeps a library healthy where plain growth does not. Claude Code itself caps the skill listing at about 1% of context (default `skillListingBudgetFraction` 0.01, 1536 chars per description, least-invoked skills evicted silently; community-documented from source, not in the changelog) and ships `/skill-doctor` (2.1.261) for unused-skill and cost reports. Vercel measured skills unused in 56% of relevant tasks while an 8KB always-on index hit 100%. Policy adopted: evidence-gated, overlap-gated, budget-gated, repo-scoped, trial-until-tested, retire-on-non-use, one per session, report not ask.

## Open questions

- Does the 1% listing budget apply identically to plugin and junctioned skills, and is `/skill-doctor` output readable from a file? (Affects `skill-budget` accuracy and the rollback signal.)

- skills.sh install counts for handoff, compound-engineering and documentation skills (site search failed 2026-09-06); use `skills.sh/api/skills` next time.
- Is Auto Dream GA in Claude Code, and does it touch anything outside the auto-memory directory? If it ever consolidates repo files, the prune pass should defer to it.
- Copilot CLI #991 status: if fixed, add a `sessionEnd` variant of the nudge hook to `everlast-setup`.
- Does a Stop-hook nudge measurably raise capture rate without annoying the user? Watch the use log and the user's reaction; retire the hook if `harmful` climbs.
- Karpathy gist URL and claude-mem star count were taken from secondary coverage; verify on the next refresh.

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `code.claude.com/docs/en/memory` (auto-memory types, what it skips, MEMORY.md limits, rules dir) and `code.claude.com/docs/en/hooks` (Stop, SessionStart, PreCompact fields)
- `site:arxiv.org AGENTS.md OR "context file" coding agent study <year>`; follow-ups to 2602.11988 and 2601.20404
- `"progressive disclosure" OR "just-in-time" context agent documentation <year>`; `agent decision record OR ADR agents <year>`
- `karpathy llm wiki <year>` and derivatives; `agents.md spec changes <year>`
- `skill library size accuracy OR "negative transfer" agent skills <year>` (2607.10113 follow-ups); `claude code skill listing budget skillListingBudgetFraction`; `claude code changelog skill-doctor`

Tooling (skills, plugins, MCP servers, scripts, knowledge graphs built for this subject):

- `path:SKILL.md handoff OR "session notes" OR "lessons learned" OR "docs/solutions"` on GitHub code search sorted by recently updated; `npx skills find handoff`, `npx skills find documentation`; skills.sh install counts via `skills.sh/api/skills`
- github.com/EveryInc/compound-engineering-plugin releases (`docs/solutions` shape); mattpocock/skills handoff; claude-mem releases
- `https://registry.modelcontextprotocol.io/v0/servers?search=memory` and `?search=knowledge`

Practice (how others use AI agents on this goal, and everything in between):

- `"how I use" OR "my workflow" "claude code" OR codex OR cursor docs OR "lessons learned" OR handoff <year>`; hn.algolia.com `agent memory file` by date
- `site:arxiv.org agent "documentation" OR "knowledge base" longitudinal OR "action research" coding <year>`
- `site:anthropic.com/engineering OR site:simonwillison.net OR site:latent.space memory OR "context engineering" <year>`

Testing (how work on this subject is verified, and how skills for it are tuned):

- `cclint OR ctxlint OR AgentLint releases <year>` (context-file linters); `"context file" ablation with without docs agent <year>`
- `path:SKILL.md documentation test OR eval` on GitHub; promptfoo `file-exists` or trajectory assertions for coding agents
- `LongMemEval OR MemoryAgentBench OR BEAM <year>` only to confirm none covers repo-doc reuse

Best sources (primary first): code.claude.com/docs (memory, hooks), arxiv.org (2602.11988, 2601.20404, 2606.19121 and citing papers), github.com repos named above, platform.claude.com (Dreams), docs.github.com (Copilot CLI hooks), promptfoo.dev/docs. Noisy: SEO "2026 guide to CLAUDE.md" pages, vendor memory benchmarks read alone, Medium (403), scraped skill mega-directories.

## Findings log

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20260906-7 · 2026-09-06 · Testing: trigger-eval method, cross-skill decoys, linters for shape but none for overlap
- Summary: agentskills.io and skill-creator converge on about 20 queries (8 to 10 triggers, 8 to 10 near-miss decoys), three runs each, pass at trigger rate 0.5, 60/40 split, five iterations, 1024-char description limit; the missing piece everywhere is using sibling skills' trigger prompts as decoys to catch competition. skill-lint, skillscheck and cclint check frontmatter and bloat; none detects two skills competing for one prompt. Applied: promote-scan's keyword overlap gate and the "sibling triggers as decoys" rule in Step 4b.
- Track: testing
- Sources: https://agentskills.io/skill-creation/optimizing-descriptions, https://github.com/anthropics/skills/tree/main/skills/skill-creator, https://github.com/himself65/skill-lint, https://github.com/Swival/skillscheck
- Magnitude: 0.4
- Applied: C-20260906-4

### R-20260906-6 · 2026-09-06 · Tooling and practice: nothing auto-creates skills unasked; the listing budget and /skill-doctor bound the cost
- Summary: Claude Code 2.1.261 added `/skill-doctor` (unused skills and context cost). The skill listing budget (`skillListingBudgetFraction` 0.01, `skillListingMaxDescChars` 1536, env `SLASH_COMMAND_TOOL_CHAR_BUDGET`; about 75 to 150 tokens per description; least-invoked evicted silently) is community-documented from source. Anthropic's internal `/skillify` leaked 2026-03; ports (0xMH/claude-skillify, 7 installs) are interactive with no duplicate check. superpowers `writing-skills` gives the create/don't-create rules (non-obvious, reusable, not regex-enforceable, not a project convention) and budgets (description under 500 chars, hot skills under 200 words). Developers Digest's `/reflect --auto` Stop hook updates existing skills with confidence tiers and never creates. Vercel (2026-01): skills unused 56% of the time, an 8KB AGENTS.md index 100%; broad knowledge always-on, skills for explicit workflows. Measured here: 58 skills visible, about 7.6k description tokens, over the 200K-window budget. Applied: budget gate, destination rule, one-per-session, report-not-ask.
- Track: tooling
- Sources: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md, https://claudefa.st/blog/guide/mechanics/skill-listing-budget, https://github.com/0xMH/claude-skillify, https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md, https://www.developersdigest.tech/blog/self-improving-skills-claude-code, https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals
- Magnitude: 0.7
- Applied: C-20260906-4

### R-20260906-5 · 2026-09-06 · Subject: skill-library research sets the gates (size cliff, negative transfer, trial-then-promote, merge/retire)
- Summary: Dynamic Agent Skills survey (arXiv 2607.10113): accuracy declines sharply past about 64 to 128 skills; realistic distractors erase curated-skill gains; PSN reverts a tentative skill when success on three recent tasks drops over 20%; most systems admit candidates as trial skills. Model-generated skills show non-trivial negative transfer, extractor quality independent of scale (arXiv 2605.23899). Procedural-memory refinement gains 3.7 to 6.7 points in-context but loses 4.8 to 7.5 across contexts (arXiv 2606.23127): repo-scope by default. SkillOps (arXiv 2605.13716) holds about 80% at 2000 skills with merge, repair, retire and validator operators; microsoft/SkillOpt gates every edit on held-out selection. Applied: rule of three on distinct dates, trial flag, baseline requirement, repo scope, retire on non-use.
- Track: subject
- Sources: https://arxiv.org/html/2607.10113v1, https://arxiv.org/pdf/2605.23899, https://arxiv.org/abs/2606.23127, https://arxiv.org/html/2605.13716v1, https://github.com/microsoft/SkillOpt
- Magnitude: 0.6
- Applied: C-20260906-4

### R-20260906-4 · 2026-09-06 · Testing: no benchmark for doc-driven relearning; context-file linters exist
- Summary: LoCoMo, LongMemEval, BEAM and MemoryAgentBench measure conversational recall, not repo-doc reuse; mem0 and cognee pages are self-benchmarks. Promptfoo's coding-agent guide reads files after the run but has no file-exists assertion. cclint (CLAUDE.md, skills, hooks) and YawLabs/ctxlint (cross-references context files against the codebase to catch stale paths) are the closest checkers. Applied as the suite's own evals (file with headings, index line, repeat-task probe) and as the dead-path and budget checks in `everlast.py lint`.
- Track: testing
- Sources: https://www.promptfoo.dev/docs/guides/evaluate-coding-agents/, https://mem0.ai/blog/ai-memory-benchmarks-in-2026, https://github.com/felixgeelhaar/cclint, https://github.com/YawLabs/ctxlint
- Magnitude: n/a (initial)
- Applied: C-20260906-1

### R-20260906-3 · 2026-09-06 · Tooling: compound-engineering, handoff skills, Dreams, claude-mem, hooks; nothing in the MCP registry
- Summary: EveryInc/compound-engineering-plugin (24.9k stars) captures learnings to `docs/solutions/` and plans to `docs/plans/`, root configurable, and recalls them in its plan skill; the closest maintained implementation, so folder names were aligned and setup points at it when present. Handoff skills (mattpocock/skills, softaworks/agent-toolkit, several clones) share one shape (done, in progress, decisions and reasons, failed approaches, next single action, under 50 lines), adopted as HANDOFF.md. Anthropic Dreams (`dreaming-2026-04-21`) and Claude Code Auto Dream define consolidation (merge, supersede, absolute dates, rebuild index); adopted as the prune pass. claude-mem is hook-driven transcript memory (stars from secondary sources), complementary. Claude Code hooks: Stop with `stop_hook_active`, SessionStart stdout injected, PreCompact cannot inject; Copilot CLI hooks fired per prompt (github/copilot-cli#991, 2026-01). MCP registry `search=memory`: 30 servers, hosted vector stores and Letta, none a git-tracked doc set.
- Track: tooling
- Sources: https://github.com/EveryInc/compound-engineering-plugin, https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md, https://github.com/softaworks/agent-toolkit/blob/main/skills/session-handoff/SKILL.md, https://platform.claude.com/docs/en/managed-agents/dreams, https://github.com/jl-cmd/claude-dream, https://www.augmentcode.com/learn/claude-mem-65k-stars, https://code.claude.com/docs/en/hooks, https://github.com/github/copilot-cli/issues/991, https://registry.modelcontextprotocol.io/v0/servers?search=memory
- Magnitude: n/a (initial)
- Applied: C-20260906-1

### R-20260906-2 · 2026-09-06 · Practice: agent-kept indexes decay (391-session study); ADR-for-agents conventions
- Summary: Zhang et al. (arXiv 2606.19121) followed a month-long Copilot project across 391 sessions: agent-maintained indexes drifted from the files ("index sickness") and the model retreated to self-referential reasoning once the symbolic layer grew past a threshold; they catalogue the failed strategies. Applied as: the index is generated from frontmatter, never hand-edited, and `everlast-resume` lints and prunes. me2resh/agent-decision-record and Codex-CLI ADR write-ups (2026-04-28) give decisions a stable format (status, context, decision, consequences, supersedes) and have agents check `docs/adrs/` before architecture choices; applied as the decisions layer headings.
- Track: practice
- Sources: https://arxiv.org/abs/2606.19121, https://github.com/me2resh/agent-decision-record, https://codex.danielvaughan.com/2026/04/28/codex-cli-architecture-decision-records-adr-automated-governance/
- Magnitude: n/a (initial)
- Applied: C-20260906-1

### R-20260906-1 · 2026-09-06 · Subject: context files cost more than they help unless rule-shaped; auto-memory skips fixes and rationale; llm-wiki shape
- Summary: ETH Zurich (arXiv 2602.11988, rev. 2026-06-23) found developer-committed context files did not improve SWE-bench success and cost over 20% more, with instructions followed and overviews ignored; the Codex PR study (arXiv 2601.20404) found the opposite on cost when the file is short and rule-shaped. Claude Code memory docs define the four auto-memory types, the 200-line MEMORY.md load, `.claude/rules/` path scoping, and state that auto-memory skips derivable facts and debugging fixes. Karpathy's llm-wiki (2026-04) fixed the index + append-only log + lint shape, with llm-atomic-wiki and a v2 gist adding atom layers and contradiction detection. Applied as the derivable gate, the routing table, the layer budgets, the generated INDEX.md and log.md.
- Track: subject
- Sources: https://arxiv.org/abs/2602.11988, https://arxiv.org/html/2601.20404v2, https://code.claude.com/docs/en/memory, https://github.com/cablate/llm-atomic-wiki, https://gist.github.com/rohitg00/2067ab416f7bbe447c1977edaaa681e2
- Magnitude: n/a (initial; the largest single finding would score 0.8 against a naive "put it all in CLAUDE.md" design)
- Applied: C-20260906-1
