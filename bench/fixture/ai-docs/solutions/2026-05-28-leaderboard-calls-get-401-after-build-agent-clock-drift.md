---
title: Leaderboard calls get 401 after build agent clock drift
kind: solution
status: active
date: 2026-05-28
verified: 2026-05-28
tags: [backend, auth, ci]
aliases: [invalid_token, The token is not valid yet]
---

# Leaderboard calls get 401 after build agent clock drift

## Problem
Integration tests against the leaderboard failed with 401 on the Mac build agent only. The service rejected the token as not valid yet.

## Dead ends
- Rotating the signing key: no change.

## Fix
The agent's clock ran 3 minutes ahead, so the token's not-before claim was in the future for the server. Enable network time on the agent and allow two minutes of skew in `backend/Auth/JwtSetup.cs` (`ClockSkew = TimeSpan.FromMinutes(2)`).

## Verified by
The integration suite passed on the agent three runs in a row.
