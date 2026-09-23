---
title: Flaky PlayMode test left Time.timeScale at zero
kind: solution
status: active
date: 2026-04-20
verified: 2026-04-20
tags: [unity, tests, ci]
---

# Flaky PlayMode test left Time.timeScale at zero

## Problem
On the CI server, every test that ran after `PauseMenuTests` timed out; locally the suite passed. The failure depended on test order.

## Dead ends
- Raising the test timeout to 180 s: the tests then hung for 180 s.

## Fix
The pause test set `Time.timeScale = 0` and never restored it. Restore it in a `[TearDown]` in `Assets/Tests/PlayMode/PauseMenuTests.cs`.

## Verified by
`Unity -batchmode -runTests -testPlatform PlayMode` reported 212 passed, 0 failed, in both orders.
