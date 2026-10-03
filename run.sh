#!/usr/bin/env bash
set -e

echo "=========================================================="
echo "Starting Loan Approval Prediction System"
echo "=========================================================="
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment (.venv)..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "[INFO] Installing dependencies..."
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

echo "[INFO] Starting web application at http://127.0.0.1:5000 ..."
python3 app.py
