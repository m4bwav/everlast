---
title: Postgres connection refused inside docker compose
kind: solution
status: active
date: 2026-09-01
verified: 2026-09-01
tags: [docker, postgres, backend]
aliases: ["could not connect to server: Connection refused", ECONNREFUSED 127.0.0.1:5432]
summary: read when the API container cannot reach Postgres in compose
---

# Postgres connection refused inside docker compose

## Problem
The API container started, then logged that it could not reach the database; the database container itself was healthy.

## Dead ends
- Opening port 5432 on the host: irrelevant inside the compose network.

## Fix
Inside a container `localhost` is the container itself. Use the service name `db` as the host in `backend/appsettings.Development.json`, and start the API only after the database reports healthy (`depends_on` with `condition: service_healthy` in `docker-compose.yml`).

## Verified by
`docker compose up -d && curl -s localhost:8080/health` printed `{"db":"ok"}`.
