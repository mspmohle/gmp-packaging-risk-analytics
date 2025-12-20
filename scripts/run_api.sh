#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# run_api.sh — start the FastAPI service via uvicorn
#
# Usage:
#   ./scripts/run_api.sh
#   HOST=127.0.0.1 PORT=8001 ./scripts/run_api.sh
#   RELOAD=0 WORKERS=2 ./scripts/run_api.sh
# ------------------------------------------------------------

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
LOG_LEVEL="${LOG_LEVEL:-info}"

# Dev defaults
RELOAD="${RELOAD:-1}"          # 1 = reload on (dev), 0 = off (prod)
WORKERS="${WORKERS:-1}"        # keep 1 when reload is on

APP_IMPORT="${APP_IMPORT:-src.app.main:app}"

# Ensure imports resolve from repo root
export PYTHONPATH="${PYTHONPATH:-$REPO_ROOT}"

UVICORN_ARGS=( "$APP_IMPORT" "--host" "$HOST" "--port" "$PORT" "--log-level" "$LOG_LEVEL" )

if [[ "$RELOAD" == "1" ]]; then
  UVICORN_ARGS+=( "--reload" )
  # Uvicorn doesn't support multiple workers with --reload
  WORKERS="1"
fi

if [[ "$WORKERS" != "1" ]]; then
  UVICORN_ARGS+=( "--workers" "$WORKERS" )
fi

echo "Starting API:"
echo "  repo      : $REPO_ROOT"
echo "  app       : $APP_IMPORT"
echo "  host:port : $HOST:$PORT"
echo "  reload    : $RELOAD"
echo "  workers   : $WORKERS"
echo

exec uvicorn "${UVICORN_ARGS[@]}"

