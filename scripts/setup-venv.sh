#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$REPO_DIR/venv"

if [[ ! -x "$(command -v "$PYTHON_BIN")" ]]; then
  echo "Python interpreter '$PYTHON_BIN' not found. Set PYTHON_BIN to an existing python3 binary." >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install --upgrade -r "$REPO_DIR/requirements.txt"
deactivate

