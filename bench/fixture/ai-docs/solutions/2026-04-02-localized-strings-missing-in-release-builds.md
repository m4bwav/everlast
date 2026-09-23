---
title: Localized strings missing in release builds
kind: solution
status: active
date: 2026-04-02
verified: 2026-04-02
tags: [localization, unity, build]
---

# Localized strings missing in release builds

## Problem
Release builds showed the string keys instead of translated text; development builds were fine.

## Dead ends
- Rebuilding the string tables.

## Fix
The tables were not loaded before the first scene. Tick "Preload All Tables" in the Localization settings.

## Verified by
A release build shows the German text on the title screen.
