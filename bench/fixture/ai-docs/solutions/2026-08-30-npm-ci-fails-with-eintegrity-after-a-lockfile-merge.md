---
title: npm ci fails with EINTEGRITY after a lockfile merge
kind: solution
status: active
date: 2026-08-30
verified: 2026-08-30
stale_after: 2026-09-20
tags: [node, npm, tools]
aliases: [npm ERR! code EINTEGRITY, sha512 integrity checksum failed]
---

# npm ci fails with EINTEGRITY after a lockfile merge

## Problem
In the level editor web tool (`tools/editor-web/`), `npm ci` failed with an integrity checksum error right after a merge.

## Dead ends
- `npm cache clean --force`: no change; the lockfile itself was wrong.

## Fix
The merge kept two different integrity hashes for the same package version. Regenerate the lockfile from the manifest: delete `package-lock.json`, run `npm install --package-lock-only`, commit.

## Verified by
`npm ci` exited 0 and `npm run build` produced `dist/`.
