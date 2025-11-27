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

# Перезапуск сервиса
# Если sudo настроен через sudoers, будет работать без пароля
# Иначе нужно запускать скрипт от root или настроить sudoers
if sudo -n systemctl restart "$SERVICE_NAME" 2>/dev/null; then
  echo "Service $SERVICE_NAME restarted successfully"
else
  echo "Warning: Could not restart service automatically (may require password or sudoers configuration)"
  echo "Please run manually: sudo systemctl restart $SERVICE_NAME"
  exit 0  # Не считаем это критической ошибкой
fi

