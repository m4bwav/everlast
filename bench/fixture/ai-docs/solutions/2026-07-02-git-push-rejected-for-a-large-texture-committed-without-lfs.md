---
title: Git push rejected for a large texture committed without LFS
kind: solution
status: active
date: 2026-07-02
verified: 2026-07-02
tags: [git, lfs, assets]
aliases: [this exceeds GitHub's file size limit of 100.00 MB, "GH001: Large files detected"]
---

# Git push rejected for a large texture committed without LFS

## Problem
Pushing the ocean branch failed: the remote said the file exceeds GitHub's file size limit of 100.00 MB. The texture had been committed before `.gitattributes` tracked `*.exr`.

## Dead ends
- `git lfs track "*.exr"` after the fact: tracks new files only; the old commit still carries the blob.

## Fix
Rewrite the branch so the blob moves into LFS: `git lfs migrate import --include="*.exr,*.psd" --include-ref=refs/heads/feature/ocean`, then push with `--force-with-lease`.

## Verified by
`git lfs ls-files` listed `Assets/Art/Ocean/foam_height.exr`; the push went through.
