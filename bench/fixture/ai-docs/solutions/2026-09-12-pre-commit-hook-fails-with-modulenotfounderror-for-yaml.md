---
title: Pre-commit hook fails with ModuleNotFoundError for yaml
kind: solution
status: active
date: 2026-09-12
verified: 2026-09-12
tags: [python, hooks, tools]
aliases: ["ModuleNotFoundError: No module named 'yaml'"]
---

# Pre-commit hook fails with ModuleNotFoundError for yaml

## Problem
The asset lint pre-commit hook failed on every commit on the Mac with a missing `yaml` module, while the same script worked when run by hand.

## Dead ends
- `pip install pyyaml` into the system Python: the hook runs a different interpreter.

## Fix
Point the hook at the project's virtual environment in `.pre-commit-config.yaml` (`language: system`, entry `tools/.venv/bin/python tools/asset_lint.py`) and install the requirements there: `tools/.venv/bin/python -m pip install -r tools/requirements.txt`.

## Verified by
`pre-commit run asset-lint --all-files` printed `Passed`.
