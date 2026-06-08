#!/bin/bash
# Launch VN Stock Dashboard
# Usage: ./dashboard/run.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV="$PROJECT_ROOT/.venv"

# Activate venv
if [ -d "$VENV" ]; then
  source "$VENV/bin/activate"
else
  echo "❌ Virtual environment not found at $VENV"
  echo "Run: python3 -m venv .venv && source .venv/bin/activate && pip install fastapi uvicorn vnstock pandas"
  exit 1
fi

echo "🎩 VN Stock Dashboard — Buffett Analyzer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Open: http://localhost:8686"
echo "📊 Press Ctrl+C to stop"
echo ""

cd "$PROJECT_ROOT"
python dashboard/server.py
