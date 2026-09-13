# Handoff

## Current state
Plugin 0.1.0 complete: protocol/ (PROTOCOL, PRIVACY, DOC-TYPES, PORTABILITY), four skills, `scripts/everlast.py` with a passing self-test (`scripts/test_everlast.py`, 21 checks), hooks, Copilot adapter, templates, evals. Vault at the config path with the user tier seeded from the evergreen profile. Both repositories on GitHub (private). Installed in Claude Code via mark-local.

## In progress
First runs logged in TESTS.md (resume 4/4 via plugin eval; privacy-1 pass via evergreen-tester). Bash-granting plugin-eval cases cannot run on this Windows PC (LEARNINGS L-001); the remaining skill cases (setup, vault, capture triggers) are still to run with evergreen-test.

## Decisions made this session
See decisions/ (absorb ai-docs skills; separate vault repo; excluded mode via junction plus info/exclude; privacy rules first; encryption deferred).

## Dead ends hit
- Global core.excludesFile for ai-docs/ would hide repo-mode docs too; rejected.
- Writing CHANGELOG/README before running evergreen.py init: init overwrites them from templates; run init first, then write.
- Bash heredocs with many apostrophes in one command failed to parse; write bodies with the Write tool, then call the script.

## Next single action
Install on the work laptop with `templates/INSTALL-PROMPT.txt` and register one work repo in excluded mode.
