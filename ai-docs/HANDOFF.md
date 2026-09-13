# Handoff

## Current state
Plugin 0.1.0 complete: protocol/ (PROTOCOL, PRIVACY, DOC-TYPES, PORTABILITY), four skills, `scripts/everlast.py` with a passing self-test (`scripts/test_everlast.py`, 21 checks), hooks, Copilot adapter, templates, evals. Vault at the config path with the user tier seeded from the evergreen profile. Both repositories on GitHub (private). Installed in Claude Code via mark-local.

## In progress
Eval suites written, not all run (claude plugin eval cases under evals/; skill evals.json per skill).

## Decisions made this session
See decisions/ (absorb ai-docs skills; separate vault repo; excluded mode via junction plus info/exclude; privacy rules first; encryption deferred).

## Dead ends hit
- Global core.excludesFile for ai-docs/ would hide repo-mode docs too; rejected.
- Writing CHANGELOG/README before running evergreen.py init: init overwrites them from templates; run init first, then write.
- Bash heredocs with many apostrophes in one command failed to parse; write bodies with the Write tool, then call the script.

## Next single action
Run the remaining eval cases (claude plugin eval from the plugin root) and log them as T- entries in TESTS.md.
