---
title: CS0103 after renaming a UI method
kind: solution
status: active
date: 2026-09-06
verified: 2026-09-06
stale_after: 2026-12-05
tags: [unity, build, csharp]
aliases: ["error CS0103: The name 'ShowInventory' does not exist in the current context"]
summary: read when a Unity build fails with CS0103 after a rename
---

# CS0103 after renaming a UI method

## Problem
After renaming `ShowInventory` to `OpenInventory` in `Assets/Scripts/UI/HudController.cs`, the editor compiled but the Windows player build failed in `Assets/Scripts/UI/MenuBindings.cs` with CS0103.

## Dead ends
- Deleting `Library/` and reimporting: same error, 25 minutes lost.
- Suspected a stale assembly definition; the asmdef references were fine.

## Fix
`MenuBindings.cs` still called the old name inside an `#if UNITY_STANDALONE` block, which the editor never compiles. Rename the call there too, and search conditional code for the old name before building: `git grep -n ShowInventory`.

## Verified by
`Unity -batchmode -quit -buildTarget StandaloneWindows64 -executeMethod Build.Player` ended with `Build succeeded` (2026-09-06).

## Applies when
Renaming any method that platform-conditional code calls.
