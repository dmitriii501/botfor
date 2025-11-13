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
            worksheet = spreadsheet.sheet1  # Используем первый лист по умолчанию
        except:
            try:
                worksheet = spreadsheet.worksheet("Анкеты")
            except gspread.exceptions.WorksheetNotFound:
                worksheet = spreadsheet.add_worksheet(title="Анкеты", rows=1000, cols=100)
        
        # Подготавливаем данные для записи
        row_data = format_form_data_to_row(form_data, user_id)
        
        # Проверяем количество колонок
        if len(row_data) < 58:
            # Дополняем пустыми значениями до нужного количества
            row_data.extend([""] * (58 - len(row_data)))
        elif len(row_data) > 58:
            # Обрезаем до нужного количества
            row_data = row_data[:58]
        
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
    """Возвращает список заголовков для таблицы (соответствует структуре таблицы)"""
    return [
        "ID",
        "Дата након",
        "Товарищ ГЦ",
        "Фамилия",
        "Имя",
        "Отчество",
        "Дата рожд",
        "Место рож:",
        "Товарищ",
        "Пол",
        "Фото 3х4",
        "Серия и но",
        "Кем выдан",
        "Дата выдачи",
        "Код по адрес:",
        "Адрес реги",
        "Факт адрес",
        "Дополнит",
        "Фото лист",
        "Ме в связи",
        "Электронн",
        "Соцсети /",
        "Медцентр",
        "Разрешени Ре",
        "ы награды",
        "СИРОТС",
        "МИК",
        "Диагнозы",
        "Образовани",
        "Период об",
        "Специальн",
        "Документ с",
        "Должн:",
        "Отм: 1 —",
        "— и",
        "Отм: 1 —",
        "— и",
        "Отм: 1 —",
        "— и",
        "Отм: 2 —",
        "— и",
        "Отм: 2 —",
        "— и",
        "Отм: 2 —",
        "— и",
        "Федулиных",
        "Категории",
        "Пома видов:",
        "Медосмотр:",
        "Списки и",
        "Согласие и",
        "Подтвержд",
        "Подтвержд",
        "Подтвержд",
        "Предупрежд",
        "Готов сброс",
        "Согласие н. и.",
        "олинская",
        "Помощник арии / вопросы"
    ]


def format_form_data_to_row(form_data: dict, user_id: int) -> list:
    """Форматирует данные анкеты в строку для таблицы (соответствует структуре таблицы)"""
    row = []
    
    # ID
    row.append(str(user_id))
    
    # Дата након (дата заполнения)
    filled_at = form_data.get("filled_at", datetime.now().strftime("%d.%m.%Y"))
    row.append(filled_at)
    
    # Товарищ ГЦ (пусто)
    row.append("")
    
    # Личные данные
    pd = form_data.get("personal_data", {})
    row.extend([
        pd.get("surname", ""),
        pd.get("name", ""),
        pd.get("patronymic", ""),
        pd.get("birth_date", ""),
        pd.get("birth_place", ""),
        "",  # Товарищ (пусто)
        pd.get("gender", ""),
        "Да" if pd.get("photo_3x4") else "Нет"
    ])
    
    # Паспортные данные
    pass_data = form_data.get("passport_data", {})
    row.extend([
        pass_data.get("series_number", ""),
        pass_data.get("issued_by", ""),
        pass_data.get("issue_date", ""),
        pass_data.get("division_code", ""),
        pass_data.get("registration_address", ""),
        pass_data.get("actual_address", ""),
        pass_data.get("additional", ""),
        "Да" if pass_data.get("photo") else "Нет"
    ])
    
    # Контактная информация
    contacts = form_data.get("contacts", {})
    row.extend([
        contacts.get("phone", ""),
        contacts.get("email", ""),
        contacts.get("social_media", "")
    ])
    
    # Документы и разрешения
    docs = form_data.get("documents", {})
    files = docs.get("files", {})
    row.extend([
        "Да" if docs.get("medical_book") else "Нет",  # Медцентр
        "Да" if docs.get("work_permit") else "Нет",  # Разрешени Ре
        "Да" if docs.get("registration") else "Нет",  # ы награды (регистрация)
        docs.get("snils", ""),  # СИРОТС
        docs.get("inn", ""),  # МИК
        "Да" if docs.get("fingerprinting") else "Нет"  # Диагнозы (дактилоскопия)
    ])
    
    # Образование
    edu = form_data.get("education", {})
    row.extend([
        edu.get("institution", ""),
        edu.get("period", ""),
        edu.get("specialty", ""),
        edu.get("document", "")
    ])
    
    # Опыт работы - первое место (Должн:)
    work_exp = form_data.get("work_experience", [])
    if len(work_exp) > 0:
        work1 = work_exp[0]
        row.append(work1.get("position", ""))  # Должн: (32)
        # Отм: 1 — и (повторяется 4 раза для первого опыта)
        row.extend([
            work1.get("period", ""),  # Отм: 1 — (33)
            "",  # — и (34)
            work1.get("organization", ""),  # Отм: 1 — (35)
            "",  # — и (36)
            work1.get("duties", "")[:200] if work1.get("duties") else "",  # Отм: 1 — (37)
            ""  # — и (38)
        ])
    else:
        row.extend(["", "", "", "", "", "", ""])
    
    # Опыт работы - второе место (Отм: 2 — и, повторяется 4 раза)
    if len(work_exp) > 1:
        work2 = work_exp[1]
        row.extend([
            work2.get("period", ""),  # Отм: 2 — (39)
            "",  # — и (40)
            work2.get("organization", ""),  # Отм: 2 — (41)
            "",  # — и (42)
            work2.get("duties", "")[:200] if work2.get("duties") else "",  # Отм: 2 — (43)
            ""  # — и (44)
        ])
    else:
        row.extend(["", "", "", "", "", ""])
    
    # Дополнительно
    add = form_data.get("additional", {})
    row.extend([
        add.get("driver_categories", ""),  # Федулиных (категории ВУ)
        add.get("driver_categories", ""),  # Категории
        "Да" if add.get("business_trips") else "Нет",  # Пома видов: (готовность к командировкам)
        "Да" if add.get("medical_exam") else "Нет"  # Медосмотр:
    ])
    
    # Согласия
    cons = form_data.get("consents", {})
    row.extend([
        "Да" if cons.get("personal_data") else "Нет",  # Списки и
        "Да" if cons.get("rotation") else "Нет"  # Согласие и
    ])
    
    # Подтверждения
    conf = form_data.get("confirmations", {})
    row.extend([
        "Да" if conf.get("tuberculosis") else "Нет",  # Подтвержд 1
        "Да" if conf.get("chronic_diseases") else "Нет",  # Подтвержд 2
        "Да" if conf.get("russia_stay") else "Нет",  # Подтвержд 3
        "Да" if conf.get("90_days_warning") else "Нет",  # Предупрежд
        "Да" if conf.get("documents_readiness") else "Нет",  # Готов сброс
        "Да" if conf.get("self_employment") else "Нет",  # Согласие н. и. (самозанятость)
        "Да" if conf.get("compensation") else "Нет"  # олинская (компенсация)
    ])
    
    # Комментарии
    row.append(form_data.get("comments", ""))  # Помощник арии / вопросы
    
    return row

