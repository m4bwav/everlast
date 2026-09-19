# The Everlast Protocol

Version 1.4 (2026-09-18). What an AI coding agent does so that nothing it learns is lost when the user changes session, model, tool or vendor. A sibling of the Evergreen Protocol (which keeps skills and research current); everlast keeps the knowledge gained while working. Every everlast skill points here. Companion specs: [DOC-TYPES.md](DOC-TYPES.md) (which documents, their shape, budgets, prune rules), [PRIVACY.md](PRIVACY.md) (what may sit in a shared repository), [PORTABILITY.md](PORTABILITY.md) (install per tool). Evidence: [../RESEARCH.md](../RESEARCH.md).

## 1. Why this exists

Every vendor now ships memory: Claude Code auto-memory, Codex memories, Copilot Memory, Gemini auto-memory. None of it survives a switch of product, and most of it is machine-local. The user works across all of them and wants the history to be theirs, on disk, in plain markdown, versioned, readable by whatever agent comes next. Three 2026 studies also show that always-loaded repository overviews cost tokens without raising success, while distilled, hard-won, on-demand procedures (setup steps, dead ends and fixes, decisions with reasons) measurably help. So everlast keeps the always-on layer tiny and puts everything else behind an index.

Five principles decide most edge cases:

1. Plain files the user owns. Markdown, git, relative links, no tool-specific syntax in shared files. The record is the files, never a product's memory; native memories hold pointers only.
2. Two tiers, one layout. The user tier (about the person, their machines, lessons that span projects) lives in a private vault repository. The project tier lives with the project when the project can hold it, in the vault when it cannot. Both use the same doc set so one script and one habit cover both.
3. Private by default at the boundary. Anything naming a person other than the user, an opinion about people or teams, a credential, an internal name or a customer goes to a private store, never to a repository other people can read. A scan enforces it; a human can override with a recorded decision.
4. On demand, not always-on. One short pointer in the always-on file; an index of one line per entry; entries opened only when their title or tags match. Budgets keep every file small.
5. Evidence, not narration. A capture is proven by the file the script printed; a resume by the file reads in the trace; a sync by the commit in the vault or the project remote. A reply saying it was done proves nothing.

## 2. The tiers

| Tier | Where | Holds | Shared with |
|---|---|---|---|
| user | `<vault>/user/` | `PROFILE.md` (how the user wants work done, each rule with its reason), `ENVIRONMENTS.md` (machines, tools, paths, what works where), `INDEX.md`, `HANDOFF.md` (what the user was doing across projects), `log.md`, `decisions/ solutions/ plans/ notes/` for cross-project lessons | nobody; the vault is private |
| project, mode `repo` | `<repo>/ai-docs/` | the project doc set (DOC-TYPES.md) | whoever reads the repository |
| project, mode `excluded` | `<vault>/projects/<slug>/ai-docs/`, junctioned to `<repo>/ai-docs/` and listed in `.git/info/exclude` | the same doc set, for a repository that must not carry it (work, client, open source) | nobody |
| private sidecar | `<vault>/projects/<slug>/private/` | the entries a project produces that fail PRIVACY.md, in the same shapes | nobody |

The vault is one git repository with a private remote; every machine clones it. Its path comes from `EVERLAST_VAULT`, then `everlast.config.json` at the plugin root, then `~/everlast-vault`. `registry.json` in the vault lists every project with its path, mode and sync setting, so a new session can find the roots without asking.

Backup is part of the layout. When a vault is created and whenever a session starts with a vault that has no remote, the agent asks the user once: the URL of a private repository they already have (`everlast.py vault remote <url>`), or permission to create one (`everlast.py vault remote --create [name]` runs `gh repo create --private` in their account and re-checks that the result is private; one that comes out public is disconnected on the spot). Nothing is pushed until the user chooses. The remote must be private because the vault names people and machines by design; credentials never belong in it at all (PRIVACY.md), so a private remote is the whole requirement. The reason for a remote at all: a vault on one disk is a single point of loss, and the commit history is where the user sees what agents have been writing.

