#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$REPO_DIR/venv"

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Virtual environment not found in $VENV_DIR" >&2
  echo "Run scripts/setup-venv.sh before using this script." >&2
  exit 1
fi

SERVICE_NAME="${SERVICE_NAME:-telegram-anketa-bot.service}"

source "$VENV_DIR/bin/activate"

pip install --upgrade pip
pip install --upgrade -r "$REPO_DIR/requirements.txt"

deactivate

sudo systemctl restart "$SERVICE_NAME"

