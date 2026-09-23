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
| Check before use: re-run the proof, or re-read the cited source, before acting on a stored fix | helps; the largest single effect measured for agent memory in 2026 | GitHub Copilot Memory cites code, re-validates it before use and expires unused memories (pull-request merge rate 90% with memory, 83% without); agents check a memory's source about 1 time in 5 and act on superseded constraints about 75% of the time, forcing the check adds 61 to 74 points (2608.25553); re-checking stored memories with read-only tools lifted a pass rate from 39% to 73% (2609.11060) |
| Lexical search over the entries (BM25 with aliases) when no index line matches | helps at personal and project scale; embeddings deferred | grep beat vector search in 8 of 8 harness and model pairs when results came back inline (2605.15184); semantic search on top of grep added 12.5% at Cursor; `bench/` here: Recall@3 0.93 against 0.61 for an index scan |

Provenance matters: artifact-anchored facts (tied to a file, commit, or command output) survive drift better than prose (EA-Graph 2608.04278). Every entry carries `date`, `verified`, and paths in backticks so the lint can check them and `recheck` can date their changes.

## The layers, from always-on to on-demand

| Layer | File | Loaded | Holds | Budget |
|---|---|---|---|---|
| 0 | `AGENTS.md` (+ `CLAUDE.md` pointer, `.github/copilot-instructions.md` pointer) | every session | rules with reasons; the eight-line everlast block | lint warns at 400 lines |
| 0 | `CODEMAP.md` | when locating a system | systems, ownership, events, paths | 150 to 250 lines |
| 1 | `INDEX.md` | at task start | one line per entry: date, title, status (or `recheck due`), tags, and the `summary` clause (when to read it) | 120 lines; split by folder past that |
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
stale_after: 2026-12-05   # due for a recheck on or after this date; `never` for a timeless entry
tags: [unity, build]
aliases: ["error CS0103: The name 'ShowInventory' does not exist in the current context"]   # optional; other names, the exact error text first
summary: read when a Unity build fails with CS0103 after a rename   # optional, one line; the index shows it, so a reader knows when to open the entry
tier: private             # optional; private | user; absent means the project's repo-safe root
supersedes: solutions/2026-08-01-old.md   # optional; the old file gets status: superseded and superseded_by
---
```

`INDEX.md` is generated from this frontmatter (`everlast.py index`), so the index cannot drift from the files. Files without frontmatter already in the folder are adopted with kind inferred from the filename. `aliases` is a property Obsidian reads natively; a value holding `: ` or a comma is written in double quotes so the frontmatter stays valid YAML.

## Check before use

After GitHub Copilot Memory, whose memories cite their sources, are re-checked against the current code before use and expire when unused. `stale_after` takes its name and meaning from Google's Open Knowledge Format v0.2 (an ISO date; stale when today is on or after it); `verified` (a date) and `status` keep their everlast meanings.

- Windows. `note` writes `stale_after` as `verified` plus a window by kind: solution 90 days, decision 180, note 120, plan 30, set in `everlast.config.json` (`stale_after_days`). `--stale-after YYYY-MM-DD` overrides it; `--stale-after never` writes `stale_after: never`, the one non-date value, for a timeless entry (an OKF export would drop the field).
- Entries without the field. An entry with no `stale_after` is due once `verified` (or `date`) plus its kind's window has passed, so entries written before protocol 1.5 join the scheme unedited. A `verified` date later than `stale_after` (a hand edit) renews the entry by its window.
- Where it shows. The generated index puts `(recheck due)` in the status slot of an active entry that is due on the day the index is built; `everlast.py search` flags it in results; the SessionStart line counts it. Superseded, done and abandoned entries are history and never "due".
- The procedure, before acting on a due solution or decision. (1) `everlast.py recheck <entry>` (read-only): is it stale, which cited files changed in git since `verified` (`git log --since`), which are missing, and the text of its `## Verified by` section. (2) Re-run that command only when it is read-only or safe: a build, a test, a status or version query; never one that deploys, deletes, pushes, sends, pays or changes shared state. Otherwise re-read the cited files and ask the user. (3) Record it: `everlast.py verify <entry>` sets `verified` to today and `stale_after` to today plus the window, logs `verify` and rebuilds the index; `verify <entry> --failed "what broke"` adds `Recheck failed YYYY-MM-DD: what broke` to the Verified-by section, sets `stale_after` to today, and logs `verify-failed`. (4) When the fix changed, find the one that holds and write it with `note --supersedes <old>`; do not act on the old fix meanwhile.
- A runnable proof. A solution's `## Verified by` holds the command, copy-pasteable, and the output that proved it (`dotnet --list-sdks` printed `9.0.317`). Without one, a recheck can only re-read.
- Per-fact stamps. An entry holding several independent facts (a note of versions, a checklist) may end each fact that can go out of date with `(verified YYYY-MM-DD)`. The lint reports a stamp older than the entry's window, and search flags the entry `(stale facts)`, so one old fact does not hide behind a fresh `verified` date. Re-check that fact and update its stamp in place.

