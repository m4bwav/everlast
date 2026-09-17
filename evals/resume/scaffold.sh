#!/bin/sh
# The capture workspace plus one existing solution about the dotnet SDK error and a real HANDOFF.
set -e
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$CASE_DIR/../.." && pwd)"
if command -v py >/dev/null 2>&1; then PY="py -3"; elif command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
sh "$CASE_DIR/../capture/scaffold.sh" >/dev/null
cat > body.md <<'EOF'
## Problem
`dotnet test` fails with "no .NET SDKs were found" even though Unity bundles an SDK.

## Dead ends
- PATH looked wrong; it was fine.
- A stale global.json; there was none.

## Fix
Install the SDK machine-wide: `winget install Microsoft.DotNet.SDK.9`.

## Verified by
`dotnet --version` printed `9.0.317`; `dotnet test` ran 150 tests in about 9 s.

## Applies when
Windows, .NET 9 projects. Unity's bundled SDK 8 is not on PATH by design.
EOF
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" note . --kind solution --title "dotnet test says no .NET SDKs were found" --tags dotnet,build --body-file body.md >/dev/null
rm body.md
cat > handoff.md <<'EOF'
# Handoff

## Current state
Build script `build.ps1` runs the tests after the SDK install.

## In progress
Nothing.

## Decisions made this session
None.

## Dead ends hit
None new.

## Next single action
Add a `--no-build` flag to `build.ps1`.
EOF
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" handoff . --body-file handoff.md >/dev/null
rm handoff.md
printf 'Write-Host "build"\n' > build.ps1
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -q -m "docs"
