#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Prefer a local venv if present (dev convenience)
if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

exec uvicorn src.app.main:app --reload --port 8000
