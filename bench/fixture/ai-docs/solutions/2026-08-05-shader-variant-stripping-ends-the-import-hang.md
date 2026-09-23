---
title: Shader variant stripping ends the import hang
kind: solution
status: active
date: 2026-08-05
verified: 2026-08-05
tags: [unity, shaders, performance]
supersedes: solutions/2026-03-15-shader-import-hangs-at-compiling-variants.md
---

# Shader variant stripping ends the import hang

## Problem
The water shader generated about 38,000 variants, so every import took most of an hour.

## Dead ends
- Clearing the shader cache (the old workaround): it only restarts the same compile.

## Fix
Replace `multi_compile` with `shader_feature` for the foam and caustics keywords, and strip unused variants in an `IPreprocessShaders` hook, `Assets/Editor/WaterVariantStripper.cs`.

## Verified by
The reimport took 45 s; the build log reported 412 variants.

Related: supersedes [Shader import hangs at Compiling variants](2026-03-15-shader-import-hangs-at-compiling-variants.md)
