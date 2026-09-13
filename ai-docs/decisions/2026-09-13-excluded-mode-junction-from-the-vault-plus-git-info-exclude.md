---
title: Excluded mode: junction from the vault plus git info exclude
kind: decision
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [excluded, git]
---

# Excluded mode: junction from the vault plus git info exclude

## Context
Some projects (work, clients, open source) must not carry an ai-docs/ folder. The docs still need to feel local to the project so relative paths and habits stay the same.

## Decision
Mode excluded: the doc set lives at `<vault>/projects/<slug>/ai-docs/` and is junctioned (Windows) or symlinked (posix) into the project as ai-docs/; the folder is appended to .git/info/exclude; the lint re-checks `git check-ignore` on every run and tells the user to re-run register when the exclusion is gone. `--no-link` keeps the docs in the vault only.

## Reasons
A junction needs no admin rights on Windows and the files stay inside the vault repo, so they are backed up and reach other machines for free. The info/exclude file is per clone and invisible to collaborators. Research found Claude Code rewrites that file on some versions (anthropics/claude-code#84954), hence the lint check rather than trust.

## Rejected alternatives
- Global core.excludesFile with ai-docs/: would hide the folder in repo-mode projects too.
- Nested git repo inside the project: two repos to sync per project and a confusing git status for the parent.
- Central store only, nothing in the project: loses locality; kept as the --no-link fallback when a link cannot be created.

## Consequences
Tools that refuse to follow junctions would see an empty folder; none observed yet. A project moved to another machine needs register again (the vault path is per machine).
