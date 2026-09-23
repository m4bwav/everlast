---
title: Newtonsoft Json.NET for save files
kind: decision
status: superseded
date: 2026-02-02
verified: 2026-02-02
tags: [saves, serialization]
superseded_by: decisions/2026-07-15-system-text-json-for-save-files.md
---

# Newtonsoft Json.NET for save files

## Context
Save files need a readable format that survives schema changes.

## Decision
JSON through Newtonsoft Json.NET.

## Reasons
Polymorphic types and tolerant reading.

## Rejected alternatives
- Binary serialization: unreadable and brittle across versions.
