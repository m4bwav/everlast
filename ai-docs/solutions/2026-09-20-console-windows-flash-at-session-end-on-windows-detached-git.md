---
title: Console windows flash at session end on Windows: detached git needs CREATE_NO_WINDOW
kind: solution
status: active
date: 2026-09-20
verified: 2026-09-20
tags: [windows, hooks, subprocess]
summary: Read when console windows pop up on Windows at session end, or before adding any subprocess call to a hook path
---

# Console windows flash at session end on Windows: detached git needs CREATE_NO_WINDOW

## Problem
Closing VS Code (or any Claude Code session run without its own terminal) flashed a burst of console windows on Windows. Only at session end; never in a terminal session.

## Cause
The SessionEnd hook hands the vault sync and the project sync to a detached python (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`). A detached process has no console. Every console program it then runs (`git.exe`, plus the `ssh.exe` or credential helper git spawns) gets a brand-new visible console from Windows because there is none to inherit. `run()` and `status_lines()` in `scripts/everlast.py` passed no creation flags, so each of the five or so git calls per sync opened a window; two syncs (vault and project) doubled it. Inside a terminal the console is inherited, so nothing shows.

## Fix (fork 0.3.4; official 0.4.0)
`creationflags=CREATE_NO_WINDOW` (0x08000000) on every subprocess call, via a `NO_WINDOW` constant next to `run()`. `CREATE_NO_WINDOW` gives the child a hidden console that its own children inherit; `DETACHED_PROCESS` alone does not. The constant is also passed to the detached launcher, where Windows ignores it (it is documented as ignored next to `DETACHED_PROCESS`), so the calls that matter are `run()` and `status_lines()`. evergreen_sync.py already did this (`detach_self` and its git runner).

## Verified by
Close a VS Code Claude Code session with an uncommitted vault change: no windows, and the vault's `.sync.log` gains a `commit: ok` / `push: ok` line (2026-09-20). A read-only check that the flag is in place: `python -c "import sys; sys.path.insert(0, 'scripts'); import everlast; print(hex(everlast.NO_WINDOW))"` from the plugin root prints `0x8000000` on Windows and `0x0` elsewhere.

## Seen in passing
`.sync.log` had two `pull --rebase failed: fatal: Cannot rebase onto multiple branches` lines. The vault was clean and tracked `origin/main` correctly afterwards; the likely cause is the vault sync and a project sync racing on the same repository. Not fixed; watch for it.
