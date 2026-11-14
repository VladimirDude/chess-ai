#!/usr/bin/env bash

cd "$(dirname "$0")" || exit 1

if [[ -x "venv/bin/python" ]]; then
    PYTHON="venv/bin/python"
elif [[ -x ".venv/bin/python" ]]; then
    PYTHON=".venv/bin/python"

elif [[ -f "venv/Scripts/python.exe" ]]; then
    PYTHON="venv/Scripts/python.exe"
elif [[ -f ".venv/Scripts/python.exe" ]]; then
    PYTHON=".venv/Scripts/python.exe"

elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    echo "python not found" >&2
    exit 1
fi

exec "$PYTHON" -u main.py 2>> stderr.log
