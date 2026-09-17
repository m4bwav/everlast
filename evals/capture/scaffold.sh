#!/bin/sh
# Seeds the empty eval workspace: a git repo registered with everlast in mode repo, with a workspace-local vault
# (.everlast-vault, which everlast.py picks up from the working directory) so the run never touches the real vault.
set -e
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$CASE_DIR/../.." && pwd)"
if command -v py >/dev/null 2>&1; then PY="py -3"; elif command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
git init -q .
printf 'hello\n' > README.md
git add -A && git -c user.email=eval@example.com -c user.name=eval commit -q -m init
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" vault init --owner eval >/dev/null
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" project register . --mode repo >/dev/null
printf '.everlast-vault/\n' >> .gitignore
cp "$PLUGIN/templates/AGENTS.md.snippet" AGENTS.md
printf 'Plugin scripts: %s/scripts/everlast.py\n' "$PLUGIN" > .everlast-plugin-path
ls ai-docs
