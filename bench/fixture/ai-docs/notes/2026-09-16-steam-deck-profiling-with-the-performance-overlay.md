---
title: Steam Deck profiling with the performance overlay
kind: note
status: active
date: 2026-09-16
verified: 2026-09-16
tags: [performance, steam-deck, tools]
---

# Steam Deck profiling with the performance overlay

## Summary
The quicker route since SteamOS 3.7: the built-in performance overlay plus Unity markers, with the profiler only for deep dives.

## Details
Level 4 of the overlay shows frame time, GPU and CPU load; Unity's `ProfilerMarker` names appear in the capture tool. Attach the Unity profiler over the network only when a marker points somewhere.

Related: builds on [Profiling on the Steam Deck](2026-04-28-profiling-on-the-steam-deck.md)
