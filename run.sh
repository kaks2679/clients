#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────
#  Client Hunter v2  –  Steve Kaks
#  Run this script to start the app on your local machine.
#
#  Usage:
#    chmod +x run.sh        (only needed once)
#    ./run.sh
#
#  Then open http://localhost:5000 in your browser.
# ──────────────────────────────────────────────────────────────────
set -e

PYTHON="python3"
PORT=5000

echo ""
echo "════════════════════════════════════════════"
echo "  🎯  CLIENT HUNTER v2  –  Steve Kaks"
echo "════════════════════════════════════════════"
echo ""

# ── Check Python ──────────────────────────────────────────────────
if ! command -v $PYTHON &>/dev/null; then
  echo "❌  python3 not found. Install Python 3.10+ from python.org"
  exit 1
fi
echo "✅  Python: $($PYTHON --version)"

# ── Create & activate virtual environment ─────────────────────────
if [ ! -d ".venv" ]; then
  echo "📦  Creating virtual environment…"
  $PYTHON -m venv .venv
fi
echo "✅  Activating virtual environment"
source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null

# ── Install dependencies ──────────────────────────────────────────
echo "📦  Installing dependencies…"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅  Dependencies installed"

# ── Create data directory ─────────────────────────────────────────
mkdir -p data
echo "✅  Data directory ready"

# ── Launch ────────────────────────────────────────────────────────
echo ""
echo "  🚀  Starting server on http://localhost:${PORT}"
echo "  ℹ️   Press Ctrl+C to stop"
echo ""
$PYTHON app.py