A mode `repo` project's doc set is backed up by the project's own remote. At session end the SessionEnd hook (or `everlast.py project sync <repo>`) commits the doc root, and only the doc root (the user's other changes stay as they were, staged or not), with a subject that lists what was added or changed, then pushes the branch when it is sure and opens a pull request when it is not. Sure means all of: the branch has an upstream, it is not behind that upstream after a fetch, every unpushed commit is the user's own, and the push is accepted. Anything else (no upstream, behind or diverged, someone else's commits in the range, a rejected or protected push, or the project registered with `--sync pr`) puts the doc root's current state on a fresh `everlast/docs-<host>-<stamp>` branch off the remote's default branch and opens a pull request from it, so the docs still reach the remote for review and no code travels with them. An empty remote is pushed to directly; there is nothing on it to be unsure about. `--sync off` leaves the project's git to the user, and the SessionStart line reports uncommitted or unpushed docs instead. Commit subjects and bodies list the files (`+new ~changed -gone`), in the vault as well, so the history itself shows what everlast wrote.

## 3. Session shape

- Start. The Claude Code SessionStart hook prints one orientation line (project slug and mode, user-tier entry count, vault behind or missing) and the project HANDOFF when it holds real content. In a tool without hooks, `everlast-resume` Step 1 does the same read by hand. New to a machine or product: read `user/PROFILE.md` and the machine's section of `user/ENVIRONMENTS.md` once.
- During. Write a user-tier lesson the moment it happens (a correction, a preference, an environment fact); do not wait for the end. Anything about a skill goes to that skill's `LEARNINGS.md` (evergreen); anything about the code's layout to `CODEMAP.md`; a repo rule to `AGENTS.md`.
- End. `everlast-capture`: harvest, route, classify for privacy, write with the script, rewrite HANDOFF when work is unfinished, lint. The Stop hook nudges once when the tree changed and nothing was written. The SessionEnd hook commits and pushes the vault, and a mode `repo` project's doc root (push when sure, pull request when not; section 2), each in a detached process.

## 4. Routing, most specific home wins

1. A rule every session must obey in this repo: `AGENTS.md`, with its reason.
2. Where a system lives: `CODEMAP.md` or the evergreen map.
3. A lesson about how a skill performs: that skill's `LEARNINGS.md`.
4. A research finding on a subject with its own skill: that skill's `RESEARCH.md`.
5. About the user, their machines, or a lesson that spans projects: the user tier.
6. About this project and safe to share: the project doc set.
7. About this project and not safe to share: the private sidecar.
8. Derivable from the code in a minute: nowhere.

## 5. Privacy

Classification happens before the write, by the rules in PRIVACY.md, and the script's scan repeats it. An inline `<private>...</private>` block in a body is dropped from any repo-safe write and kept only in a `--private` one, so a single draft can hold both halves: a repo-safe write that trips the scan is refused until it is written `--private` or `--allow-private` records a human decision. Names, hostnames and codenames the user adds to `<vault>/config/redact.txt` extend the scan. Private content is quoted to the user, never copied into a repo-safe file, a commit message, a pull request or a message to anyone else. Encryption at rest is a later layer (a decision in the plugin's `ai-docs/`); the layout does not change when it arrives.

## 6. Portability

The plugin is one git repository. Claude Code installs it as a plugin (hooks included); Cowork takes the packed `.plugin`; Copilot, Codex, OpenCode and Windsurf read the four skills from `~/.agents/skills/` after `everlast.py export`; Cursor and Gemini need one more link. The vault is a second repository cloned beside it. Details and the one-paste install prompt: PORTABILITY.md and `templates/INSTALL-PROMPT.txt`.

## 7. Maintenance and contribution

Every everlast skill and the plugin itself are evergreen units in pointer mode: research refreshes on a schedule, learnings captured as they happen, tests that pass on evidence. The protocol here changes by delta edits with a `C-` entry in `../CHANGELOG.md`; two clones adding entries merge by union.

The official version is https://github.com/m4bwav/everlast. Updates flow from it into every install with `everlast.py pull` (it finds the remote that points at the official repository, `upstream` on a fork, `origin` on a plain clone; the SessionStart line reports when the clone is behind; Claude Code then needs `claude plugin marketplace update` and a reinstall when skills, scripts or hooks changed). The other direction needs consent, asked once at install and stored in the user's config directory, never in the plugin tree: `everlast.py contribute yes` lets `everlast.py publish` (run by the SessionEnd hook) push the plugin's own changed `LEARNINGS.md`, `RESEARCH.md`, `CHANGELOG.md` and `TESTS.md` files as a draft pull request in the user's name; nothing else ever travels (not the vault, not a project's docs, not transcripts). `contribute no` means nothing leaves the machine by any route. Unanswered counts as no for anything unattended; `DO_NOT_TRACK=1` and `CI=true` are a no that also silences the question. The choice is not re-asked on a version bump, only if what is shared ever widens. A private fork holds customisations that should not be shared (a real vault path, private units) and pulls from the official repository routinely; it contributes only general lessons, as pull requests from a branch off the official `master`.

Scripts and hooks are cross-platform wherever that is not onerous (the Evergreen Protocol section 8 and its PORTABILITY checklist): stdlib Python or POSIX `sh`, `pathlib`-style paths, UTF-8 and LF, no platform tool without a branch or a message; CI runs the self-test on Linux, macOS and Windows on every push.

## 8. Tone and hygiene

Write for the next reader, who may be a different model in a different tool with no chat history. Imperative voice. Absolute dates. No em dashes. Say what is uncertain. Every rule carries the reason it exists, so it can be deleted when the reason goes away.

Link the documents together, through the index first. A doc set is a small graph, not a pile: the generated `INDEX.md` lists every entry on one line (`date [title](path) (status) tags: when to read it`), an entry that builds on, contradicts or supersedes another ends with a `Related:` line, and a reference to another document is a relative markdown link (`[title](../solutions/2026-09-06-cs0103.md)`), never a bare filename. The reason is twofold: an agent opens only what the index points it to (a map queried on demand measurably helps, an overview loaded every session measurably does not; RESEARCH.md R-20260918-1), and a human reading the same files in a graph-aware editor (Obsidian, Foam, Logseq) gets backlinks and a navigable graph for free. An entry needs no link back to the index: the index-to-entry edge is the one editors show and the lint counts, and no study shows an agent using the reverse; one `Up:` line is allowed where readers lack a backlinks pane (GitHub). The index stays small (120 lines; past that the prune pass archives or the set splits by folder) and is read at task start, never pasted into `AGENTS.md`. Relative markdown links are the one form that works in all of those readers and on GitHub; wikilinks (`[[...]]`) do not render outside graph editors, so do not use them in a shared repository. Rules for the format are in [DOC-TYPES.md](DOC-TYPES.md).
