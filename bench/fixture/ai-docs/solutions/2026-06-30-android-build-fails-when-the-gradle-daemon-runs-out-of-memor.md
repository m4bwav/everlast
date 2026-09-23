---
title: Android build fails when the Gradle daemon runs out of memory
kind: solution
status: active
date: 2026-06-30
verified: 2026-06-30
tags: [android, build, gradle]
aliases: [Gradle build daemon disappeared unexpectedly, "java.lang.OutOfMemoryError: Java heap space"]
---

# Android build fails when the Gradle daemon runs out of memory

## Problem
The Android player build failed after about 8 minutes with the Gradle daemon disappearing.

## Fix
Raise the daemon heap in `Assets/Plugins/Android/gradleTemplate.properties`: `org.gradle.jvmargs=-Xmx4g`.

## Verified by
The build succeeded in 11 minutes with a peak of 3.1 GB.
