---
title: Relay server instead of Netcode for co-op
kind: decision
status: active
date: 2026-03-01
verified: 2026-03-01
tags: [multiplayer, networking]
---

# Relay server instead of Netcode for co-op

## Context
Two-player co-op over the internet without asking players to open ports.

## Decision
A small relay server of our own; clients send inputs, the host simulates.

## Reasons
Netcode for GameObjects (Unity's own package) needed its relay service and more setup than two players need.

## Rejected alternatives
- Peer to peer with NAT punch-through: fails on strict NATs.

## Consequences
We run one more service.
