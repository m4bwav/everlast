# Changelog: everlast-protocol

Every change to [README.md](README.md), [protocol/](protocol/PROTOCOL.md), `scripts/`, `hooks/` and the plugin-level companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: [MAINTENANCE.md](MAINTENANCE.md). Each skill keeps its own changelog.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20260926-1 · 2026-09-26 · Research refresh: vendor project memory, handoff comparables, how to tune the failing triggers
- because: R-20260926-1, R-20260926-2
- files: RESEARCH.md (Current understanding: vendor memory list, packaging and plugin eval; Open questions; R-20260926-1, R-20260926-2), README.md (comparable tools), TESTS.md (harness notes)
- Cursor and Claude Code both regained a project-scoped memory store, still product-local; the most-installed handoff skill writes to a temp directory; the recheck undertrigger must be tuned with plugin eval, not skill-creator's trigger rate, and plugin eval now needs git 2.31.

### C-20260923-13 · 2026-09-23 · Plugin 0.4.1: the lint's link check skips inline code and fenced blocks
- because: L-006 (the first 0.4.0 lint of a real user tier reported the format example `[title](path)` inside inline code as a dead link)
- files: scripts/everlast.py (`CODE_RE`, `without_code`, the dead-link loop in `lint`), scripts/test_everlast.py (typed Related lint block), .claude-plugin/plugin.json (0.4.1)
- Links are found in the body with fenced blocks and inline code spans blanked, so a documented example is not a finding and does not inflate the SessionStart `maintain` count. Backticked paths are still checked by the separate path check, which is what backticks are for.

### C-20260923-12 · 2026-09-23 · `note` keeps a body's own H1; the lint checks backticked paths in active entries only
- because: T-20260923-3; L-005
- files: scripts/everlast.py (`cmd_note`: no second `# title` when the body starts with an H1; `lint_root`: the dead-path check skips superseded, done and abandoned entries), scripts/test_everlast.py (two checks)
- History may name files that are gone; flagging them pushed an agent to reword a correct path in a new entry. Links between documents are still checked in every entry.

### C-20260923-11 · 2026-09-23 · Eval cases for check before use (`recheck`) and search; resume trigger cases for the new phrasing
- because: the owner's request (prove the agent checks a stale fix before editing); R-20260923-2; T-20260923-2
- files: evals/recheck/ (case.yaml, prompt.md, scaffold.sh, graders: ran-recheck, check-before-edit, no-stale-fix, recorded, not-blind, skill-fired), evals/search/ (case.yaml, prompt.md, scaffold.sh, graders: ran-search, answer, skill-fired), skills/everlast-resume/evals/evals.json (trigger-3, trigger-4, decoy-3, action-2)
- The recheck case seeds a stale solution whose cited file moved on after it was verified; graders pass only on a `recheck` or Verified-by call in the trace before the first `Edit`. Both new cases need Bash, which `claude plugin eval` grants only under an OS sandbox (none on native Windows), so their first proof is recorded as described in T-20260923-2.

### C-20260923-10 · 2026-09-23 · Plugin 0.4.0, protocol 1.5: README, research and version
- because: the owner's request ("update and improve everlast with everything learned"); R-20260923-1 to R-20260923-8; T-20260923-1
- files: README (intro bullets, What you get, Releases and contribution: comparable tools, Using the script, Design notes, new Benchmark subsection), RESEARCH.md (Current understanding edited in place, Open questions: external score plan, R-20260923-1..8), protocol/PROTOCOL.md header (1.5, 2026-09-23), .claude-plugin/plugin.json (0.4.0 and description; `VERSION` in scripts/everlast.py reads it)
- R-20260917-1 keeps its SkillsBench v1 numbers as logged; R-20260923-6 carries v4's.

### C-20260923-9 · 2026-09-23 · CLAUDE.md and excluded mode's CLAUDE.local.md import AGENTS.md with an `@AGENTS.md` line
- because: everlast-capture R-20260922-3 (Claude Code 2.1.277+ reads AGENTS.md itself only when no CLAUDE.md or CLAUDE.local.md exists; a prose pointer loads nothing); the contradiction flagged on everlast-setup 2026-09-22
- files: templates/CLAUDE.md.snippet (why the import stays first; excluded-mode note), protocol/PORTABILITY.md (The always-on pointer per tool), skills/everlast-setup (SKILL.md Step 5, its C-20260923-1)
- No script writes these files; the skill does, following Step 5.

