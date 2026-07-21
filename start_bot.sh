#!/usr/bin/env bash
# === LMU Setup Bot launcher (Linux/macOS) ===
set -e
cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
    echo "[!] .env not found. Copy .env.example to .env and fill in BOT_TOKEN."
    exit 1
fi

if [ ! -f ".venv/bin/python" ]; then
    echo "[*] First run: creating a virtual environment and installing dependencies..."
    python3 -m venv .venv
    ".venv/bin/python" -m pip install --upgrade pip
    ".venv/bin/python" -m pip install -r requirements.txt
fi

echo "[*] Starting the bot... (Ctrl+C to stop)"
exec ".venv/bin/python" bot.py
