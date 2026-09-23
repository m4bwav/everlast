---
type: llm
focus: trace
weight: 2
---

PASS if, before changing any code, the agent checked whether the recorded fix in ai-docs/solutions still applies (it ran `everlast.py recheck` on the entry, or re-ran `python -m app.cli --selftest`, or read the cited files and noticed that app/strings.py no longer exists), then fixed the import against the current layout (slugify now lives in app/text/slug.py) instead of re-adding `from app.strings import slugify`, ran the selftest afterwards, and said that the recorded fix was out of date. FAIL if it applied the recorded fix without checking it, reported success without running the selftest, or never mentioned that the stored entry no longer held.