### C-20260923-8 · 2026-09-23 · A benchmark: `bench/` and `scripts/bench_everlast.py`, held as a floor by the self-test
- because: the owner's request (no benchmark score); R-20260923-3; T-20260923-1
- files: bench/README.md, bench/queries.json (41 typed queries), bench/fixture/ai-docs/ (44 synthetic entries, their INDEX.md, a HANDOFF.md and log.md), scripts/bench_everlast.py, scripts/test_everlast.py (`BENCH_FLOOR_R3` 0.90)
- Compares an index scan with `search` on Recall@1, Recall@3, MRR by query type and two staleness measures; the query types are checked before scoring. Written by the same team as the method: a regression floor, not evidence against RAG.

### C-20260923-7 · 2026-09-23 · SessionStart line ends with `recheck due: N (titles) · maintain: M` when something is due
- because: the owner's request (upkeep that does not depend on the agent); R-20260923-2, R-20260923-8
- files: scripts/everlast.py (`cmd_hook_run` SessionStart), adapters/copilot/hooks.json unchanged (it runs the same script)
- Read-only (no git call, nothing written), at most three titles, silent when nothing is due. No new hook event. About 0.2 s on the 44-entry fixture and 1.3 s on 528 near-duplicate entries (T-20260923-1).

### C-20260923-6 · 2026-09-23 · `everlast.py maintain`: an upkeep report; `--apply` archives and relinks, nothing else
- because: the owner's request (upkeep depends on the agent); R-20260923-8
- files: scripts/everlast.py (`maintenance`, `duplicate_pairs`, `archive_entries`, `rewrite_links`, `rewrite_frontmatter_paths`, `cmd_maintain`; `entries(root, archive=True)`; the index lists archive/ entries under an Archive heading; lint findings carry a category), protocol/PROTOCOL.md §3 (Upkeep), protocol/DOC-TYPES.md (Prune pass), skills/everlast-resume (Step 5)
- The report: entries due for a recheck, done/abandoned/superseded entries older than 90 days, active entries more than a window past `stale_after` (proposed only), near-duplicate titles (difflib 0.85 within a kind, or 0.7 with the same tags), open contradictions, dead links and other lint findings. `--apply` moves the first group to `archive/` in the same layout, rewrites every relative link to and inside them (and frontmatter `supersedes` paths), rebuilds the index, logs `prune`; it never merges, deletes or edits content.

### C-20260923-5 · 2026-09-23 · Typed `Related:` links and per-fact stamps, checked by the lint
- because: the owner's request (coarse tracking of time and links); R-20260923-7; the Evergreen Protocol's parallel update (same grammar)
- files: scripts/everlast.py (`related_links`, `LINK_RE`, `split_outside_links`; lint: every relative link resolves, a `supersedes` target is superseded, unknown labels, open `contradicts` pairs, frontmatter `supersedes` targets, `(verified YYYY-MM-DD)` stamps older than the window; `note --supersedes` writes `Related: supersedes [title](path)` when the body has no Related line; search flags `(stale facts)`), protocol/PROTOCOL.md §8, protocol/DOC-TYPES.md (rules, Check before use), templates/AGENTS.md.snippet
- Labels: `supersedes`, `superseded by`, `contradicts`, `builds on`, `see also`; an unlabelled link counts as `see also`, so every existing Related line stays valid.

### C-20260923-4 · 2026-09-23 · `everlast.py search`: BM25 over title, aliases, tags, summary and body; `aliases` frontmatter
- because: the owner's request (no meaning-based search); R-20260923-3; decision "Search is lexical (BM25 plus aliases) first" in ai-docs/decisions
- files: scripts/everlast.py (`tokenize`, `stem`, `bm25_corpus`, `bm25_scores`, `search_entries`, `search_roots`, `cmd_search`; `note --aliases a,b` and `--alias "text"`; the frontmatter parser reads quoted values and the writer quotes what YAML would misread, `set_fields` edits keys in place), protocol/PROTOCOL.md §8 and principle 4, protocol/DOC-TYPES.md (Finding entries, frontmatter, rules), skills/everlast-resume (Step 2), skills/everlast-capture (Step 5)
- Weights title and aliases x3, tags and summary x2, body x1; light stemming; identifiers and dotted names count whole and in parts; a superseded entry x0.5, done or abandoned x0.8, recheck due x0.9, so the current entry ranks first. Scope: the project root, `--private`, `--user`, or `--all` registered roots.

