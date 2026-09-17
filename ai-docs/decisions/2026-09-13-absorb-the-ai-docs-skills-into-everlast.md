---
title: Absorb the ai-docs skills into everlast
kind: decision
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [skills, lineage]
---

# Absorb the ai-docs skills into everlast

## Context
The three ai-docs-* skills (setup, capture, resume) already produced the per-project layout everlast needs. Everlast adds a user tier, a privacy split, an excluded mode and cross-tool install. Three options: absorb the skills into the plugin, depend on them as separate installs, or reimplement.

## Decision
Absorb: the three skills moved into the plugin as everlast-setup, everlast-capture, everlast-resume, keeping their CHANGELOG, RESEARCH, LEARNINGS, TESTS and evals; aidocs.py became `scripts/everlast.py`. The standalone copies are parked, not deleted.

## Reasons
One thing to install on a new machine is the whole point of the plugin. The absorbed histories keep the reasoning lineage (evergreen rule: never regenerate). A dependency would mean two installs and two places for one rule.

## Rejected alternatives
- Depend on ai-docs-*: two installs, and every protocol change touches two repos.
- Reimplement fresh: loses seven research findings and four test runs already paid for.

## Consequences
The ai-docs-* skills under the Claude and .agents skill roots are parked in the skills-parked lots; anything that named them (AGENTS.md blocks in other repos) should be updated to the everlast names when next touched. The evergreen registry now lists the everlast units instead.
