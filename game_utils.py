"""Игровые утилиты для бота"""


def calculate_progress(form_data: dict) -> tuple[int, str]:
    """Рассчитывает прогресс заполнения анкеты в процентах и возвращает прогресс-бар"""
    if not form_data:
        return 0, "░░░░░░░░░░"
    
    total_sections = 10
    completed_sections = 0
    
    # Проверяем каждый раздел более тщательно
    # 1. Личные данные - проверяем наличие хотя бы одного поля
    pd = form_data.get("personal_data", {})
    if pd and isinstance(pd, dict):
        if any([pd.get("surname"), pd.get("name"), pd.get("patronymic"), pd.get("birth_date"), pd.get("birth_place"), pd.get("citizenship"), pd.get("gender")]):
            completed_sections += 1
    
    # 2. Паспортные данные
    pass_data = form_data.get("passport_data", {})
    if pass_data and isinstance(pass_data, dict):
        if any([pass_data.get("series_number"), pass_data.get("issued_by"), pass_data.get("issue_date"), pass_data.get("division_code"), pass_data.get("registration_address")]):
            completed_sections += 1
    
    # 3. Контактная информация
    contacts = form_data.get("contacts", {})
    if contacts and isinstance(contacts, dict):
        if any([contacts.get("phone"), contacts.get("email"), contacts.get("social_media")]):
            completed_sections += 1
    
    # 4. Документы и разрешения
    docs = form_data.get("documents", {})
    if docs and isinstance(docs, dict):
        if any([docs.get("medical_book") is not None, docs.get("work_permit") is not None, docs.get("registration") is not None, docs.get("snils"), docs.get("inn"), docs.get("fingerprinting") is not None]):
            completed_sections += 1
    
    # 5. Образование
    edu = form_data.get("education", {})
    if edu and isinstance(edu, dict):
        if any([edu.get("institution"), edu.get("period"), edu.get("specialty"), edu.get("document")]):
            completed_sections += 1
    
    # 6. Опыт работы
    work_exp = form_data.get("work_experience", [])
    if work_exp and isinstance(work_exp, list) and len(work_exp) > 0:
        # Проверяем, что хотя бы один блок опыта работы заполнен
        if any([work.get("period") or work.get("organization") or work.get("position") for work in work_exp if isinstance(work, dict)]):
            completed_sections += 1
    
    # 7. Дополнительно
    add = form_data.get("additional", {})
    if add and isinstance(add, dict):
        if any([add.get("driver_license") is not None, add.get("driver_categories"), add.get("business_trips") is not None, add.get("medical_exam") is not None]):
            completed_sections += 1
    
    # 8. Согласия
    cons = form_data.get("consents", {})
    if cons and isinstance(cons, dict):
        if any([cons.get("personal_data") is not None, cons.get("rotation") is not None]):
            completed_sections += 1
    
    # 9. Подтверждения
    conf = form_data.get("confirmations", {})
    if conf and isinstance(conf, dict):
        if any([conf.get("tuberculosis") is not None, conf.get("chronic_diseases") is not None, conf.get("russia_stay") is not None, conf.get("90_days_warning") is not None, conf.get("documents_readiness") is not None, conf.get("self_employment") is not None, conf.get("compensation") is not None]):
            completed_sections += 1
    
    # 10. Комментарии (необязательный раздел, но считаем если есть)
    if form_data.get("comments"):
        completed_sections += 1
    
    percentage = int((completed_sections / total_sections) * 100)
    
    # Создаем прогресс-бар (максимум 10 символов)
    filled = min(completed_sections, 10)
    empty = max(0, 10 - filled)
    progress_bar = "█" * filled + "░" * empty
    
    return percentage, progress_bar


def get_motivational_message(percentage: int) -> str:
    """Возвращает мотивационное сообщение в зависимости от прогресса"""
    if percentage == 0:
        return "🎯 Начните заполнение анкеты — первый шаг к успеху!"
    elif percentage < 20:
        return "🌱 Отличное начало! Продолжайте в том же духе."
    elif percentage < 40:
        return "📈 Вы на правильном пути! Уже четверть пути пройдено."
    elif percentage < 60:
        return "💪 Половина работы уже сделана! Осталось совсем немного."
    elif percentage < 80:
        return "🚀 Отличный прогресс! Вы почти у цели."
    elif percentage < 100:
        return "✨ Финальный рывок! Осталось заполнить последние разделы."
    else:
        return "🎉 Поздравляем! Анкета полностью заполнена!"


def get_section_emoji(section_num: int) -> str:
    """Возвращает эмодзи для раздела"""
    emojis = {
        1: "👤",
        2: "📄",
        3: "📞",
        4: "📋",
        5: "🎓",
        6: "💼",
        7: "⭐",
        8: "✅",
        9: "🔒",
        10: "💬"
    }
    return emojis.get(section_num, "📝")


def get_completion_message(section_name: str) -> str:
    """Возвращает сообщение о завершении раздела"""
    messages = [
        f"✅ Раздел '{section_name}' успешно завершен!",
        f"🎯 Отлично! Раздел '{section_name}' заполнен.",
        f"✨ Раздел '{section_name}' готов. Продолжаем дальше!",
        f"🌟 Превосходно! Раздел '{section_name}' завершен.",
    ]
    import random
    return random.choice(messages)

