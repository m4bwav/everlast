---
title: Memory leak in the inventory pool
kind: solution
status: active
date: 2026-09-15
verified: 2026-09-15
tags: [unity, performance]
summary: read when heap size climbs over a long session
---

# Memory leak in the inventory pool

## Problem
After about 40 minutes of play the process grew past 6 GB and the handheld closed the game.

## Dead ends
- The texture streaming budget: unchanged heap after lowering it.
- Audio clip loading: the clips were already streamed.

## Fix
`InventorySlotPool.Release` never unsubscribed `OnItemChanged`, so released slots stayed reachable. Unsubscribe in `Assets/Scripts/Inventory/InventorySlotPool.cs`.

## Verified by
A Memory Profiler capture after 60 minutes showed the managed heap flat at 410 MB.
