import json
import os
from datetime import datetime
from config import DATA_DIR, GOOGLE_SHEETS_ID
from google_sheets import save_form_to_sheets
from database import save_form_to_db, load_form_from_db, init_database


def save_form_data(user_id: int, data: dict, save_to_sheets: bool = False):
    """Сохраняет данные анкеты в базу данных и опционально в Google Sheets"""
    # Инициализируем БД если нужно
    init_database()
    
    # Добавляем дату заполнения
    if "filled_at" not in data:
        data["filled_at"] = datetime.now().isoformat()
    
    # Сохраняем в базу данных
    form_id = save_form_to_db(user_id, data)
    
    # Если нужно отправить в Google Sheets
    if save_to_sheets and GOOGLE_SHEETS_ID:
        try:
            success = save_form_to_sheets(GOOGLE_SHEETS_ID, data, user_id)
            if success:
                from database import mark_as_sent
                mark_as_sent(form_id)
        except Exception as e:
            print(f"Ошибка при сохранении в Google Sheets: {e}")
    
    return form_id


def load_form_data(user_id: int) -> dict:
    """Загружает данные анкеты пользователя из базы данных"""
    init_database()
    data = load_form_from_db(user_id)
    return data if data else {}


def format_form_preview(data: dict) -> str:
    """Форматирует данные анкеты для предпросмотра"""
    text = "📋 Предпросмотр анкеты:\n\n"
    
    # 1. Личные данные
    if data.get("personal_data"):
        pd = data["personal_data"]
        text += "1️⃣ Личные данные:\n"
        text += f"Фамилия: {pd.get('surname', 'Не указано')}\n"
        text += f"Имя: {pd.get('name', 'Не указано')}\n"
        text += f"Отчество: {pd.get('patronymic', 'Не указано')}\n"
        text += f"Дата рождения: {pd.get('birth_date', 'Не указано')}\n"
        text += f"Место рождения: {pd.get('birth_place', 'Не указано')}\n"
        text += f"Гражданство: {pd.get('citizenship', 'Не указано')}\n"
        text += f"Пол: {pd.get('gender', 'Не указано')}\n"
        text += f"Фото 3×4: {'✅ Загружено' if pd.get('photo_3x4') else '❌ Не загружено'}\n\n"
    
    # 2. Паспортные данные
    if data.get("passport_data"):
        pass_data = data["passport_data"]
        text += "2️⃣ Паспортные данные:\n"
        text += f"Серия и номер: {pass_data.get('series_number', 'Не указано')}\n"
        text += f"Кем выдан: {pass_data.get('issued_by', 'Не указано')}\n"
        text += f"Дата выдачи: {pass_data.get('issue_date', 'Не указано')}\n"
        text += f"Код подразделения: {pass_data.get('division_code', 'Не указано')}\n"
        text += f"Адрес регистрации: {pass_data.get('registration_address', 'Не указано')}\n"
        text += f"Фактический адрес: {pass_data.get('actual_address', 'Не указано')}\n"
        text += f"Дополнительно: {pass_data.get('additional', 'Не указано')}\n"
        text += f"Фото паспорта: {'✅ Загружено' if pass_data.get('photo') else '❌ Не загружено'}\n\n"
    
    # 3. Контактная информация
    if data.get("contacts"):
        contacts = data["contacts"]
        text += "3️⃣ Контактная информация:\n"
        text += f"Телефон: {contacts.get('phone', 'Не указано')}\n"
        text += f"Email: {contacts.get('email', 'Не указано')}\n"
        text += f"Соцсети: {contacts.get('social_media', 'Не указано')}\n\n"
    
    # 4. Документы и разрешения
    if data.get("documents"):
        docs = data["documents"]
        text += "4️⃣ Документы и разрешения:\n"
        text += f"Медкнижка: {'✅ Есть' if docs.get('medical_book') else '❌ Нет'}\n"
        text += f"Разрешение на работу: {'✅ Есть' if docs.get('work_permit') else '❌ Нет'}\n"
        text += f"Регистрация: {'✅ Да' if docs.get('registration') else '❌ Нет'}\n"
        text += f"СНИЛС: {docs.get('snils', 'Не указано')}\n"
        text += f"ИНН: {docs.get('inn', 'Не указано')}\n"
        text += f"Дактилоскопия: {'✅ Да' if docs.get('fingerprinting') else '❌ Нет'}\n\n"
    
    # 5. Образование
    if data.get("education"):
        edu = data["education"]
        text += "5️⃣ Образование:\n"
        text += f"Учебное заведение: {edu.get('institution', 'Не указано')}\n"
        text += f"Период обучения: {edu.get('period', 'Не указано')}\n"
        text += f"Специальность: {edu.get('specialty', 'Не указано')}\n"
        text += f"Документ: {edu.get('document', 'Не указано')}\n"
        text += f"Диплом: {'✅ Загружен' if edu.get('diploma_file') else '❌ Не загружен'}\n\n"
    
    # 6. Опыт работы
    if data.get("work_experience"):
        text += "6️⃣ Опыт работы:\n"
        for i, work in enumerate(data["work_experience"], 1):
            text += f"  Место {i}:\n"
            text += f"  Период: {work.get('period', 'Не указано')}\n"
            text += f"  Организация: {work.get('organization', 'Не указано')}\n"
            text += f"  Должность: {work.get('position', 'Не указано')}\n"
            text += f"  Обязанности: {work.get('duties', 'Не указано')[:50]}...\n"
        text += "\n"
    
    # 7. Дополнительно
    if data.get("additional"):
        add = data["additional"]
        text += "7️⃣ Дополнительно:\n"
        text += f"Водительское удостоверение: {'✅ Да' if add.get('driver_license') else '❌ Нет'}\n"
        if add.get('driver_categories'):
            text += f"Категории: {add.get('driver_categories')}\n"
        text += f"Готовность к командировкам: {'✅ Да' if add.get('business_trips') else '❌ Нет'}\n"
        text += f"Медосмотр: {'✅ Да' if add.get('medical_exam') else '❌ Нет'}\n\n"
    
    # 8. Согласия
    if data.get("consents"):
        cons = data["consents"]
        text += "8️⃣ Согласия:\n"
        text += f"Обработка ПД: {'✅ Да' if cons.get('personal_data') else '❌ Нет'}\n"
        text += f"Разрешение на вахту: {'✅ Да' if cons.get('rotation') else '❌ Нет'}\n\n"
    
    # 9. Подтверждения
    if data.get("confirmations"):
        conf = data["confirmations"]
        text += "9️⃣ Подтверждения:\n"
        text += f"Нет заболеваний: {'✅ Да' if conf.get('tuberculosis') else '❌ Нет'}\n"
        text += f"Нет хронических заболеваний: {'✅ Да' if conf.get('chronic_diseases') else '❌ Нет'}\n"
        text += f"Пребывание в РФ: {'✅ Да' if conf.get('russia_stay') else '❌ Нет'}\n"
        text += f"Предупреждение о 90 днях: {'✅ Да' if conf.get('90_days_warning') else '❌ Нет'}\n"
        text += f"Готовность оформить документы: {'✅ Да' if conf.get('documents_readiness') else '❌ Нет'}\n"
        text += f"Самозанятость: {'✅ Да' if conf.get('self_employment') else '❌ Нет'}\n"
        text += f"Компенсация затрат: {'✅ Да' if conf.get('compensation') else '❌ Нет'}\n\n"
    
    # 10. Комментарии
    if data.get("comments"):
        text += "💬 Комментарии:\n"
        text += f"{data.get('comments')[:200]}...\n\n"
    
    text += "\nИспользуйте кнопки ниже для редактирования или подтверждения."
    
    return text

