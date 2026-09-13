---
title: Privacy classification: rules first, ask when unsure
kind: decision
status: active
date: 2026-09-13
verified: 2026-09-13
tags: [privacy, scan]
---

# Privacy classification: rules first, ask when unsure

## Context
Entries about a project can name coworkers, internal hosts, credentials or opinions that must never reach a shared repository. Vendors redact only narrow token patterns.

## Decision
Rules first, ask when unsure: `protocol/PRIVACY.md` lists what is private by default; everlast.py runs a regex scan (emails, tokens, credential assignments, handles, phones, people by role, opinion words, plus the vault's redact list) at write time and in lint and scan; a repo-safe write that trips it is refused unless written --private or --allow-private (a recorded human decision). Borderline cases get one line of question; the default while waiting is private.

## Reasons
Asking every time is slow and gets ignored; fully automatic misses judgement calls. A written checklist plus a mechanical net catches the common leaks and leaves the rare judgement to the user. The redact list lives in the vault so the names themselves never sit in a public file.

## Rejected alternatives
- Ask every time: too slow for the end-of-session habit to survive.
- Fully automatic: no way to handle a public maintainer's name or a company blog tool name.

## Consequences
False positives (a public email in a docs link) need --allow-private. The scan is a net, not a judge; PRIVACY.md says so.
