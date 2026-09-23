---
description: A stale solution covers the task; the agent checks it (recheck or its Verified-by command) before editing, does not reapply the old fix blindly, and records the outcome
tags: [check-before-use, recheck]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

`python -m app.cli --selftest` fails again with "ImportError: cannot import name 'slugify' from 'app.helpers'". We fixed this exact error before in this repo. Fix it so the selftest passes.
