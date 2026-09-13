# Privacy: what may sit in a shared repository

Part of the [Everlast Protocol](PROTOCOL.md). Applied by `everlast-capture` before every write and repeated by `everlast.py` (the `note` and `handoff` gate, `scan`, and `lint`). The rule is rules first, ask when unsure: the checklist decides most entries; a borderline one gets a one-line question; while waiting, it is private.

## Private by default (sidecar or user tier, never a project repository)

- Any named person other than the user: coworkers, managers, customers, vendors' staff, family. Also people identified by role ("my manager", "the reviewer on the platform team").
- Opinions and judgements about people, teams, management, or company direction. Anything that reads as politics, blame, or a complaint.
- Anything learned from a private conversation, chat, email, or meeting, including who said what.
- Credentials of any kind: passwords, tokens, keys, connection strings, cookies, one-time codes. Even expired ones; they reveal formats and habits.
- Internal hostnames, IP ranges, environment names, project codenames, unreleased product names, customer names, contract terms, prices not public.
- Compensation, HR, legal, health, and personal-life facts about anyone.
- The user's own contact details and home address.

## Repo-safe

- Technical facts about the code, build, tests, tools, and commands, with the output that proved them.
- Decisions and their technical reasons; rejected alternatives on technical grounds.
- Plans, status, next actions, as long as they name no one and quote no private conversation.
- Public documentation, public issue numbers, public package versions, public URLs.

## The user tier is private too

`<vault>/user/` names the user's machines, paths, habits and preferences. It never leaves the vault. A skill or profile shared with other people is written from it by hand, not copied.

## Borderline, ask once

- A named open-source maintainer or a public figure in a technical context (usually safe; ask if the entry judges them).
- A coworker's technical contribution ("X wrote the migration script"): safe as an anonymous fact ("the migration script in `tools/`"), private with the name.
- A company-internal tool name that is also on the company's public blog.

Ask in one line listing the entries: "Two entries name people or internal hosts; keep them private (default) or allow them in the repo?" Record an override with `--allow-private`; the entry's log line shows it was reviewed.

## Never do this

- Rewrite a sensitive entry into a vague public one and call it done. Write the full version privately; if a technical lesson survives without the people, write that as a second, public entry.
- Copy a private entry into a commit message, pull request, issue, or a message to anyone.
- Put a redaction pattern in a public file. `config/redact.txt` lives in the vault only.

## The scan

`everlast.py scan <repo>` and the write-time gate look for: email addresses; API tokens (`sk-`, `ghp_`, `xox`, `AKIA` and friends); assignments like `password=` or `token:`; bearer tokens; private-key blocks; `@handles`; phone numbers; people by role; words that signal opinions about people or politics; every regex in `<vault>/config/redact.txt`. It is a net, not a judge: a clean scan does not make an entry safe, and a hit is a prompt to think, not a verdict. Add every coworker, customer, internal host and codename to `redact.txt` the first time it comes up.

## Later

Encryption at rest for the vault or the sidecars (sops with age recipients for per-file diffs; gocryptfs for a transparent folder) and an off-git backup route are deferred by decision. They change nothing in this file.
