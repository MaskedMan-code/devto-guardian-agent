#!/bin/bash
set -e

if command -v coral >/dev/null 2>&1; then
  coral source add --file coral/devto_guardian_connector.yaml || true
fi

PORT="${PORT:-8080}"
python -m streamlit run app.py --server.address 0.0.0.0 --server.port "$PORT" --server.headless true
