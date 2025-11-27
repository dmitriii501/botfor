from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard():
    """Главная клавиатура"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📝 Начать заполнение анкеты"))
    builder.add(KeyboardButton(text="📋 Моя анкета"))
    builder.add(KeyboardButton(text="❌ Отменить"))
    return builder.as_markup(resize_keyboard=True)


def get_section_keyboard():
    """Клавиатура выбора раздела"""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="1️⃣ Личные данные", callback_data="section_1"))
    builder.add(InlineKeyboardButton(text="2️⃣ Паспортные данные", callback_data="section_2"))
    builder.add(InlineKeyboardButton(text="3️⃣ Контактная информация", callback_data="section_3"))
    builder.add(InlineKeyboardButton(text="4️⃣ Документы", callback_data="section_4"))
    builder.add(InlineKeyboardButton(text="5️⃣ Готовность к работе", callback_data="section_5"))
    builder.add(InlineKeyboardButton(text="6️⃣ Согласия", callback_data="section_6"))
    builder.add(InlineKeyboardButton(text="7️⃣ Комментарии", callback_data="section_7"))
    builder.add(InlineKeyboardButton(text="✅ Завершить анкету", callback_data="finish_form"))
    builder.adjust(1)
    return builder.as_markup()


def get_citizenship_keyboard():
    """Клавиатура выбора гражданства"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🇷🇺 Гражданин России"))
    builder.add(KeyboardButton(text="🌍 Иностранный гражданин"))
    return builder.as_markup(resize_keyboard=True)


def get_yes_no_keyboard():
    """Клавиатура Да/Нет"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Да"))
    builder.add(KeyboardButton(text="❌ Нет"))
    builder.add(KeyboardButton(text="⏪ Назад"))
    return builder.as_markup(resize_keyboard=True)


def get_gender_keyboard():
    """Клавиатура выбора пола"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="👨 Мужской"))
    builder.add(KeyboardButton(text="👩 Женский"))
    builder.add(KeyboardButton(text="⏪ Назад"))
    return builder.as_markup(resize_keyboard=True)


def get_add_more_keyboard():
    """Клавиатура для добавления еще одного блока"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="➕ Добавить еще"))
    builder.add(KeyboardButton(text="➡️ Продолжить"))
    builder.add(KeyboardButton(text="⏪ Назад"))
    return builder.as_markup(resize_keyboard=True)


def get_skip_keyboard():
    """Клавиатура с возможностью пропустить"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⏭️ Пропустить"))
    builder.add(KeyboardButton(text="⏪ Назад"))
    return builder.as_markup(resize_keyboard=True)


def get_final_confirmation_keyboard():
    """Клавиатура финального подтверждения"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="✅ Подтвердить и отправить"))
    builder.add(KeyboardButton(text="✏️ Редактировать"))
    builder.add(KeyboardButton(text="❌ Отменить"))
    return builder.as_markup(resize_keyboard=True)

