---
type: regex
target:
  source: file
  path: app/helpers.py
pattern: 'app\.strings'
match: not_contains
weight: 2
---
