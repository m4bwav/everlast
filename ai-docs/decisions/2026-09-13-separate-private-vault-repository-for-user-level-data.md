---
title: Separate private vault repository for user-level data
kind: decision
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [vault, privacy]
---

# Separate private vault repository for user-level data

## Context
User-level knowledge (profile, environments, cross-project lessons) and project sidecars need a home that every machine can clone. Evergreen keeps its profile/ inside the plugin repo, which makes that repo unshareable.

## Decision
A second, always-private repository, everlast-vault (github.com/m4bwav/everlast-vault), cloned to the path in `everlast.config.json` per OS (Windows: a Documents folder off the OS drive; posix: ~/everlast-vault). The plugin repo holds no personal data and can be shared later. Evergreen's profile/ files became pointers into the vault.

## Reasons
Separating code from data is what lets the protocol be published without a scrub. One vault also gives the excluded-mode projects and the private sidecars a single backup route. EVERLAST_VAULT overrides the config, mirroring evergreen's store convention.

## Rejected alternatives
- Data inside the plugin repo: simplest, but the plugin could never be public and every clone would carry every machine's facts.
- Local folder with no repo: nothing survives a machine loss and nothing reaches the next machine.

## Consequences
Two clones per machine instead of one; the install prompt covers both. The vault is synced by the SessionEnd hook in Claude Code and by hand elsewhere.
