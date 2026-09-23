---
title: Shader import hangs at Compiling variants
kind: solution
status: superseded
date: 2026-03-15
verified: 2026-03-15
tags: [unity, shaders]
superseded_by: solutions/2026-08-05-shader-variant-stripping-ends-the-import-hang.md
---

# Shader import hangs at Compiling variants

## Problem
Importing the water shader froze the editor at "Compiling variants" for over 40 minutes.

## Dead ends
- Restarting the editor.

## Fix
Delete `Library/ShaderCache` and reimport overnight.

## Verified by
The import finished after 41 minutes (2026-03-15).