### C-20260923-3 · 2026-09-23 · Protocol 1.5: check before use (`stale_after`, `recheck`, `verify`, the index flag)
- because: the owner's request (the check-before-use info for everlast solutions); R-20260923-2, R-20260923-4
- files: scripts/everlast.py (`stale_due`, `is_stale`, `stale_stamps`, `find_entry`, `cited_paths`, `git_changes_since`, `cmd_recheck`, `cmd_verify`, `add_to_section`; `note --stale-after DATE|never`; `index_text` puts `(recheck due)` in the status slot; INDEX header; `EVERLAST_TODAY` for tests; lint staleness by kind, `--stale-days` now an explicit override), everlast.config.json (`stale_after_days`), protocol/PROTOCOL.md (principle 6, §3 Start and During), protocol/DOC-TYPES.md (evidence rows, frontmatter, Check before use), protocol/PORTABILITY.md (the check by hand), templates/AGENTS.md.snippet, AGENTS.md (the everlast block), skills/everlast-resume (Step 3), skills/everlast-capture (Step 5)
- Windows by kind: solution 90 days, decision 180, note 120, plan 30. An entry without `stale_after` falls back to its window, so existing doc sets join unedited; `--stale-after never` writes the literal `never` (omitting the field would make the entry fall back to the window). `recheck` is read-only; `verify` renews, `verify --failed` records what broke and marks the entry due now. Behaviour change for existing users: `lint` now reports entries past their kind's window (a plan after 30 days) instead of after a flat 120 days.

### C-20260923-2 · 2026-09-23 · A private machine path removed from the install prompt
- because: the repository rule (no machine paths beyond everlast.config.json); found in this release's privacy scrub
- files: templates/INSTALL-PROMPT.txt (step 1)
- The example marketplace folder named the owner's own directory; it now reads "an existing local marketplace folder if this machine has one". The git history still carries the old string.

### C-20260923-1 · 2026-09-23 · Vault paths expand environment variables, so the shipped Windows default works
- because: L-004
- files: scripts/everlast.py (`vault_path`: `os.path.expandvars` for `EVERLAST_VAULT` and the config value), scripts/test_everlast.py
- The public `everlast.config.json` names `%USERPROFILE%\everlast-vault` on Windows, which was never expanded, so the vault resolved to a literal `%USERPROFILE%` folder under the current directory.

