#!/usr/bin/env bash
# ==============================================================================
# run.sh: Convenience script to run the service locally for testing
# ==============================================================================

set -e

# Find the directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Layer 4: Export assigned OS environment variables
export APP_PORT=8144
export APP_WORKERS=11

# Prefer the workspace virtual environment if available, otherwise fallback to system uvicorn
if [ -f "$DIR/../.venv/bin/uvicorn" ]; then
    "$DIR/../.venv/bin/uvicorn" main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
else
    uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --reload
fi
