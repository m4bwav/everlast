#!/bin/sh
# Claude Code hooks for the Everlast Protocol. Fail-silent by design; never blocks a session.
#   SessionStart: one line of orientation (project mode, user tier, vault state) plus the project HANDOFF when it holds real content.
#   Stop:         once per session, when the working tree changed and no project doc was written in 8 h, block once with the capture checklist.
#   SessionEnd:   hand the vault commit + push to a detached process (SessionEnd hooks share a 1.5 s budget).
# The JSON payload on stdin passes straight through to everlast.py hook run.
# Windows (Git Bash): ${CLAUDE_PLUGIN_ROOT} may arrive with backslashes, and `python3` is often the Store stub.
self=$(printf '%s' "$0" | tr '\\' '/')
DIR="$(cd "$(dirname "$self")" && pwd)"
PY=""
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*)
    if command -v py >/dev/null 2>&1; then PY="py -3"
    elif command -v python >/dev/null 2>&1; then PY=python
    elif command -v python3 >/dev/null 2>&1; then PY=python3
    fi ;;
  *)
    if command -v python3 >/dev/null 2>&1; then PY=python3
    elif command -v python >/dev/null 2>&1; then PY=python
    fi ;;
esac
[ -z "$PY" ] && exit 0
$PY "$DIR/everlast.py" hook run 2>/dev/null
exit 0
