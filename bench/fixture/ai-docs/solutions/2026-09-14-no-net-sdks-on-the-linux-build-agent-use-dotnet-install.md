---
title: "No .NET SDKs on the Linux build agent: use dotnet-install"
kind: solution
status: active
date: 2026-09-14
verified: 2026-09-14
tags: [dotnet, ci, backend]
supersedes: solutions/2026-05-10-dotnet-test-says-no-net-sdks-were-found.md
---

# No .NET SDKs on the Linux build agent: use dotnet-install

## Problem
After the CI move from the Windows agent to Linux runners, `dotnet test` failed again with "No .NET SDKs were found". The earlier winget fix does not exist on Linux.

## Dead ends
- The distribution package `dotnet-sdk-9.0` installed an SDK the runner image then shadowed with its own runtime-only copy.

## Fix
Install the SDK per job with the official script, pinned: `curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 9.0 --install-dir $HOME/.dotnet`, then put `$HOME/.dotnet` first on PATH in `.ci/test.yml`.

## Verified by
`dotnet --list-sdks` printed `9.0.317 [/home/runner/.dotnet/sdk]`; the test job passed in 2 min 40 s.

## Applies when
Linux CI runners; Windows developer machines still use the installer.

Related: supersedes [dotnet test says no .NET SDKs were found](2026-05-10-dotnet-test-says-no-net-sdks-were-found.md)
