---
title: Cache leaderboard reads in Redis for 60 seconds
kind: solution
status: active
date: 2026-04-12
verified: 2026-04-12
tags: [backend, redis, performance]
---

# Cache leaderboard reads in Redis for 60 seconds

## Problem
The leaderboard page took over a second to load at peak.

## Fix
Cache the top-100 query in Redis with a 60 s expiry (`backend/Leaderboard/CachedLeaderboard.cs`).

## Verified by
p95 latency dropped to 180 ms in the load test.
