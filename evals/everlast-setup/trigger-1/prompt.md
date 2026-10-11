---
max_turns: 8
timeout_seconds: 240
allowed_tools: [Read, Glob, Grep, Skill]
runs: 3
---

Set this repo up so the AI stops relearning the same things every session. Keep the always-loaded context small.

(For this run: start the job, and stop after the first two or three tool calls with a one-line note of which skill you invoked and what you would do next.)
