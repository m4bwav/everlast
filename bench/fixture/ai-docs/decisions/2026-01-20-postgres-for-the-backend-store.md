---
title: Postgres for the backend store
kind: decision
status: active
date: 2026-01-20
verified: 2026-07-01
tags: [backend, postgres]
---

# Postgres for the backend store

## Context
The leaderboard and accounts need concurrent writes and point-in-time backups.

## Decision
Postgres, managed, one instance per region.

## Reasons
Concurrent writers, mature backups, materialized views for the leaderboard.

## Rejected alternatives
- SQLite: one writer at a time.
- A document store: no joins for the reports we already run.

## Consequences
Schema migrations live in `backend/Db/Migrations/`.
