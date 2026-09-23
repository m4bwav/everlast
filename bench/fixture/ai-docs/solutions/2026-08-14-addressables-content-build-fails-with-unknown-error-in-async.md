---
title: Addressables content build fails with Unknown error in AsyncOperation
kind: solution
status: active
date: 2026-08-14
verified: 2026-08-14
tags: [unity, addressables]
---

# Addressables content build fails with Unknown error in AsyncOperation

## Problem
The nightly content build stopped with "Unknown error in AsyncOperation" and no stack trace.

## Dead ends
- Clearing the build cache: same failure.
- Upgrading the package to the latest patch: same failure.

## Fix
A merge left the `UI` group pointing at a sprite atlas that had been deleted. Run the Analyze rule "Check Duplicate Bundle Dependencies", then remove the missing entry from `Assets/AddressableAssetsData/AssetGroups/UI.asset`.

## Verified by
`Unity -batchmode -quit -executeMethod Build.Content` logged `Addressable content build succeeded`.
