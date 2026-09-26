# Everlast Protocol

Nothing an AI session learned is lost when you change model, session, tool or vendor. Everlast keeps what agents learn in plain markdown you own, in two tiers, with a privacy split, installed as one plugin in every agent product you use.

- Project tier: an `ai-docs/` doc set per project (solutions with dead ends and the verified command, decisions with reasons and rejected alternatives, living plans, a 50-line HANDOFF, a generated INDEX, an append-only log), committed with the repository, or, when the repository must not carry it, kept in the vault and junctioned into the project as an excluded folder.
- User tier: a private vault repository holding your profile (how you want agents to work, each rule with its reason), your environments (machines, tools, paths, what works where), and lessons that span projects.
- Privacy split: anything naming a person, an opinion about people, a credential, an internal name or a customer goes to a private sidecar in the vault, never to a shared repository. The script scans and refuses; a human can override with a recorded decision.
- Check before use: every entry carries a `stale_after` date. The index, the session-start line and search flag what is due, and `recheck` and `verify` re-check a stored fix against the current code (cited files changed since it was verified, its proof re-run when that is safe) before an agent acts on it: GitHub Copilot Memory's idea, in plain files.
- Found even when worded differently: the index first, then `everlast.py search` (BM25 over titles, aliases, tags, summaries and bodies) when no index line matches; typed `Related:` links; deterministic upkeep (`maintain`); a reproducible benchmark in `bench/`.
- Cross-tool: a Claude Code plugin with hooks; a `.plugin` for Cowork; skills exported to `~/.agents/skills` for Copilot, Codex, OpenCode and Windsurf; one link more for Cursor and Gemini.
- Evergreen: every skill and the plugin itself re-research their subject on a schedule, capture learnings, and carry evals that pass on evidence (pointer mode to the installed evergreen plugin).

The spec is [protocol/PROTOCOL.md](protocol/PROTOCOL.md); which documents pay and why is [protocol/DOC-TYPES.md](protocol/DOC-TYPES.md); the privacy rules are [protocol/PRIVACY.md](protocol/PRIVACY.md); per-tool install is [protocol/PORTABILITY.md](protocol/PORTABILITY.md). The evidence behind the design is [RESEARCH.md](RESEARCH.md). This repository is its own everlast project: see [ai-docs/INDEX.md](ai-docs/INDEX.md).

## What you get

| Piece | What it does |
|---|---|
| `skills/everlast-setup` | Register a project in the vault in mode `repo` or `excluded`, scaffold its doc set and private sidecar, add the eight-line AGENTS.md pointer, lint. |
| `skills/everlast-capture` | End of task: harvest what was learned, route it (project, private sidecar, user tier, or elsewhere), classify for privacy, write with the script (a runnable proof in every solution, a recheck date, aliases, typed links), rewrite HANDOFF, lint. Promotes recurring procedures to skills, conservatively. |
| `skills/everlast-resume` | Start of task: read the user tier once per new environment, then the index, search when no line matches, open only matching entries, check a stale one before acting on it (recheck, re-run its proof when safe, verify or supersede), take HANDOFF's next action, run the upkeep pass when due. |
| `skills/everlast-vault` | The vault: init, remote (name a private repository or create one with gh), status, sync (commit, pull --rebase, push), privacy scan, new-machine install, export to other tools, pack for Cowork. |
| `scripts/everlast.py` | Everything deterministic, stdlib only: docs roots, index, lint (typed links, per-fact stamps), search, recheck and verify, maintain, privacy scan, project registry, junction and git exclusion, vault remote and sync, project docs sync (push when sure, pull request when not), export, pack, hooks. `scripts/test_everlast.py` is the self-test. |
| `hooks/hooks.json` | Claude Code: SessionStart prints one orientation line (ending `recheck due: N (titles) · maintain: M` when something is due; nothing is written) and the project HANDOFF; Stop nudges once per session when the tree changed and nothing was written; SessionEnd syncs the vault and the project's doc root in detached processes. |
| `bench/`, `scripts/bench_everlast.py` | A synthetic doc set (44 entries) and 41 typed queries; compares an index scan with `search` on Recall@1, Recall@3, MRR and two staleness measures. The self-test holds the floor. |
| `adapters/copilot/hooks.json` | The same SessionStart and SessionEnd for Copilot's `.github/hooks/`. |
| `templates/` | The AGENTS.md block, CLAUDE.md and copilot-instructions snippets, the one-paste install prompt. |
| `evals/` | Cases for `claude plugin eval` (file and regex graders); each skill also carries `evals/evals.json` for trigger tests. |

## Releases and contribution

