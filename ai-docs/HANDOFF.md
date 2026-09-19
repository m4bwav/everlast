# Handoff

## Current state
Plugin 0.3.0, protocol 1.3 (2026-09-18). `scripts/test_everlast.py` passes 57 checks on Windows (T-20260918-1). New since 0.2.1: `vault remote [<url> | --create]` (asked once; private only), `project sync` for mode `repo` (commit the doc root alone, push when sure, pull request when not; `--sync push|pr|off` on register), descriptive commit subjects everywhere, SessionStart lines for a remote-less vault and for uncommitted or unpushed project docs, SessionEnd runs `project sync --if-changed --detach`. The reasoning is in `decisions/2026-09-18-project-docs-push-when-sure-pull-request-when-not-vault-remo.md`; the change log entry is C-20260918-2; L-002 records the `run()` strip bug that also affected `publish`.

## In progress
Nothing half-done in the tree. Still open from earlier sessions: the skill eval suites (setup, vault, capture triggers) have not been run with `evergreen-test` on a machine with a sandbox backend (L-001); a link check on `Related:` lines in the lint is a candidate for a later release (C-20260918-1).

## Decisions made this session
See the 2026-09-18 decision entry: push directly only when upstream set, not behind, all commits the user's own, push accepted; otherwise a docs-only `everlast/docs-*` branch and a pull request; pathspec commits; temporary worktree for the PR branch; private remote is the whole requirement for the vault.

## Dead ends hit
- Parsing `git status --porcelain` from `run()`: its `strip()` eats the first line's leading space, so `ln[3:]` returns `i-docs/INDEX.md` (L-002). Use `status_lines()`.
- `git config user.email` is empty when identity comes from `GIT_AUTHOR_EMAIL`; `git var GIT_AUTHOR_IDENT` is the reliable source for "whose commits are the user's own".
- `everlast.py note --kind note` needs a `## Summary` heading; a body with solution headings is refused (fail-soft, so the test saw nothing written).

## Next single action
Tag `v0.3.0` on the official clone after the commit, pull it into the private fork (`everlast.py pull`), then `claude plugin marketplace update` and reinstall so the hooks run the new script.
