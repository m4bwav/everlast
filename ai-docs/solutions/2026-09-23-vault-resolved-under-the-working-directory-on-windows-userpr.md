---
title: "Vault resolved under the working directory on Windows: %USERPROFILE% was never expanded"
kind: solution
status: active
date: 2026-09-23
verified: 2026-09-23
stale_after: 2026-12-22
tags: [windows, vault, config]
aliases: [vault missing, expandvars, "%USERPROFILE%\\everlast-vault (missing)"]
summary: read when vault where prints a path holding %USERPROFILE% or $HOME, or a fresh Windows install says the vault is missing
agent: claude-code
---

# Vault resolved under the working directory on Windows: %USERPROFILE% was never expanded

## Problem
In a clone of the public repository with no `EVERLAST_VAULT` set, `python scripts/everlast.py vault where` printed `<clone>\%USERPROFILE%\everlast-vault (missing)`: the shipped Windows default in `everlast.config.json` was used as a literal relative path. `vault init` would have created a folder named `%USERPROFILE%` in the current directory, and every session would report the vault as missing.

## Dead ends
None tried; it showed up while reading `vault where` output during the 0.4.0 work. The owner's fork never hit it because its config names a real path.

## Fix
`vault_path()` in `scripts/everlast.py` calls `os.path.expandvars` before `os.path.expanduser`, for both `EVERLAST_VAULT` and the config value (plugin CHANGELOG C-20260923-1, LEARNINGS L-004).

## Verified by
`python scripts/everlast.py vault where` with `EVERLAST_VAULT` unset now prints the vault under the user's home folder (2026-09-23, Windows); `python scripts/test_everlast.py` includes "vault paths expand environment variables", which fails without `expandvars`.

## Applies when
Any path read from `everlast.config.json` or the environment. `%VAR%` expands only on Windows; `$VAR` expands on every OS.