Official releases are on the Releases page of https://github.com/m4bwav/everlast: each `vX.Y.Z` tag runs the self-test and publishes a zip of the tree, the `.plugin` for Cowork and the install prompt. The self-test also runs on Linux, macOS and Windows on every push. Updates flow in with `git pull`; the other way is opt-in: at install the agent asks once whether this install may open draft pull requests with the plugin's own learnings (four log file kinds, never your vault or project docs), and `everlast.py contribute yes|no` records or changes the answer. `no` means nothing ever leaves the machine.

Comparable tools worth knowing: mattpocock's `handoff` skill (the most installed, about 870K on skills.sh; it writes to the OS temp directory, so the handoff is gone after a reboot or on another machine; its "suggested skills for the next agent" line is a good idea), agentmemory's `handoff` skill (session resume keyed by working directory, an inline `<private>` marker everlast now honours too), `/memory-doctor` and AgentMemora (memory inspectors), and each vendor's own memory (Claude auto-memory and Claude Code Projects memory, Codex memories, Copilot Memory, Cursor Projects' shared files), which stay machine-, account- or product-local; everlast is the portable layer beside them. GitHub Copilot Memory is the model for check before use (each memory cites code, is re-validated against the current branch before use, and expires after 28 days unused). The closest designs on the same substrate are Letta Context Repositories (git-backed markdown with frontmatter descriptions, pinned and on-demand files, reflection and defragmentation subagents; tied to Letta's runtime, no privacy tiers) and ByteRover (a human-readable context tree of markdown with explicit relations and recency decay; its benchmark scores are self-reported).

## Install

Paste `templates/INSTALL-PROMPT.txt` into any agent. By hand, Claude Code:

```
git clone https://github.com/m4bwav/everlast <plugins root>/everlast-protocol
git clone <your private vault repository> <vault path from everlast.config.json>   # or: everlast.py vault init, then vault remote <url> | --create
claude plugin marketplace add <plugins root>/everlast-protocol     # or `marketplace update` when one already lists it
claude plugin install everlast-protocol@everlast --scope user
claude plugin list
```

Then in a project: "set up everlast for this repo" (two questions: commit the docs with the repo or keep them out of it; and, when committed, push them at session end, always open a pull request, or leave git to you). At the end of work: "write down what we learned". At the start: "pick up where we left off".

`python` is `python3` on macOS and Linux (the hook probes for whichever runs). Other tools: `python scripts/everlast.py export ~` (skills into `~/.agents/skills`), then the AGENTS.md block. Cowork: `python scripts/everlast.py pack`, upload the `.plugin`. Details: [protocol/PORTABILITY.md](protocol/PORTABILITY.md).

## Using the script

```
python scripts/everlast.py vault where | status | init | sync [--if-changed]
python scripts/everlast.py vault remote [<url> | --create [name]]   # back the vault up: a private repository you name, or one gh creates
python scripts/everlast.py project register <repo> --mode repo|excluded [--sync push|pr|off] [--no-link]
python scripts/everlast.py project status <repo> | list
python scripts/everlast.py project sync <repo> [--dry-run] [--pr]    # mode repo: commit the doc root only, push when sure, pull request when not
python scripts/everlast.py note <repo> --kind solution|decision|plan|note --title "..." --tags a,b [--aliases a,b] [--alias "exact error"] [--summary "when to read it"] [--stale-after YYYY-MM-DD|never] --body-file f [--private | --user]
python scripts/everlast.py handoff <repo> --body-file f
python scripts/everlast.py search "<query>" [<repo>] [--private] [--user] [--all] [-n 5] [--json]   # BM25: title and aliases x3, tags and summary x2, body x1
python scripts/everlast.py recheck <entry> [<repo>] [--private | --user]   # read-only: stale?, cited files changed in git since verified, the Verified-by text
python scripts/everlast.py verify <entry> [<repo>] [--failed "what broke"] [--note "..."]   # renew verified and stale_after, or record a failed recheck
python scripts/everlast.py maintain [<repo>] [--private | --user] [--apply]   # upkeep report; --apply archives old done/abandoned/superseded entries and relinks
python scripts/everlast.py lint <repo> [--all]      # budgets, headings, dead paths and links, stale, typed Related, stamps, duplicates, privacy, exclusion
python scripts/everlast.py scan <repo>              # privacy scan only
python scripts/everlast.py export <target> | pack
python scripts/everlast.py pull [--dry-run]         # update from the official repository; the SessionStart line says when this clone is behind
python scripts/everlast.py contribute [yes|no]      # asked once at install; publish is a no-op until yes
python scripts/everlast.py publish [--dry-run]      # consent-gated draft pull request with the plugin's own learnings
python scripts/test_everlast.py
python scripts/bench_everlast.py [--json] [--misses]   # the benchmark in bench/
```

Run it by absolute path; the shell's working directory is usually the project. Every command fails soft unless `--strict` precedes the subcommand, so hooks never break a session. `stale_after_days` in `everlast.config.json` sets the recheck window per kind (solution 90, decision 180, note 120, plan 30).

## Design notes

Six principles settle most edge cases: plain files the user owns (native memories hold pointers only); two tiers, one layout; private by default at the boundary; on demand, not always-on; evidence, not narration; checked before use. The evidence: three 2026 studies found always-on repository overviews cost tokens without raising success, while distilled setup procedures, solutions with dead ends, and decisions with reasons help when loaded on demand; every vendor's memory is now user-level and private but none survives a product switch, so the only portable layer is markdown in a repository you control. By 2026 Anthropic, OpenAI, Letta and GitHub had converged on the same substrate (plain-text files the agent edits, a consolidation pass, versioned scoped stores), and independent tests put memory layers level with tuned RAG, so what separates designs now is freshness: agents check a memory's source about one time in five and act on superseded constraints about three times in four unless something forces the check, and forcing it added 61 to 74 points. Sources and magnitudes are in [RESEARCH.md](RESEARCH.md).

- Check before use. `stale_after` (named after Google's Open Knowledge Format v0.2) is written by `note` as verified plus a window by kind; entries without it fall back to that window, so older doc sets join unedited. `recheck` is read-only and dates every cited file's changes with `git log --since`; the agent re-runs the Verified-by command only when it is read-only or safe, then records `verify` or `verify --failed`, and a fix that changed is superseded. Details: [protocol/DOC-TYPES.md](protocol/DOC-TYPES.md).
- Lexical search first. `search` is BM25 over fields, with aliases at the title's weight and light stemming, stdlib only. Embeddings are deferred by a recorded decision ([ai-docs/decisions/](ai-docs/INDEX.md)): in 2026 grep beat vector search when results came back inline, semantic search helps most as an addition to grep, and portability matters more at this scale. The benchmark below says when to revisit.
- Finer time and typed links. `Related:` lines take the labels `supersedes`, `superseded by`, `contradicts`, `builds on`, `see also` (the grammar the Evergreen Protocol shares); the lint checks targets, supersede status and open contradictions. A fact in a multi-fact entry can carry its own `(verified YYYY-MM-DD)` stamp.
- Upkeep that does not depend on the agent. `maintain` reports what is due and `--apply` does only the deterministic, reversible part (archive and relink); the SessionStart line counts it every session. Merging and resolving contradictions stay a judgment call.

Deferred by decision: encryption at rest and an off-git backup route (`ai-docs/decisions/`). The layout does not change when they arrive.

### Benchmark

`python scripts/bench_everlast.py` runs 41 queries against a synthetic 44-entry doc set (a fictional game project) as of 2026-09-23, comparing an index scan (the query words found on each `INDEX.md` line, ties in index order) with `everlast.py search`. First run, 2026-09-23 (TESTS.md T-20260923-1):

| method | Recall@1 | Recall@3 | MRR |
|---|---|---|---|
| index scan | 0.39 | 0.61 | 0.50 |
| `everlast.py search` | 0.90 | 0.93 | 0.92 |

By type (Recall@3, index / search): title 1.00 / 1.00, paraphrase 0.00 / 0.70, exact error 0.86 / 1.00, alias 0.00 / 1.00, tag 1.00 / 1.00, stale probes 1.00 / 1.00. Out-of-date entries in the top 3 that carry a flag: 29 of 34 for the index (it cannot show stale per-fact stamps), 33 of 33 for search; the current entry ranked above the out-of-date one in 0 of 6 stale probes for the index scan and 6 of 6 for search. Caveat: the fixture and the queries were written by the same team as the method, so this is a regression floor that catches a change for the worse, not evidence that lexical search beats RAG or embeddings, and the index baseline is a word-matching proxy that understates an agent, which also matches synonyms. An external score (LongMemEval-V2 or a STALE-style probe) is planned in [RESEARCH.md](RESEARCH.md) Open questions.

## Maintenance

This plugin is an evergreen unit (tier `fast`), in pointer mode to the installed evergreen plugin: [RESEARCH.md](RESEARCH.md), [CHANGELOG.md](CHANGELOG.md), [LEARNINGS.md](LEARNINGS.md), [TESTS.md](TESTS.md), `evergreen.json`, [MAINTENANCE.md](MAINTENANCE.md). Each skill carries the same set. Lineage: the three `ai-docs-*` skills (2026-09-06) were absorbed on 2026-09-13 with their histories.
