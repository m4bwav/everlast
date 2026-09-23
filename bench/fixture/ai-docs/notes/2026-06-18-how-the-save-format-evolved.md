---
title: How the save format evolved
kind: note
status: active
date: 2026-06-18
verified: 2026-06-18
tags: [saves, serialization]
---

# How the save format evolved

## Summary
Why save files look the way they do, version by version.

## Details
Version 1 was binary; version 2 moved to JSON with Json.NET; version 3 kept the JSON and switched to System.Text.Json. Each version carries `formatVersion`, and `SaveMigrator` upgrades one step at a time.
