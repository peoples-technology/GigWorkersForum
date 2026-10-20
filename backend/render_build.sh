#!/usr/bin/env bash
# Build script for Render backend service
set -euo pipefail

echo "=== Installing uv and syncing backend dependencies ==="
pip install --upgrade uv
uv sync

echo "=== Initializing schema and database seeds ==="
uv run python -m app.db.init_db

echo "=== Build finished successfully ==="
