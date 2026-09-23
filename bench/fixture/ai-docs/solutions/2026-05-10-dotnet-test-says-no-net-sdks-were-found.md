---
title: dotnet test says no .NET SDKs were found
kind: solution
status: superseded
date: 2026-05-10
verified: 2026-05-10
tags: [dotnet, build, backend]
aliases: [No .NET SDKs were found]
summary: read when dotnet test cannot find an SDK on a build machine
superseded_by: solutions/2026-09-14-no-net-sdks-on-the-linux-build-agent-use-dotnet-install.md
---

# dotnet test says no .NET SDKs were found

## Problem
`dotnet test backend/Tidewater.Api.Tests` stopped at "No .NET SDKs were found" on the Windows build agent, although `dotnet --info` ran.

## Dead ends
- PATH looked wrong; it held `C:\Program Files\dotnet` as expected.
- A global.json pin was the next suspect; the repository has none.

## Fix
Only the runtime was installed. Install the SDK: `winget install Microsoft.DotNet.SDK.9`.

## Verified by
`dotnet --list-sdks` printed `9.0.317`; `dotnet test` ran 148 tests in 11 s.

## Applies when
Windows agents provisioned with the runtime only.
