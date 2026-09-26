#!/usr/bin/env bash
# Run the plugin eval suite under WSL2 (or any Linux or macOS shell), the way that grades correctly (TESTS.md harness notes).
# Usage, from PowerShell (Git Bash rewrites /mnt paths):  wsl bash /mnt/<drive>/<path>/everlast/scripts/eval-wsl.sh [RUN_NAME] [CASE ...]
#   RUN_NAME  results go to evals/results/<RUN_NAME>/ (gitignored); default: a timestamp
#   CASE      default: every case; read-only cases (resume) run without the tool grant (L-007)
# After the run: python scripts/eval_summary.py evals/results/<RUN_NAME>  (cost 0 means nothing ran: read the ERR lines, L-008)
set -u
# The Linux claude by path: a non-login shell under WSL finds the Windows claude.exe first, which cannot run the scaffolds (L-008).
CLAUDE="${CLAUDE:-$HOME/.local/bin/claude}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT" || exit 1
NAME="${1:-$(date -u +%Y-%m-%dT%H-%M-%SZ)}"
shift || true
CASES="${*:-resume privacy search recheck capture}"
READ_ONLY=" resume "
O="evals/results/$NAME"
mkdir -p "$O"
# --no-publish: the HTML report stays local (the default publishes it to claude.ai); --keep-temp keeps each run's workspace
# until WSL shuts down (/tmp is cleared then), for reading a failed run.
common=(--scaffold --trust-plugin --no-publish --keep-temp --judge-model sonnet -j 3)
for c in $CASES; do
  grant=(--allow-tools Bash Write Edit)
  case "$READ_ONLY" in *" $c "*) grant=() ;; esac
  "$CLAUDE" plugin eval . --case "$c" "${common[@]}" "${grant[@]}" --json "$O/$c.json" --report "$O/$c.html" > "$O/$c.log" 2>&1
  echo "$c exit $?"
done
echo "results: $O"
