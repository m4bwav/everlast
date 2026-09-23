#!/bin/sh
# A registered repo whose ai-docs hold a solution that was right on 2026-03-02 and is stale now: the code it cites
# moved on 2026-04-15 (app/strings.py is gone, slugify lives in app/text/slug.py), so reapplying the recorded fix
# ("re-export slugify from app.strings in app/helpers.py") would fail. INDEX.md shows it as (recheck due).
set -e
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$(cd "$CASE_DIR/../.." && pwd)"
if command -v py >/dev/null 2>&1; then PY="py -3"; elif command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
git init -q .
mkdir -p app
printf '' > app/__init__.py
printf 'import re\n\n\ndef slugify(text):\n    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")\n' > app/strings.py
printf 'from app.strings import slugify  # re-exported for app.cli\n\n\ndef title(text):\n    return text.strip().title()\n' > app/helpers.py
cat > app/cli.py <<'EOF'
import sys

from app.helpers import slugify


def main():
    if "--selftest" in sys.argv:
        assert slugify("Hello World") == "hello-world"
        print("selftest ok")


if __name__ == "__main__":
    main()
EOF
git add -A
GIT_AUTHOR_DATE="2026-03-01T10:00:00" GIT_COMMITTER_DATE="2026-03-01T10:00:00" git -c user.email=eval@example.com -c user.name=eval commit -q -m "cli selftest"
# 2026-04-15: slugify moves into a package; the re-export in helpers.py is dropped
mkdir -p app/text
printf '' > app/text/__init__.py
printf 'import re\n\n\ndef slugify(text):\n    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")\n' > app/text/slug.py
git rm -q app/strings.py
printf 'def title(text):\n    return text.strip().title()\n' > app/helpers.py
git add -A
GIT_AUTHOR_DATE="2026-04-15T10:00:00" GIT_COMMITTER_DATE="2026-04-15T10:00:00" git -c user.email=eval@example.com -c user.name=eval commit -q -m "move slugify to app/text/slug.py"
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" vault init --owner eval >/dev/null
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" project register . --mode repo --sync off >/dev/null
cat > ai-docs/solutions/2026-03-02-importerror-cannot-import-slugify-from-app-helpers.md <<'EOF'
---
title: ImportError cannot import slugify from app.helpers
kind: solution
status: active
date: 2026-03-02
verified: 2026-03-02
stale_after: 2026-05-31
tags: [python, imports, selftest]
aliases: ["ImportError: cannot import name 'slugify' from 'app.helpers'"]
summary: read when the selftest fails with an ImportError about slugify
---

# ImportError cannot import slugify from app.helpers

## Problem
`python -m app.cli --selftest` failed with "ImportError: cannot import name 'slugify' from 'app.helpers'" after a refactor removed the re-export.

## Dead ends
- Reinstalling the package: nothing is installed; the code runs from the tree.

## Fix
Re-export it in `app/helpers.py`: add `from app.strings import slugify` at the top. `app.cli` imports it from `app.helpers`.

## Verified by
`python -m app.cli --selftest` printed `selftest ok` (2026-03-02).

## Applies when
`app/strings.py` holds `slugify` and `app/cli.py` imports it from `app.helpers`.
EOF
printf '## [2026-03-02] add | solution: ImportError cannot import slugify from app.helpers\n' >> ai-docs/log.md
EVERLAST_VAULT="$PWD/.everlast-vault" $PY "$PLUGIN/scripts/everlast.py" index . >/dev/null
printf '.everlast-vault/\n__pycache__/\n' >> .gitignore
cp "$PLUGIN/templates/AGENTS.md.snippet" AGENTS.md
printf 'Plugin scripts: %s/scripts/everlast.py\n' "$PLUGIN" > .everlast-plugin-path
git add -A
GIT_AUTHOR_DATE="2026-04-16T10:00:00" GIT_COMMITTER_DATE="2026-04-16T10:00:00" git -c user.email=eval@example.com -c user.name=eval commit -q -m "docs"
grep -q "importerror-cannot-import-slugify-from-app-helpers.md) (recheck due)" ai-docs/INDEX.md
