# Doc types: what pays, what costs, and the shape of each

Part of the [Everlast Protocol](PROTOCOL.md). Which documents an agent should keep, with the 2026 evidence (sources in [../RESEARCH.md](../RESEARCH.md)), and the format `everlast.py` enforces. Descended from the ai-docs format reference (2026-09-06).

## What the evidence says

| Document | Verdict | Evidence |
|---|---|---|
| Always-on repository overview, directory layout, dependency list, architecture summary in `AGENTS.md`/`CLAUDE.md` | cost without benefit | ETH Zurich 2602.11988 (no success gain, +20% cost); 2605.10039 (1,650 sessions: file shape has no detectable effect on adherence); 2607.27250 (288 runs: context files never convert a near miss); Claude Code's own `/doctor` now trims these |
| Short rules with reasons, non-default conventions, pitfalls, in the always-on file | marginally useful when human-written and minimal | same studies; keep under 200 lines |
| Setup and bootstrap procedures, distilled | measurably helps: higher success, lower cost than rediscovery | BootstrapAgent 2605.15815; Codified Context 2602.20478 (283 sessions, on-demand retrieval) |
| Solutions: problem, dead ends, fix, verified command | helps; the most adopted concrete convention | compound-engineering `docs/solutions/` (25k stars); Codified Context; auto-memory explicitly skips these, which is why a file is needed |
| Decisions with reasons and rejected alternatives | helps; the core of every cross-agent handoff design | ESAA 2606.23752 (`decisions.md` projected from an event log); ADR practice |
| HANDOFF: state, in progress, decisions, dead ends, next single action | helps; the one file every handoff tool produces | ESAA; session-handoff skills on skills.sh; `npx continues` |
| Index of one line per entry, loaded first | helps when kept within budget and linted | agent-kept indexes decay without a lint (2606.19121); memory-doctor tools check size, provenance, staleness |
| Append-only log | cheap; history and blame the entries do not carry | ESAA event sourcing; evergreen's union-merge logs |
| User profile and environment facts, portable | helps; every vendor converged on a user-level store, none of them portable | Claude auto-memory, Codex `~/.codex/memory`, Copilot Memory, Gemini auto-memory (all 2026) |
| Codemap | helps only when loaded on demand for a locating question; harmful always-on | ETH Zurich; evergreen-map keeps it in the plugin store |
| Raw transcripts, tool logs | not this layer; a transcript store (claude-mem and similar) is complementary | claude-mem 94k stars keeps its own SQLite; everlast is the curated layer |

Provenance matters: artifact-anchored facts (tied to a file, commit, or command output) survive drift better than prose (EA-Graph 2608.04278). Every entry carries `date`, `verified`, and paths in backticks so the lint can check them.

## The layers, from always-on to on-demand

| Layer | File | Loaded | Holds | Budget |
|---|---|---|---|---|
| 0 | `AGENTS.md` (+ `CLAUDE.md` pointer, `.github/copilot-instructions.md` pointer) | every session | rules with reasons; the eight-line everlast block | lint warns at 400 lines |
| 0 | `CODEMAP.md` | when locating a system | systems, ownership, events, paths | 150 to 250 lines |
| 1 | `INDEX.md` | at task start | one line per entry: date, title, status, tags, and the `summary` clause (when to read it) | 120 lines; split by folder past that |
| 1 | `HANDOFF.md` | at session start (hook or resume) | current state, in progress, decisions, dead ends, next single action | 50 lines |
| 2 | `solutions/*.md` | when the task matches | Problem, Dead ends, Fix, Verified by, Applies when | 80 lines each |
| 2 | `decisions/*.md` | when touching that design | Context, Decision, Reasons, Rejected alternatives, Consequences | 80 lines |
| 2 | `plans/*.md` | when continuing that work | Goal, Status, Steps, Open questions, Next single action | 80 lines |
| 2 | `notes/*.md` | when the task matches | Summary, Details | 80 lines |
| 3 | `log.md` | almost never (history, blame) | `## [date] op \| title`, append-only | archive at 400 lines |
| user | `user/PROFILE.md` | once per new environment | how the user wants work done, each rule with its reason | 200 lines |
| user | `user/ENVIRONMENTS.md` | once per new environment, the machine's section | per machine and tool: paths, ports, what works, what breaks | 60 lines per section |

Git is the fourth layer: every entry is versioned, so `git log -- ai-docs/solutions/x.md` shows when a fix changed. Do not duplicate that history inside entries.

## Entry frontmatter

```yaml
---
title: CS0103 after renaming a UI method
kind: solution            # solution | decision | plan | note
status: active            # active | superseded | done | abandoned | promoted
date: 2026-09-06          # written
verified: 2026-09-06      # last time the fix or decision was confirmed to hold
tags: [unity, build]
summary: read when a Unity build fails with CS0103 after a rename   # optional, one line; the index shows it, so a reader knows when to open the entry
tier: private             # optional; private | user; absent means the project's repo-safe root
supersedes: solutions/2026-08-01-old.md   # optional; the old file gets status: superseded and superseded_by
---
```

`INDEX.md` is generated from this frontmatter (`everlast.py index`), so the index cannot drift from the files. Files without frontmatter already in the folder are adopted with kind inferred from the filename.

## Rules that keep it small

- Derivable gate: nothing a grep or one file read answers.
- One entry per problem or decision, updated in place; a contradiction supersedes, it never edits history away.
- Titles are what a future agent would search for (the error text, the feature name), never "session notes".
- Absolute dates. Paths to code and files outside the doc set in backticks (the lint checks they exist). Commands with the output that proved them.
- Linked, not just filed: a reference to another entry is a relative markdown link, and an entry that builds on, contradicts or supersedes another ends with a `Related:` line linking it (`Related: [the earlier fix](../solutions/2026-08-01-old.md)`). The generated `INDEX.md` is the hub, so every entry is reachable in two hops from the always-on pointer, and a graph-aware editor such as Obsidian shows the connections as backlinks. Give an entry a one-line `summary` (when to read it) so its index line is not a bare path, which agents ignore or load whole (the configuration-smells study calls this a blind reference). No link back to the index is needed; one `Up:` line at most, for GitHub readers. No wikilinks in a repo-safe root (they do not render on GitHub or in most tools); one distinct basename per entry (the date prefix does this) so a link is never ambiguous.
- No secrets, credentials, or people, in any repo-safe root (PRIVACY.md).
- Plain markdown; no `@imports`, no tool-specific front matter beyond the fields above.

## Prune pass (consolidation)

Run by `everlast-resume` when the lint reports more than five findings, or every 25 log entries, or on request: merge duplicates, mark contradicted entries superseded, convert relative dates to absolute, move `done`/`abandoned`/`superseded` entries older than 90 days to `archive/` (keep their index lines under an Archive heading), rebuild the index, log `prune`. Edit entries individually; never regenerate a file (wholesale rewrites erode detail; evergreen measured it).

## Promotion to a skill (automatic, conservative)

`everlast.py promote-scan` finds entries with three or more steps touched on three or more distinct dates, or three or more solutions under one tag. Gates: overlap (an existing skill covering the keywords is extended, never duplicated), listing budget (Claude Code caps the skill listing near 1% of context and evicts silently), then scope (repo-scoped unless evidence spans repos). One promotion per session; `trial: true` until its suite passes and it is used. Status `promoted` with `promoted_to:` keeps provenance.