## Rules that keep it small

- Derivable gate: nothing a grep or one file read answers.
- One entry per problem or decision, updated in place; a contradiction supersedes, it never edits history away.
- Titles are what a future agent would search for (the error text, the feature name), never "session notes". Other names go in `aliases` (the exact error string, the tool's own words, a synonym): an index line shows only the title, and search reads the aliases at the title's weight.
- Absolute dates. Paths to code and files outside the doc set in backticks (the lint checks they exist in active entries, since history may name files that are gone; `recheck` dates their changes). Commands with the output that proved them.
- Linked, not just filed: a reference to another entry is a relative markdown link, and an entry that builds on, contradicts or supersedes another ends with a typed `Related:` line linking it (`Related: supersedes [the earlier fix](../solutions/2026-08-01-old.md); see also [the decision](../decisions/2026-07-15-json-saves.md)`; labels `supersedes`, `superseded by`, `contradicts`, `builds on`, `see also`; an unlabelled link counts as `see also`). `note --supersedes` writes the `supersedes` link itself when the body has no `Related:` line. The generated `INDEX.md` is the hub, so every entry is reachable in two hops from the always-on pointer, and a graph-aware editor such as Obsidian shows the connections as backlinks. Give an entry a one-line `summary` (when to read it) so its index line is not a bare path, which agents ignore or load whole (the configuration-smells study calls this a blind reference). No link back to the index is needed; one `Up:` line at most, for GitHub readers. No wikilinks in a repo-safe root (they do not render on GitHub or in most tools); one distinct basename per entry (the date prefix does this) so a link is never ambiguous.
- No secrets, credentials, or people, in any repo-safe root (PRIVACY.md).
- Plain markdown; no `@imports`, no tool-specific front matter beyond the fields above.

## Finding entries

Index first: one read, match the task against titles, tags and summaries, open two or three entries. When no line matches, `everlast.py search "<key terms>" [<repo>] [--private] [--user] [--all]` ranks every entry (archive included) by BM25 over title and aliases (x3), tags and summary (x2) and body (x1), with light stemming (s, es, ed, ing) and code-like tokens kept whole (`CS0103`, `CREATE_NO_WINDOW`); a superseded entry ranks below its successor and every hit carries its flags. Open the top two or three hits at most; no hit means nothing was recorded. The decision to stay lexical, and when to revisit it, is in the plugin's `ai-docs/decisions/`; `bench/` measures it.

## Prune pass (consolidation)

Run by `everlast-resume` when the lint reports more than five findings, or every 25 log entries, or on request. First `everlast.py maintain <repo>` (read-only report: entries due for a recheck, archive candidates, near-duplicate titles by difflib ratio 0.85 within a kind or 0.7 with the same tags, open contradictions, dead links and other lint findings), then `maintain --apply`, which does only the deterministic, reversible part: move `done`/`abandoned`/`superseded` entries older than 90 days to `archive/` in the same folder layout, rewrite every relative link to them (and inside them), keep their index lines under an Archive heading, rebuild the index, log `prune`. It never merges, deletes or edits content. An active entry more than one window past its `stale_after` with no successful `verify` is an archive candidate that `maintain` proposes and never moves: verify it, supersede it, or set its status to `done` or `abandoned`. Then the judgment items by hand: merge duplicates, resolve open contradictions (supersede one, or relabel the link `see also` once both are shown to hold), mark contradicted entries superseded, convert relative dates to absolute. Edit entries individually; never regenerate a file (wholesale rewrites erode detail; evergreen measured it).

## Promotion to a skill (automatic, conservative)

`everlast.py promote-scan` finds entries with three or more steps touched on three or more distinct dates, or three or more solutions under one tag. Gates: overlap (an existing skill covering the keywords is extended, never duplicated), listing budget (Claude Code caps the skill listing near 1% of context and evicts silently), then scope (repo-scoped unless evidence spans repos). One promotion per session; `trial: true` until its suite passes and it is used. Status `promoted` with `promoted_to:` keeps provenance.
