---
title: Audio crackles on Bluetooth headsets
kind: solution
status: active
date: 2026-07-19
verified: 2026-07-19
tags: [audio]
aliases: [AirPods static, earbuds popping]
---

# Audio crackles on Bluetooth headsets

## Problem
Players on wireless headsets heard crackle during busy scenes; wired headphones were fine.

## Dead ends
- Lowering the music bitrate.

## Fix
The DSP buffer was set to "Best latency" (256 samples), too small for Bluetooth. Set DSP Buffer Size to "Good latency" in `ProjectSettings/AudioManager.asset`.

## Verified by
A ten-minute listening test on two headsets with no crackle.
