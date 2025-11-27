"""Модуль для работы с Google Sheets"""
import gspread
import gspread.exceptions
from google.oauth2.service_account import Credentials
import os
from datetime import datetime


# Области доступа для Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


def get_sheets_client():
    """Создает и возвращает клиент для работы с Google Sheets"""
    creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    if not os.path.exists(creds_path):
        raise FileNotFoundError(f"Файл credentials.json не найден: {creds_path}")
    
    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client


def get_service_account_email():
    """Возвращает email сервисного аккаунта для предоставления доступа к таблице"""
    try:
        creds_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
        if not os.path.exists(creds_path):
            return None
        
        import json
        with open(creds_path, 'r', encoding='utf-8') as f:
            creds_data = json.load(f)
            return creds_data.get('client_email')
    except Exception as e:
        print(f"Ошибка при чтении credentials.json: {e}")
        return None


def save_form_to_sheets(spreadsheet_id: str, form_data: dict, user_id: int):
    """Сохраняет данные анкеты в Google Sheets таблицу"""
    try:
        if not spreadsheet_id:
            print("Ошибка: GOOGLE_SHEETS_ID не указан в .env файле")
            return False
        
        client = get_sheets_client()
        
        # Пробуем открыть таблицу по ID
        try:
            spreadsheet = client.open_by_key(spreadsheet_id)
        except gspread.exceptions.SpreadsheetNotFound:
            service_email = get_service_account_email()
            print(f"Ошибка: Таблица с ID '{spreadsheet_id}' не найдена.")
            print("\nПроверьте:")
            print("1. Правильность ID таблицы в .env файле (GOOGLE_SHEETS_ID)")
            print("   ID можно взять из URL таблицы: https://docs.google.com/spreadsheets/d/ID_ТАБЛИЦЫ/edit")
            if service_email:
                print(f"2. Поделитесь таблицей с сервисным аккаунтом: {service_email}")
                print("   (Права: Редактор или Редактор с комментариями)")
            else:
                print("2. Поделитесь таблицей с email сервисного аккаунта из credentials.json")
            return False
        except Exception as e:
            print(f"Ошибка при открытии таблицы: {e}")
            return False
        
        # Получаем первый лист (или лист "Анкеты" если есть)
        try:
            worksheet = spreadsheet.worksheet("Анкеты")
        except gspread.exceptions.WorksheetNotFound:
            try:
                worksheet = spreadsheet.sheet1  # Используем первый лист по умолчанию
                # Переименовываем первый лист
                worksheet.update_title("Анкеты")
            except:
                worksheet = spreadsheet.add_worksheet(title="Анкеты", rows=1000, cols=100)
        
        # Проверяем, есть ли заголовки. Если нет - добавляем
        try:
            headers = worksheet.row_values(1)
            if not headers or len(headers) == 0:
                # Добавляем заголовки
                headers_list = get_headers()
                worksheet.insert_row(headers_list, 1)
        except:
            # Если не удалось прочитать заголовки, добавляем их
            headers_list = get_headers()
            worksheet.insert_row(headers_list, 1)
        
        # Подготавливаем данные для записи
        row_data = format_form_data_to_row(form_data, user_id)
        
        # Проверяем количество колонок (14 полей согласно ТЗ)
        if len(row_data) < 14:
            # Дополняем пустыми значениями до нужного количества
            row_data.extend([""] * (14 - len(row_data)))
        elif len(row_data) > 14:
            # Обрезаем до нужного количества
            row_data = row_data[:14]
        
        # Добавляем строку в таблицу
        worksheet.append_row(row_data)
        
        print(f"Данные успешно записаны в Google Sheets для пользователя {user_id}")
        return True
    except gspread.exceptions.APIError as e:
        print(f"Ошибка API Google Sheets: {e}")
        print("Возможные причины:")
        print("1. Сервисный аккаунт не имеет доступа к таблице")
        print("2. Неправильный ID таблицы")
        print("3. Таблица была удалена или перемещена")
        return False
    except Exception as e:
        print(f"Ошибка при записи в Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        return False


def get_headers():
    """Возвращает список заголовков для таблицы (минимальные поля согласно ТЗ)"""
    return [
        "ID",
        "Дата заполнения",
        "ФИО",
        "Телефон",
        "Гражданство",
        "Ветка",
        "Город",
        "Когда готов начать",
        "Паспорт",
        "ID (иностранец)",
        "Проверка в реестре МВД",
        "Медосмотр/дактилоскопия",
        "Согласия",
        "Комментарии"
    ]


def format_form_data_to_row(form_data: dict, user_id: int) -> list:
    """Форматирует данные анкеты в строку для таблицы (минимальные поля согласно ТЗ)"""
    row = []
    
    # ID
    row.append(str(user_id))
    
    # Дата заполнения
    filled_at = form_data.get("filled_at", datetime.now().strftime("%d.%m.%Y"))
    if isinstance(filled_at, str) and "T" in filled_at:
        # Если ISO формат, конвертируем
        try:
            from datetime import datetime as dt
            dt_obj = dt.fromisoformat(filled_at.replace("Z", "+00:00"))
            filled_at = dt_obj.strftime("%d.%m.%Y")
        except:
            pass
    row.append(filled_at)
    
    # ФИО
    pd = form_data.get("personal_data", {})
    fio = f"{pd.get('surname', '')} {pd.get('name', '')} {pd.get('patronymic', '')}".strip()
    row.append(fio)
    
    # Телефон
    contacts = form_data.get("contacts", {})
    row.append(contacts.get("phone", ""))
    
    # Гражданство
    citizenship = pd.get("citizenship", "")
    row.append(citizenship)
    
    # Ветка (Россия или Иностранец)
    citizenship_type = form_data.get("citizenship_type", "")
    row.append(citizenship_type)
    
    # Город
    readiness = form_data.get("readiness", {})
    row.append(readiness.get("city", ""))
    
    # Когда готов начать
    row.append(readiness.get("vakhta_start_date", ""))
    
    # Паспорт
    pass_data = form_data.get("passport_data", {})
    passport = pass_data.get("series_number", "")
    row.append(passport)
    
    # ID (иностранец)
    docs = form_data.get("documents", {})
    foreigner_id = docs.get("foreigner_id", "") if citizenship_type == "Иностранец" else ""
    row.append(foreigner_id)
    
    # Проверка в реестре МВД
    mvd_check = "Да" if docs.get("mvd_registry_check") else "Нет" if citizenship_type == "Иностранец" else ""
    row.append(mvd_check)
    
    # Медосмотр/дактилоскопия
    fingerprinting = "Да" if docs.get("fingerprinting") else "Нет" if citizenship_type == "Иностранец" else ""
    medical_exam = "Да" if docs.get("medical_exam_dactyloscopy") else "Нет" if citizenship_type == "Иностранец" else ""
    med_info = f"Дактилоскопия: {fingerprinting}, Медосмотр: {medical_exam}" if citizenship_type == "Иностранец" else ""
    row.append(med_info)
    
    # Согласия
    cons = form_data.get("consents", {})
    consents_str = f"ПД: {'Да' if cons.get('personal_data') else 'Нет'}, Вахта: {'Да' if cons.get('rotation') else 'Нет'}"
    row.append(consents_str)
    
    # Комментарии
    row.append(form_data.get("comments", ""))
    
    return row

