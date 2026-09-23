---
title: Clone fails on Windows with Filename too long
kind: solution
status: active
date: 2026-06-11
verified: 2026-06-11
tags: [windows, git]
aliases: ["fatal: cannot create directory", "error: unable to create file"]
---

# Clone fails on Windows with Filename too long

## Problem
A fresh clone on a Windows build agent stopped with "error: unable to create file" for deep paths under `Assets/ThirdParty/`, followed by "Filename too long".

## Fix
Enable long paths for git and for Windows: `git config --system core.longpaths true`, and set `LongPathsEnabled` to 1 under `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem`.

## Verified by
The clone completed and `git status` was clean.
