---
title: Ship tester builds only from tagged releases
kind: decision
status: active
date: 2026-08-20
verified: 2026-08-20
tags: [release, testing]
---

# Ship tester builds only from tagged releases

## Context
Testers lost save files twice to nightly builds with half-done migrations.

## Decision
Testers get builds from release tags only.

## Reasons
Stable saves for the people giving feedback.

## Rejected alternatives
- Nightly builds with save backups: still broke the play sessions.

## Consequences
Regressions reach testers later.

Related: contradicts [Ship nightly builds to testers](2026-06-01-ship-nightly-builds-to-testers.md)
