---
title: System.Text.Json for save files
kind: decision
status: active
date: 2026-07-15
verified: 2026-07-15
tags: [saves, serialization]
supersedes: decisions/2026-02-02-newtonsoft-json-net-for-save-files.md
---

# System.Text.Json for save files

## Context
Json.NET's reflection cost showed up in the save hitch, and the package is one more dependency to ship.

## Decision
Keep JSON for player progress, written with System.Text.Json source generators.

## Reasons
No reflection at runtime, faster saves, one fewer package.

## Rejected alternatives
- Staying on Json.NET: the hitch.
- A binary format: readable saves help support.

## Consequences
Every saved type needs an entry in `Assets/Scripts/Saves/SaveJsonContext.cs`.

Related: supersedes [Newtonsoft Json.NET for save files](2026-02-02-newtonsoft-json-net-for-save-files.md)
