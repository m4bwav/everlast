#!/bin/sh
# Claude Code hooks for the Everlast Protocol. Fail-silent by design; never blocks a session.
#   SessionStart: one line of orientation (project mode, user tier, vault state) plus the project HANDOFF when it holds real content.
#   Stop:         once per session, when the working tree changed and no project doc was written in 8 h, block once with the capture checklist.
#   SessionEnd:   hand the vault commit + push to a detached process (SessionEnd hooks share a 1.5 s budget).
# The JSON payload on stdin passes straight through to everlast.py hook run.
# Windows (Git Bash): ${CLAUDE_PLUGIN_ROOT} may arrive with backslashes, and `python3` is often the Store stub.
self=$(printf '%s' "$0" | tr '\\' '/')
DIR="$(cd "$(dirname "$self")" && pwd)"
# A candidate counts only if it can run Python: the Windows Store stub and the macOS Command Line Tools stub are on
# PATH but fail (or pop a dialog) instead of running a script. The pinned launcher comes last, not first.
PY=""
case "$(uname -s 2>/dev/null)" in
  MINGW*|MSYS*|CYGWIN*) CANDS="python|python3|py -3" ;;
  *)                    CANDS="python3|python" ;;
esac
old_ifs=$IFS; IFS='|'
for c in $CANDS; do
  if $c -c "import sys" >/dev/null 2>&1; then PY=$c; break; fi
done
IFS=$old_ifs
[ -z "$PY" ] && exit 0
export PYTHONUTF8=1
if [ -n "$1" ]; then $PY "$DIR/everlast.py" hook run --event "$1" 2>/dev/null; else $PY "$DIR/everlast.py" hook run 2>/dev/null; fi
exit 0
