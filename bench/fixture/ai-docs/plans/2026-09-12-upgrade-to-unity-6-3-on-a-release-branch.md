---
title: Upgrade to Unity 6.3 on a release branch
kind: plan
status: active
date: 2026-09-12
verified: 2026-09-18
tags: [unity, upgrade]
supersedes: plans/2026-07-01-upgrade-to-unity-6-lts.md
---

# Upgrade to Unity 6.3 on a release branch

## Goal
Ship the next release on Unity 6.3 without blocking daily work.

## Status
The branch builds; two editor tools still fail.

## Steps
- [x] Branch `release/unity-6.3`
- [ ] Port the two editor tools
- [ ] Soak test for a week

## Next single action
Port the level tool's custom inspector.

Related: supersedes [Upgrade to Unity 6 LTS](2026-07-01-upgrade-to-unity-6-lts.md)
