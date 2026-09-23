---
title: Leaderboard reads served from a materialized view
kind: solution
status: active
date: 2026-09-08
verified: 2026-09-08
stale_after: 2026-12-07
tags: [backend, postgres, performance]
---

# Leaderboard reads served from a materialized view

## Problem
During events players saw their own score missing for up to a minute: the cached page lagged the database.

## Dead ends
- Shorter cache expiry: load went back up.

## Fix
Serve reads from a Postgres materialized view refreshed every 10 s (`backend/Db/Migrations/0042_leaderboard_view.sql`), with no cache in front.

## Verified by
p95 latency 35 ms; a posted score appears within 10 s.

Related: see also [Cache leaderboard reads in Redis for 60 seconds](2026-04-12-cache-leaderboard-reads-in-redis-for-60-seconds.md)
