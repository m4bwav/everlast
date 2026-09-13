---
description: End-of-task capture writes a solution entry through the script into the project's ai-docs
tags: [smoke, capture]
max_turns: 25
allowed_tools: [Read, Glob, Grep, Skill, Bash, Write]
---

We're done for today in this repo. Write down what we learned so the next session doesn't rediscover it: `dotnet test` failed with "no .NET SDKs were found". I first suspected PATH (it was fine) and then a stale global.json (there was none). The fix was installing the SDK with `winget install Microsoft.DotNet.SDK.9`; afterwards `dotnet --version` printed `9.0.317` and the 150 tests passed in about 9 seconds. Nothing is left unfinished.