### C-20260922-1 · 2026-09-22 · Machine and project labels generalised in the published files
- because: the repository rule (no personal data, machine names only in a fork's state files); found while refreshing everlast-capture
- files: TESTS.md (T-20260913-1, T-20260913-2 env), ai-docs/plans/2026-09-13-everlast-rollout.md (log line), skills/everlast-capture/LEARNINGS.md (a Scope and an Evidence line), skills/everlast-capture/TESTS.md, skills/everlast-resume/TESTS.md, skills/everlast-setup/TESTS.md (T- env labels), skills/everlast-setup/evergreen.json (tests env)
- The development machine's nickname became `owner-pc` (the label the public state files already use) and a private project and skill name became generic descriptions. The git history still carries the old strings.

### C-20260920-1 · 2026-09-20 · No console windows from the detached SessionEnd sync on Windows (fork 0.3.4; official 0.4.0)
- because: L-003 (the owner saw a burst of console windows open and close when closing VS Code; each was a `git.exe` spawned by the detached vault or project sync)
- files: scripts/everlast.py (`NO_WINDOW` constant beside `run()`; `run()`, `status_lines()` and both `--detach` Popen calls pass it)
- `CREATE_NO_WINDOW` (0x08000000) on every subprocess call, the same flag evergreen_sync.py already uses. Made in the owner's fork first and brought here unchanged in code. General fix, worth a pull request to the official repository.

### C-20260918-5 · 2026-09-18 · `project register --mode excluded` merges an existing `ai-docs/` into the scaffolded store instead of nesting it (fork 0.3.3; official 0.4.0)
- because: L-20260918-1 in everlast-setup (registering a project whose `ai-docs/` already had `plans/` and `decisions/` moved them to `<store>/plans/plans/` because the store had been scaffolded first)
- files: scripts/everlast.py (`cmd_project_register`, the move loop)
- When both the source and the store hold a folder of the same name, the folder's files are moved into the store's folder and the empty source folder removed; files and folders with no counterpart move as before. General fix, worth a pull request to the official repository.

### C-20260918-4 · 2026-09-18 · Protocol 1.4: the index first, with a `summary` clause per entry and no back-link requirement; plugin 0.3.2
- because: the owner's request (indexes that link most docs as a net positive for agents and people, without costing agent performance; back-links only where useful); R-20260918-1
- files: protocol/PROTOCOL.md §8, protocol/DOC-TYPES.md (layer table, frontmatter `summary`, rules), templates/AGENTS.md.snippet, scripts/everlast.py (`note --summary`, `build_index` shows the summary after the link), README §Using the script, .claude-plugin/plugin.json (0.3.2)
- 1.2 asked every entry to link back to its index; 1.4 drops that (the index-to-entry edge is the one graph editors show, and no study shows an agent using the reverse) and instead asks for a one-line `summary` so an index line says when to open the entry rather than being a bare path. Existing entries without a summary keep their old line; the field is optional.

### C-20260918-3 · 2026-09-18 · Plugin 0.3.1: commit subjects list added files first
- because: the owner's stated reason for the remote ("I can see what it's adding in the commits"); the first real vault commit under 0.3.0 led with `~.gitignore, -.sync.log, ...` and the new note fell into the body
- files: scripts/everlast.py (`change_summary` sorts `+` before `~` before `-`), .claude-plugin/plugin.json (0.3.1)
- The body still lists every file in that order.

### C-20260918-2 · 2026-09-18 · Protocol 1.3, plugin 0.3.0: the vault asks once for a private remote (or creates one with gh); mode `repo` docs are committed and pushed at session end, with a pull request whenever the push is not certain; commit subjects list the files
- because: the owner's request (ask for a repository or permission to create a private one, back the notes up, and make the commits show what everlast adds; then, after a mode `repo` project turned out to have three unpushed commits carrying its docs, "really it should just be pushing commits, if it's not sure then a pull request instead"); L-002
- files: scripts/everlast.py (`vault remote [<url> | --create [name]]` with a visibility re-check; `project sync <repo> [--if-changed] [--detach] [--pr] [--dry-run]` with `project_git_state`, `docs_pull_request` in a temporary worktree, `commit_paths` that commits only the doc root; `project register --sync push|pr|off` kept across re-registration; `change_summary` for every commit subject, vault included; `status_lines` and `author_email` helpers; SessionStart reports a vault without a remote and a project's uncommitted or unpushed docs; SessionEnd runs `project sync --if-changed --detach`; `vault init` prints the back-up question), scripts/test_everlast.py (twenty-six new checks against local bare remotes: docs-only commits, empty remote, fast-forward push, behind-upstream pull request branch, sync off, re-register, vault remote), protocol/PROTOCOL.md §2 (backup paragraphs, the sure/not-sure rule) and §3, protocol/PORTABILITY.md, README §What you get, §Install and §Using the script, templates/INSTALL-PROMPT.txt step 2, skills everlast-vault (§Back it up), everlast-setup (§Step 3 sync choice), everlast-capture (§Prod mechanism), .claude-plugin/plugin.json (0.3.0)
- Sure means: upstream set, not behind after a fetch, every unpushed commit the user's own, push accepted. Otherwise the doc root's current state goes on an `everlast/docs-<host>-<stamp>` branch off the remote's default branch and a pull request is opened from it (gh when the remote is GitHub, else the compare URL), so no code travels and the user's working tree, branch and index are untouched. An empty remote is pushed to directly. Existing registrations without a `sync` key behave as `push`. Also fixed in passing: `shareable_changes` lost the first unstaged file of `publish` because `run()` strips the porcelain output (L-002).

### C-20260918-1 · 2026-09-18 · Protocol 1.2: documents link each other (index per folder, Related lines, relative markdown links, no wikilinks); plugin 0.2.1
- because: the owner's request (make AI-written doc sets navigable for a human in Obsidian as well as for agents; a set of markdown files should be a graph, reachable from an index, not a pile)
- files: protocol/PROTOCOL.md §8 (new paragraph; version line), protocol/DOC-TYPES.md §Rules that keep it small (paths rule narrowed to files outside the doc set; new "linked, not just filed" rule), templates/AGENTS.md.snippet (one bullet), .claude-plugin/plugin.json (0.2.1)
- The generated INDEX.md already made every entry reachable in two hops; the new rule adds the edges between entries and states why relative markdown links are the only form that works on GitHub, in VS Code and in graph editors alike. No script change: the lint still checks backticked paths; a link check on `Related:` lines is a candidate for a later release.

### C-20260917-2 · 2026-09-17 · `pull` from the official repository, SessionStart reports a clone that is behind, `publish` pushes to the official remote
- because: the owner's request ("point the local copy to the repo as the official version to check for updates and to pull request learnings back to"); a private fork's `origin` is not the official repository, so `publish` pushing to `origin` could never open the pull request it announced
- files: scripts/everlast.py (`official_remote`, `behind_official`, `cmd_pull`; SessionStart line; `publish` pushes to the official remote), README §Using the script, protocol/PROTOCOL.md §7, AGENTS.md (fork rules), scripts/test_everlast.py
- A plain clone has `origin` = official; a private fork adds `upstream` = official and keeps `origin` private. Both work the same way from the script's point of view.

### C-20260917-1 · 2026-09-17 · Protocol 1.1, plugin 0.2.0: public release at https://github.com/m4bwav/everlast; consent-gated contribution; cross-platform scripts with CI on three operating systems; inline `<private>` marker and provenance fields
- because: the owner's request (make everlast public the way evergreen was: research, latest protocol, cross-platform scripts, versions, tests, releases; ask consent before any automatic pull request); R-20260917-1 to R-20260917-3; the Evergreen Protocol 1.6 sections 8 and 10
- files: scripts/everlast.py (`contribute yes|no|status` stored in the user's config dir with DO_NOT_TRACK and CI as no; `publish` gated on it, carrying only LEARNINGS/RESEARCH/CHANGELOG/TESTS files as a draft pull request; SessionStart nudges until decided; `strip_private_blocks` on repo-safe writes; `--agent`/`--model` provenance; portability fixes from the audit), scripts/test_everlast.py (gate cases, private-block case), scripts/everlast-hook.sh (interpreter probing), protocol/PROTOCOL.md §5 and §7, protocol/PORTABILITY.md (Codex path, SessionEnd timeout, autoMemoryDirectory), README (releases, contribution, comparable tools, python3 note), templates/INSTALL-PROMPT.txt (the consent question), .github/workflows (tests matrix, release on tag), everlast.config.json (placeholder vault path in the public tree)
- The public repository started from a scrubbed single commit (no hostnames, no owner paths); the owner's private clone is a fork of it that pulls routinely and contributes general lessons only.

### C-20260913-1 · 2026-09-13 · Plugin created: protocol 1.0, four skills, everlast.py, hooks, vault, cross-tool packaging
- because: user request (an evergreen-style plugin so nothing learned across sessions, models and agent products is lost; user-level and per-project doc sets; an excluded-folder mode for repos that must not hold the docs; a repo-safe versus private split; encryption and other backups deferred); R-20260913-1 to R-20260913-8
- files: protocol/PROTOCOL.md, PRIVACY.md, DOC-TYPES.md, PORTABILITY.md; scripts/everlast.py (aidocs.py plus vault, registry, modes, tiers, privacy gate and scan, export, pack, sync, hooks), scripts/everlast-hook.sh, scripts/test_everlast.py; hooks/hooks.json; adapters/copilot/hooks.json; templates/; evals/; .claude-plugin/plugin.json and marketplace.json; everlast.config.json; skills/everlast-setup, everlast-capture, everlast-resume (absorbed from the ai-docs-* skills with their histories), everlast-vault (new)
- Decisions recorded in `ai-docs/decisions/`: absorb the ai-docs skills rather than depend on them; a separate private vault repository rather than data inside the plugin repo; excluded mode as a junction from the vault plus `.git/info/exclude`, with a lint re-check because Claude Code rewrites that file; privacy by rules first with a one-line question when borderline; evergreen pointer mode for every unit; encryption deferred.
