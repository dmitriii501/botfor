#!/usr/bin/env python3
"""Скрипт для проверки подключения к Google Sheets"""
import sys
import os

# Определяем корневую директорию проекта
REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_DIR = os.path.join(REPO_DIR, 'venv')

# Активируем виртуальное окружение если оно существует
if os.path.exists(VENV_DIR):
    venv_python = os.path.join(VENV_DIR, 'bin', 'python3')
    if os.path.exists(venv_python) and sys.executable != venv_python:
        # Перезапускаем скрипт с Python из venv
        os.execv(venv_python, [venv_python] + sys.argv)
    
    # Добавляем venv в путь для импортов
    import glob
    venv_site_packages = os.path.join(VENV_DIR, 'lib', 'python3.*', 'site-packages')
    site_packages = glob.glob(venv_site_packages)
    if site_packages:
        sys.path.insert(0, site_packages[0])

# Добавляем корневую директорию в путь
sys.path.insert(0, REPO_DIR)

# Меняем рабочую директорию на корневую
os.chdir(REPO_DIR)

from config import GOOGLE_SHEETS_ID
from google_sheets import get_sheets_client, get_service_account_email, get_headers

def check_google_sheets():
    """Проверяет подключение к Google Sheets"""
    print("=" * 60)
    print("Проверка подключения к Google Sheets")
    print("=" * 60)
    
    # Проверка GOOGLE_SHEETS_ID
    if not GOOGLE_SHEETS_ID:
        print("❌ ОШИБКА: GOOGLE_SHEETS_ID не установлен в .env файле")
        return False
    else:
        print(f"✅ GOOGLE_SHEETS_ID установлен: {GOOGLE_SHEETS_ID[:20]}...")
    
    # Проверка credentials.json
    creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials.json')
    if not os.path.exists(creds_path):
        print(f"❌ ОШИБКА: Файл credentials.json не найден: {creds_path}")
        return False
    else:
        print(f"✅ Файл credentials.json найден: {creds_path}")
    
    # Получение email сервисного аккаунта
    service_email = get_service_account_email()
    if service_email:
        print(f"✅ Email сервисного аккаунта: {service_email}")
    else:
        print("⚠️  Не удалось прочитать email сервисного аккаунта")
    
    # Проверка подключения
    try:
        print("\nПопытка подключения к Google Sheets API...")
        client = get_sheets_client()
        print("✅ Клиент Google Sheets успешно создан")
    except Exception as e:
        print(f"❌ ОШИБКА при создании клиента: {e}")
        return False
    
    # Проверка доступа к таблице
    try:
        print(f"\nПопытка открыть таблицу с ID: {GOOGLE_SHEETS_ID[:20]}...")
        spreadsheet = client.open_by_key(GOOGLE_SHEETS_ID)
        print(f"✅ Таблица успешно открыта: '{spreadsheet.title}'")
    except Exception as e:
        print(f"❌ ОШИБКА при открытии таблицы: {e}")
        print("\nВозможные причины:")
        print("1. Неправильный ID таблицы")
        print("2. Сервисный аккаунт не имеет доступа к таблице")
        if service_email:
            print(f"3. Поделитесь таблицей с: {service_email}")
        return False
    
    # Проверка листа "Анкеты"
    try:
        worksheet = spreadsheet.worksheet("Анкеты")
        print(f"✅ Лист 'Анкеты' найден")
        
        # Проверка заголовков
        headers = worksheet.row_values(1)
        if headers:
            print(f"✅ Заголовки найдены: {len(headers)} колонок")
            expected_headers = get_headers()
            if len(headers) == len(expected_headers):
                print("✅ Количество колонок соответствует ожидаемому")
            else:
                print(f"⚠️  Количество колонок не совпадает: ожидается {len(expected_headers)}, найдено {len(headers)}")
        else:
            print("⚠️  Заголовки не найдены, будут добавлены при следующей записи")
    except Exception as e:
        print(f"⚠️  Лист 'Анкеты' не найден: {e}")
        print("   Лист будет создан автоматически при следующей записи")
    
    # Тестовая запись (опционально)
    print("\n" + "=" * 60)
    print("✅ Все проверки пройдены успешно!")
    print("=" * 60)
    print(f"\nДля добавления доступа к таблице:")
    print(f"1. Откройте таблицу: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/edit")
    print(f"2. Нажмите 'Настройки доступа' (Share)")
    if service_email:
        print(f"3. Добавьте email: {service_email}")
        print(f"4. Дайте права: 'Редактор' (Editor)")
    
    return True

if __name__ == "__main__":
    success = check_google_sheets()
    sys.exit(0 if success else 1)

