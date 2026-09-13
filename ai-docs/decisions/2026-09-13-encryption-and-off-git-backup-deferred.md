---
title: Encryption and off-git backup deferred
kind: decision
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [privacy, backup]
---

# Encryption and off-git backup deferred

## Context
The user wants the option to encrypt the vault or sidecars and back them up outside git later.

## Decision
Deferred. The layout is fixed now (plain markdown, one repo); encryption and alternative backup routes are a later layer. Candidates recorded: sops with age recipients (per-file, diffable), gocryptfs (transparent folder mount); git-crypt rejected as stagnant.

## Reasons
Nothing in the doc layout changes when encryption arrives, and a private GitHub repository already meets today's need. Building it now would delay the habit that matters (capture and resume).

## Rejected alternatives
- Encrypt from day one with git-crypt: last major update 2025-09; sops and age are the current recommendation.

## Consequences
The vault must stay a private repository until this is built. Revisit when the vault holds work-project sidecars or when a machine cannot use GitHub.
