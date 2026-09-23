---
title: Steam overlay missing in development builds
kind: solution
status: active
date: 2026-09-10
verified: 2026-09-10
tags: [steam, build]
aliases: [SteamAPI_Init failed]
---

# Steam overlay missing in development builds

## Problem
Shift+Tab did nothing in development builds; release builds were fine.

## Fix
Development builds lacked `steam_appid.txt` beside the executable. A post-build step now copies `Build/steam_appid.txt` into the output folder (`Assets/Editor/PostBuildSteam.cs`).

## Verified by
The overlay opens with Shift+Tab in a development build.
