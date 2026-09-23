---
title: Trunk-based development with short-lived branches
kind: decision
status: active
date: 2026-04-15
verified: 2026-04-15
tags: [git, process]
aliases: [mainline development, no long-lived branches]
---

# Trunk-based development with short-lived branches

## Context
Long feature branches merged painfully before each milestone.

## Decision
Branches live a day or two and merge behind feature flags.

## Reasons
Smaller merges, earlier integration.

## Rejected alternatives
- Git flow with a develop branch: two long-lived lines to keep in step.
