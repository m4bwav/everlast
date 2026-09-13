#!/bin/sh
# Same workspace as the capture case: a repo in mode repo with a workspace-local vault.
set -e
CASE_DIR="$(cd "$(dirname "$0")" && pwd)"
sh "$CASE_DIR/../capture/scaffold.sh"
