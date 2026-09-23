#!/bin/sh
# A registered repo with seven entries. The one that answers the prompt has a vague title and tags ("Player build
# settings that matter", build-pipeline); only its alias and body name the error, so an index scan finds nothing and
# `everlast.py search` finds it.
set -e
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$CASE_DIR/../.." && pwd)"
if command -v py >/dev/null 2>&1; then PY="py -3"; elif command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
EV() { EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" "$@"; }
git init -q .
printf 'game\n' > README.md
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -q -m init
EV vault init --owner eval >/dev/null
EV project register . --mode repo --sync off >/dev/null
note() {  # kind title tags summary body
  printf '%s\n' "$5" > body.md
  EV note . --kind "$1" --title "$2" --tags "$3" --summary "$4" --body-file body.md --allow-missing >/dev/null
}
note solution "Player build settings that matter" "build-pipeline" "read before changing player build settings" "## Problem
Near the end of the Android player build the Gradle daemon died with java.lang.OutOfMemoryError: Java heap space.

## Fix
Raise the daemon heap in \`Assets/Plugins/Android/gradleTemplate.properties\`: \`org.gradle.jvmargs=-Xmx4g\`.

## Verified by
The Android build succeeded in 11 minutes with a peak of 3.1 GB."
note solution "CS0103 after renaming a UI method" "unity,csharp" "read when a build fails with CS0103 after a rename" "## Problem
CS0103 in the player build only.

## Fix
Rename the call inside the platform-conditional block too.

## Verified by
The Windows player build succeeded."
note solution "Addressables content build fails" "unity,addressables" "read when the content build stops without a stack trace" "## Problem
Unknown error in AsyncOperation.

## Fix
Remove the missing atlas from the UI group.

## Verified by
The content build succeeded."
note decision "Relay server instead of Netcode for co-op" "multiplayer" "read before changing the co-op networking" "## Context
Two-player co-op.

## Decision
Our own relay.

## Reasons
No port forwarding for players."
note decision "Target 60 fps on handhelds" "performance" "read before adding an expensive effect" "## Context
Frame spikes.

## Decision
A 16.6 ms budget at 800p.

## Reasons
Stable input."
note plan "Localization pass" "localization" "read when continuing the German and Japanese text" "## Goal
German and Japanese text.

## Status
German 80 percent.

## Next single action
Send the remaining strings."
note note "Asset naming conventions" "assets" "read before naming new art or audio files" "## Summary
Prefixes T_, M_, SFX_, MUS_.

## Details
No spaces."
rm body.md
# the Android entry also carries the error as an alias, as everlast-capture now asks
f=$(ls ai-docs/solutions/*player-build-settings-that-matter.md)
$PY - "$f" <<'EOF'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.replace("tags: [build-pipeline]\n", "tags: [build-pipeline]\naliases: [\"java.lang.OutOfMemoryError: Java heap space\", Gradle daemon disappeared]\n", 1)
open(p, "w", encoding="utf-8", newline="\n").write(s)
EOF
EV index . >/dev/null
printf '.everlast-vault/\n' >> .gitignore
cp "$PLUGIN/templates/AGENTS.md.snippet" AGENTS.md
printf 'Plugin scripts: %s/scripts/everlast.py\n' "$PLUGIN" > .everlast-plugin-path
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -q -m "docs"
if grep -qi "outofmemory\|heap" ai-docs/INDEX.md; then echo "the index must not name the error" >&2; exit 1; fi
