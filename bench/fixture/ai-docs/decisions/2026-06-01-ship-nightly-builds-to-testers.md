---
title: Ship nightly builds to testers
kind: decision
status: active
date: 2026-06-01
verified: 2026-06-01
tags: [release, testing]
---

# Ship nightly builds to testers

## Context
Testers found regressions a week late.

## Decision
Every nightly build that passes the smoke tests goes to the tester group.

## Reasons
Faster feedback on regressions.

## Rejected alternatives
- Weekly builds: too slow.

## Consequences
Testers see unfinished features.

Related: contradicts [Ship tester builds only from tagged releases](2026-08-20-ship-tester-builds-only-from-tagged-releases.md)
