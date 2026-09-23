---
title: Addressables instead of Resources folders
kind: decision
status: active
date: 2026-02-10
verified: 2026-02-10
tags: [unity, addressables, assets]
---

# Addressables instead of Resources folders

## Context
Everything under `Resources/` loads at startup, and every patch shipped the whole asset set again.

## Decision
Move runtime assets to Addressables groups by feature; keep `Resources/` for the boot splash only.

## Reasons
Memory at the title screen and download size for patches.

## Rejected alternatives
- Hand-built AssetBundles: the same result with more code to own.

## Consequences
Content builds become a CI step; missing references now fail the content build instead of at runtime.
