---
title: Leaderboard API returns 429 during events
kind: solution
status: active
date: 2026-09-18
verified: 2026-09-18
tags: [backend, api]
aliases: [429 Too Many Requests, rate limit exceeded]
---

# Leaderboard API returns 429 during events

## Problem
During live events the leaderboard service answered most requests with Too Many Requests; clients polled every 2 seconds.

## Fix
Clients back off exponentially with jitter (`Assets/Scripts/Net/LeaderboardClient.cs`), and the service allows 60 requests a minute per player.

## Verified by
A k6 load test with 5,000 virtual players produced no 429 responses.
