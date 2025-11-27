import os
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import FormStates
from keyboards import (
    get_section_keyboard, get_yes_no_keyboard, get_gender_keyboard,
    get_add_more_keyboard, get_skip_keyboard, get_final_confirmation_keyboard,
    get_main_keyboard, get_citizenship_keyboard
)
from utils import save_form_data, load_form_data, format_form_preview
from database import init_database
from config import PHOTOS_DIR, DOCUMENTS_DIR
from game_utils import calculate_progress, get_motivational_message, get_section_emoji, get_completion_message


async def save_form_auto(message: Message, state: FSMContext):
    """Автоматически сохраняет форму в БД"""
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if form_data:
        user_id = message.from_user.id
        save_form_data(user_id, form_data, save_to_sheets=False)
    
async def save_form_auto_callback(callback: CallbackQuery, state: FSMContext):
    """Автоматически сохраняет форму в БД из callback"""
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if form_data:
        user_id = callback.from_user.id
        save_form_data(user_id, form_data, save_to_sheets=False)


# ========== ОБРАБОТЧИКИ НАЧАЛА РАБОТЫ ==========

async def start_form(message: Message, state: FSMContext):
    """Начало заполнения анкеты"""
    init_database()
    
    # Загружаем существующую анкету из БД, если есть
    user_id = message.from_user.id
    existing_data = load_form_data(user_id)
    
    if existing_data:
        await state.update_data(form_data=existing_data)
        percentage, progress_bar = calculate_progress(existing_data)
        await message.answer(
            "📝 Продолжение заполнения анкеты\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}\n\n"
            "Выберите раздел, который хотите заполнить или продолжить:",
            reply_markup=get_section_keyboard()
        )
    else:
        await state.clear()
        await state.update_data(form_data={})
        percentage, progress_bar = calculate_progress({})
        await message.answer(
            "📝 Заполнение анкеты\n\n"
            f"📊 Прогресс: {progress_bar} 0%\n"
            f"{get_motivational_message(0)}\n\n"
            "Выберите раздел, который хотите заполнить:",
            reply_markup=get_section_keyboard()
        )


async def show_my_form(message: Message, state: FSMContext):
    """Показать текущую анкету"""
    data = await state.get_data()
    if not data.get("form_data"):
        data = load_form_data(message.from_user.id)
        if not data:
            await message.answer("❌ Анкета еще не заполнена. Начните заполнение.")
            return
    else:
        data = data.get("form_data", {})
    
    percentage, progress_bar = calculate_progress(data)
    preview = format_form_preview(data)
    await message.answer(
        f"📊 Прогресс заполнения: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}\n\n{preview}",
        reply_markup=get_section_keyboard()
    )


async def cancel_form(message: Message, state: FSMContext):
    """Отмена заполнения анкеты"""
    await state.clear()
    await message.answer(
        "❌ Заполнение анкеты отменено.",
        reply_markup=get_main_keyboard()
    )


# ========== ОБРАБОТЧИКИ ВЫБОРА РАЗДЕЛОВ ==========

async def section_1_personal_data(callback: CallbackQuery, state: FSMContext):
    """Раздел 1: Личные данные"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_surname)
    await callback.message.answer(
        f"{get_section_emoji(1)} Раздел 1: Личные данные\n\n"
        "Начнем с основных данных. Пожалуйста, введите вашу фамилию:",
        reply_markup=get_skip_keyboard()
    )


async def section_2_passport(callback: CallbackQuery, state: FSMContext):
    """Раздел 2: Паспортные данные"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_passport_series_number)
    await callback.message.answer(
        f"{get_section_emoji(2)} Раздел 2: Паспортные данные\n\n"
        "Переходим к паспортным данным. Введите серию и номер паспорта (например: 1234 567890):",
        reply_markup=get_skip_keyboard()
    )


async def section_3_contacts(callback: CallbackQuery, state: FSMContext):
    """Раздел 3: Контактная информация"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_phone)
    await callback.message.answer(
        f"{get_section_emoji(3)} Раздел 3: Контактная информация\n\n"
        "Укажите контактные данные для связи. Введите мобильный телефон (например: +7 900 123 45 67):",
        reply_markup=get_skip_keyboard()
    )


async def section_4_documents(callback: CallbackQuery, state: FSMContext):
    """Раздел 4: Документы"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    citizenship_type = form_data.get("citizenship_type", "")
    
    await state.set_state(FormStates.waiting_for_medical_book)
    await callback.message.answer(
        f"{get_section_emoji(4)} Раздел 4: Документы\n\n"
        "Проверим наличие необходимых документов. Есть ли у вас медицинская книжка?",
        reply_markup=get_yes_no_keyboard()
    )


async def section_5_readiness(callback: CallbackQuery, state: FSMContext):
    """Раздел 5: Готовность к работе"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_vakhta_start_date)
    await callback.message.answer(
        f"{get_section_emoji(5)} Раздел 5: Готовность к работе\n\n"
        "Когда вы готовы начать вахту? (укажите дату или примерный период):",
        reply_markup=get_skip_keyboard()
    )


async def section_6_consents(callback: CallbackQuery, state: FSMContext):
    """Раздел 6: Согласия"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_personal_data_consent)
    await callback.message.answer(
        f"{get_section_emoji(6)} Раздел 6: Согласия\n\n"
        "Необходимо ваше согласие на обработку данных. Согласны ли вы на обработку персональных данных?",
        reply_markup=get_yes_no_keyboard()
    )


async def section_7_comments(callback: CallbackQuery, state: FSMContext):
    """Раздел 7: Комментарии"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    citizenship_type = form_data.get("citizenship_type", "")
    
    # Если иностранец, сначала показываем подтверждения
    if citizenship_type == "Иностранец":
        await state.set_state(FormStates.waiting_for_tuberculosis_confirmation)
        await callback.message.answer(
            f"{get_section_emoji(7)} Раздел 7: Подтверждения (для иностранных граждан)\n\n"
            "Требуется подтверждение важных сведений. Подтверждаете ли вы, что у вас нет таких заболеваний как туберкулез, сифилис, ВИЧ?",
            reply_markup=get_yes_no_keyboard()
        )
    else:
        await state.set_state(FormStates.waiting_for_comments)
        await callback.message.answer(
            f"{get_section_emoji(7)} Раздел 7: Комментарии / вопросы\n\n"
            "Если у вас есть дополнительные комментарии или вопросы, укажите их здесь (необязательно):",
            reply_markup=get_skip_keyboard()
        )


async def finish_form_handler(callback: CallbackQuery, state: FSMContext):
    """Завершение анкеты"""
    await callback.answer()
    
    # Загружаем данные из state или из БД
    data = await state.get_data()
    form_data = data.get("form_data", {})
    
    # Если в state нет данных, загружаем из БД
    if not form_data:
        user_id = callback.from_user.id
        form_data = load_form_data(user_id)
        if form_data:
            await state.update_data(form_data=form_data)
    
    if not form_data:
        await callback.message.answer("❌ Анкета пуста. Заполните хотя бы один раздел.")
        return
    
    preview = format_form_preview(form_data)
    await state.set_state(FormStates.waiting_for_final_confirmation)
    await callback.message.answer(
        preview + "\n\nПодтвердите отправку анкеты:",
        reply_markup=get_final_confirmation_keyboard()
    )


# ========== РАЗДЕЛ 1: ЛИЧНЫЕ ДАННЫЕ ==========

async def process_surname(message: Message, state: FSMContext):
    """Обработка фамилии"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите имя:")
        await state.set_state(FormStates.waiting_for_name)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "personal_data" not in form_data:
        form_data["personal_data"] = {}
    form_data["personal_data"]["surname"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_name)
    await message.answer("Введите имя:", reply_markup=get_skip_keyboard())


async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите отчество:")
        await state.set_state(FormStates.waiting_for_patronymic)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["name"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_patronymic)
    await message.answer("Введите отчество:", reply_markup=get_skip_keyboard())


async def process_patronymic(message: Message, state: FSMContext):
    """Обработка отчества"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите дату рождения (ДД.ММ.ГГГГ):")
        await state.set_state(FormStates.waiting_for_birth_date)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["patronymic"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_birth_date)
    await message.answer("Введите дату рождения (ДД.ММ.ГГГГ):", reply_markup=get_skip_keyboard())


async def process_birth_date(message: Message, state: FSMContext):
    """Обработка даты рождения"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите место рождения:")
        await state.set_state(FormStates.waiting_for_birth_place)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["birth_date"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_birth_place)
    await message.answer("Введите место рождения:", reply_markup=get_skip_keyboard())


async def process_birth_place(message: Message, state: FSMContext):
    """Обработка места рождения"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите гражданство:")
        await state.set_state(FormStates.waiting_for_citizenship)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["birth_place"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_citizenship)
    await message.answer("Введите гражданство:", reply_markup=get_skip_keyboard())


async def process_citizenship(message: Message, state: FSMContext):
    """Обработка гражданства"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Выберите пол:")
        await state.set_state(FormStates.waiting_for_gender)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["citizenship"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_gender)
    await message.answer("Выберите пол:", reply_markup=get_gender_keyboard())


async def process_gender(message: Message, state: FSMContext):
    """Обработка пола"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_citizenship)
        await message.answer("Введите гражданство:")
        return
    
    gender = "Мужской" if "Мужской" in message.text else "Женский" if "Женский" in message.text else message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["gender"] = gender
    await state.update_data(form_data=form_data)
    
    # Сохраняем в БД
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Личные данные')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
        reply_markup=get_section_keyboard()
    )


async def process_photo_3x4(message: Message, state: FSMContext):
    """Обработка фото 3x4"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        # Сохраняем в БД
        user_id = message.from_user.id
        save_form_data(user_id, form_data, save_to_sheets=False)
        
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Личные данные')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )
        # НЕ очищаем state, чтобы данные остались доступны
        return
    
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото.")
        return
    
    # Сохраняем фото
    photo = message.photo[-1]
    user_id = message.from_user.id
    user_photos_dir = os.path.join(PHOTOS_DIR, str(user_id))
    os.makedirs(user_photos_dir, exist_ok=True)
    
    file_path = os.path.join(user_photos_dir, "photo_3x4.jpg")
    file = await message.bot.get_file(photo.file_id)
    await message.bot.download_file(file.file_path, file_path)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["personal_data"]["photo_3x4"] = file_path
    await state.update_data(form_data=form_data)
    
    # Сохраняем в БД
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"✅ Фото сохранено!\n"
        f"{get_completion_message('Личные данные')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
        reply_markup=get_section_keyboard()
    )
    # НЕ очищаем state, чтобы данные остались доступны для финального подтверждения


# ========== РАЗДЕЛ 2: ПАСПОРТНЫЕ ДАННЫЕ ==========

async def process_passport_series_number(message: Message, state: FSMContext):
    """Обработка серии и номера паспорта"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите кем выдан паспорт:")
        await state.set_state(FormStates.waiting_for_passport_issued_by)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "passport_data" not in form_data:
        form_data["passport_data"] = {}
    form_data["passport_data"]["series_number"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_passport_issued_by)
    await message.answer("Введите кем выдан паспорт:", reply_markup=get_skip_keyboard())


async def process_passport_issued_by(message: Message, state: FSMContext):
    """Обработка кем выдан паспорт"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите дату выдачи (ДД.ММ.ГГГГ):")
        await state.set_state(FormStates.waiting_for_passport_issue_date)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["issued_by"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_passport_issue_date)
    await message.answer("Введите дату выдачи (ДД.ММ.ГГГГ):", reply_markup=get_skip_keyboard())


async def process_passport_issue_date(message: Message, state: FSMContext):
    """Обработка даты выдачи паспорта"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите код подразделения:")
        await state.set_state(FormStates.waiting_for_passport_division_code)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["issue_date"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_passport_division_code)
    await message.answer("Введите код подразделения:", reply_markup=get_skip_keyboard())


async def process_passport_division_code(message: Message, state: FSMContext):
    """Обработка кода подразделения"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите адрес регистрации:")
        await state.set_state(FormStates.waiting_for_registration_address)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["division_code"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_registration_address)
    await message.answer("Введите адрес регистрации:", reply_markup=get_skip_keyboard())


async def process_registration_address(message: Message, state: FSMContext):
    """Обработка адреса регистрации"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите фактический адрес проживания:")
        await state.set_state(FormStates.waiting_for_actual_address)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["registration_address"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_actual_address)
    await message.answer("Введите фактический адрес проживания:", reply_markup=get_skip_keyboard())


async def process_actual_address(message: Message, state: FSMContext):
    """Обработка фактического адреса"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите дополнительно (СНИЛС, ИНН, Грин-карта):")
        await state.set_state(FormStates.waiting_for_additional_docs)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["actual_address"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_additional_docs)
    await message.answer("Введите дополнительно (СНИЛС, ИНН, Грин-карта):", reply_markup=get_skip_keyboard())


async def process_additional_docs(message: Message, state: FSMContext):
    """Обработка дополнительных документов"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Загрузите фото паспорта (отправьте фото):")
        await state.set_state(FormStates.waiting_for_passport_photo)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["additional"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_passport_photo)
    await message.answer("Загрузите фото паспорта (отправьте фото):", reply_markup=get_skip_keyboard())


async def process_passport_photo(message: Message, state: FSMContext):
    """Обработка фото паспорта"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Паспортные данные')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )
        return
    
    if not message.photo:
        await message.answer("❌ Пожалуйста, отправьте фото.")
        return
    
    # Сохраняем фото
    photo = message.photo[-1]
    user_id = message.from_user.id
    user_photos_dir = os.path.join(PHOTOS_DIR, str(user_id))
    os.makedirs(user_photos_dir, exist_ok=True)
    
    file_path = os.path.join(user_photos_dir, "passport_photo.jpg")
    file = await message.bot.get_file(photo.file_id)
    await message.bot.download_file(file.file_path, file_path)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["passport_data"]["photo"] = file_path
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"✅ Фото сохранено!\n"
        f"{get_completion_message('Паспортные данные')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )


# ========== РАЗДЕЛ 3: КОНТАКТНАЯ ИНФОРМАЦИЯ ==========

async def process_phone(message: Message, state: FSMContext):
    """Обработка телефона"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Выберите ваше гражданство:")
        await state.set_state(FormStates.waiting_for_citizenship_choice)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "contacts" not in form_data:
        form_data["contacts"] = {}
    form_data["contacts"]["phone"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_citizenship_choice)
    await message.answer(
        "Выберите ваше гражданство:",
        reply_markup=get_citizenship_keyboard()
    )


async def process_citizenship_choice(message: Message, state: FSMContext):
    """Обработка выбора гражданства"""
    if "России" in message.text or "Россия" in message.text:
        citizenship_type = "Россия"
    elif "Иностранный" in message.text:
        citizenship_type = "Иностранец"
    else:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "citizenship_type" not in form_data:
        form_data["citizenship_type"] = citizenship_type
    else:
        form_data["citizenship_type"] = citizenship_type
    await state.update_data(form_data=form_data)
    
    # Сохраняем в БД
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"✅ Гражданство выбрано: {citizenship_type}\n\n"
        f"{get_completion_message('Контактная информация')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
        reply_markup=get_section_keyboard()
    )


# ========== РАЗДЕЛ 4: ДОКУМЕНТЫ И РАЗРЕШЕНИЯ ==========

async def process_medical_book(message: Message, state: FSMContext):
    """Обработка медицинской книжки"""
    if message.text == "⏪ Назад":
        await state.clear()
        await message.answer("Выберите раздел:", reply_markup=get_section_keyboard())
        return
    
    has_medical_book = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "documents" not in form_data:
        form_data["documents"] = {}
    form_data["documents"]["medical_book"] = has_medical_book
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_registration)
    await message.answer(
        "Есть ли у вас регистрация по месту пребывания?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_registration(message: Message, state: FSMContext):
    """Обработка регистрации"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_medical_book)
        await message.answer("Есть ли у вас медицинская книжка?", reply_markup=get_yes_no_keyboard())
        return
    
    has_registration = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    citizenship_type = form_data.get("citizenship_type", "")
    form_data["documents"]["registration"] = has_registration
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_snils)
    await message.answer("Введите СНИЛС:", reply_markup=get_skip_keyboard())


async def process_snils(message: Message, state: FSMContext):
    """Обработка СНИЛС"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите ИНН:")
        await state.set_state(FormStates.waiting_for_inn)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["snils"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_inn)
    await message.answer("Введите ИНН:", reply_markup=get_skip_keyboard())


async def process_inn(message: Message, state: FSMContext):
    """Обработка ИНН"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        citizenship_type = form_data.get("citizenship_type", "")
        
        # Если иностранец, спрашиваем ID
        if citizenship_type == "Иностранец":
            await state.set_state(FormStates.waiting_for_foreigner_id)
            await message.answer("Введите ID (для иностранных граждан):", reply_markup=get_skip_keyboard())
        else:
            # Для граждан РФ переходим к загрузке медкнижки
            await state.set_state(FormStates.waiting_for_medical_book_file)
            await message.answer(
                "Загрузите медицинскую книжку (отправьте файл или фото):",
                reply_markup=get_skip_keyboard()
            )
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    citizenship_type = form_data.get("citizenship_type", "")
    form_data["documents"]["inn"] = message.text
    await state.update_data(form_data=form_data)
    
    # Если иностранец, спрашиваем ID
    if citizenship_type == "Иностранец":
        await state.set_state(FormStates.waiting_for_foreigner_id)
        await message.answer("Введите ID (для иностранных граждан):", reply_markup=get_skip_keyboard())
    else:
        # Для граждан РФ переходим к загрузке медкнижки
        await state.set_state(FormStates.waiting_for_medical_book_file)
        await message.answer(
            "Загрузите медицинскую книжку (отправьте файл или фото):",
            reply_markup=get_skip_keyboard()
        )


async def process_foreigner_id(message: Message, state: FSMContext):
    """Обработка ID для иностранцев"""
    if message.text == "⏭️ Пропустить":
        await state.set_state(FormStates.waiting_for_fingerprinting)
        await message.answer("Прошли ли вы дактилоскопию?", reply_markup=get_yes_no_keyboard())
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "documents" not in form_data:
        form_data["documents"] = {}
    form_data["documents"]["foreigner_id"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_fingerprinting)
    await message.answer("Прошли ли вы дактилоскопию?", reply_markup=get_yes_no_keyboard())


async def process_fingerprinting(message: Message, state: FSMContext):
    """Обработка дактилоскопии"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_foreigner_id)
        await message.answer("Введите ID:")
        return
    
    has_fingerprinting = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["fingerprinting"] = has_fingerprinting
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_medical_exam_dactyloscopy)
    await message.answer(
        "Проходили ли вы медосмотр по дактилоскопии?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_medical_exam_dactyloscopy(message: Message, state: FSMContext):
    """Обработка медосмотра по дактилоскопии"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_fingerprinting)
        await message.answer("Прошли ли вы дактилоскопию?", reply_markup=get_yes_no_keyboard())
        return
    
    has_exam = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["medical_exam_dactyloscopy"] = has_exam
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_mvd_registry_check)
    await message.answer(
        "Проверили ли вы себя в Реестре контролируемых лиц МВД? (https://мвд.рф/rkl)",
        reply_markup=get_yes_no_keyboard()
    )


async def process_mvd_registry_check(message: Message, state: FSMContext):
    """Обработка проверки в реестре МВД"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_medical_exam_dactyloscopy)
        await message.answer("Проходили ли вы медосмотр по дактилоскопии?", reply_markup=get_yes_no_keyboard())
        return
    
    checked = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["mvd_registry_check"] = checked
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_medical_book_file)
    await message.answer(
        "Загрузите медицинскую книжку (отправьте файл или фото):",
        reply_markup=get_skip_keyboard()
    )


async def process_medical_book_file(message: Message, state: FSMContext):
    """Обработка файла медицинской книжки"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        user_id = message.from_user.id
        save_form_data(user_id, form_data, save_to_sheets=False)
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Документы')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )
        return
    
    if not (message.photo or message.document):
        await message.answer("❌ Пожалуйста, отправьте файл или фото.")
        return
    
    # Сохраняем файл
    user_id = message.from_user.id
    user_docs_dir = os.path.join(DOCUMENTS_DIR, str(user_id))
    os.makedirs(user_docs_dir, exist_ok=True)
    
    if message.photo:
        photo = message.photo[-1]
        file_path = os.path.join(user_docs_dir, "medical_book.jpg")
        file = await message.bot.get_file(photo.file_id)
    else:
        file_path = os.path.join(user_docs_dir, f"medical_book_{message.document.file_name}")
        file = await message.bot.get_file(message.document.file_id)
    
    await message.bot.download_file(file.file_path, file_path)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "files" not in form_data["documents"]:
        form_data["documents"]["files"] = {}
    form_data["documents"]["files"]["medical_book"] = file_path
    await state.update_data(form_data=form_data)
    
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"✅ Файл сохранен!\n"
        f"{get_completion_message('Документы')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
        reply_markup=get_section_keyboard()
    )


# ========== РАЗДЕЛ 5: ГОТОВНОСТЬ К РАБОТЕ ==========

async def process_vakhta_start_date(message: Message, state: FSMContext):
    """Обработка даты начала вахты"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Готовы ли вы к командировкам / вахте?")
        await state.set_state(FormStates.waiting_for_business_trips)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "readiness" not in form_data:
        form_data["readiness"] = {}
    form_data["readiness"]["vakhta_start_date"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_business_trips)
    await message.answer(
        "Готовы ли вы к командировкам / вахте?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_business_trips(message: Message, state: FSMContext):
    """Обработка готовности к командировкам"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_vakhta_start_date)
        await message.answer("Когда вы готовы начать вахту?")
        return
    
    ready = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "readiness" not in form_data:
        form_data["readiness"] = {}
    form_data["readiness"]["business_trips"] = ready
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_city)
    await message.answer("Введите город проживания:", reply_markup=get_skip_keyboard())


async def process_city(message: Message, state: FSMContext):
    """Обработка города проживания"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        user_id = message.from_user.id
        save_form_data(user_id, form_data, save_to_sheets=False)
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Готовность к работе')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "readiness" not in form_data:
        form_data["readiness"] = {}
    form_data["readiness"]["city"] = message.text
    await state.update_data(form_data=form_data)
    
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Готовность к работе')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
        reply_markup=get_section_keyboard()
    )


# ========== РАЗДЕЛ 8: СОГЛАСИЯ ==========

async def process_personal_data_consent(message: Message, state: FSMContext):
    """Обработка согласия на обработку персональных данных"""
    if message.text == "⏪ Назад":
        await state.clear()
        await message.answer("Выберите раздел:", reply_markup=get_section_keyboard())
        return
    
    consented = "Да" in message.text
    
    if not consented:
        await message.answer("❌ Для продолжения необходимо дать согласие на обработку персональных данных.")
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "consents" not in form_data:
        form_data["consents"] = {}
    form_data["consents"]["personal_data"] = True
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_rotation_consent)
    await message.answer(
        "Готовы ли вы к выезду и проживанию на вахте?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_rotation_consent(message: Message, state: FSMContext):
    """Обработка разрешения на вахту"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_personal_data_consent)
        await message.answer("Согласны ли вы на обработку персональных данных?", reply_markup=get_yes_no_keyboard())
        return
    
    consented = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["consents"]["rotation"] = consented
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Согласия')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )


# ========== РАЗДЕЛ 9: ПОДТВЕРЖДЕНИЯ ==========

async def process_tuberculosis_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения об отсутствии заболеваний"""
    if message.text == "⏪ Назад":
        await state.clear()
        await message.answer("Выберите раздел:", reply_markup=get_section_keyboard())
        return
    
    confirmed = "Да" in message.text
    
    if not confirmed:
        await message.answer("❌ Для продолжения необходимо подтвердить отсутствие заболеваний.")
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["tuberculosis"] = True
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_chronic_diseases_confirmation)
    await message.answer(
        "Подтверждаете ли вы, что у вас нет хронических заболеваний, мешающих работать на производстве?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_chronic_diseases_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения об отсутствии хронических заболеваний"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_tuberculosis_confirmation)
        await message.answer("Подтверждаете ли вы, что у вас нет таких заболеваний как туберкулез, сифилис, ВИЧ?", reply_markup=get_yes_no_keyboard())
        return
    
    confirmed = "Да" in message.text
    
    if not confirmed:
        await message.answer("❌ Для продолжения необходимо подтвердить отсутствие хронических заболеваний.")
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["chronic_diseases"] = True
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_russia_stay_confirmation)
    await message.answer(
        "Подтверждаете ли вы, что в этом году находились в России менее 2 месяцев без оформления разрешающих документов?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_russia_stay_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения о пребывании в России"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_chronic_diseases_confirmation)
        await message.answer("Подтверждаете ли вы, что у вас нет хронических заболеваний?", reply_markup=get_yes_no_keyboard())
        return
    
    confirmed = "Да" in message.text
    
    if not confirmed:
        await message.answer("❌ Для продолжения необходимо подтвердить, что вы не находились в России более 2 месяцев без оформления документов.")
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["russia_stay"] = False  # НЕТ - не находились более 2 месяцев
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_90_days_warning_confirmation)
    await message.answer(
        "Подтверждаете ли вы, что вас предупредили, что в России можно находиться без разрешающих документов в течение года только 90 дней?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_90_days_warning_confirmation(message: Message, state: FSMContext):
    """Обработка подтверждения о предупреждении"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_russia_stay_confirmation)
        await message.answer("Подтверждаете ли вы, что в этом году находились в России менее 2 месяцев?", reply_markup=get_yes_no_keyboard())
        return
    
    confirmed = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["90_days_warning"] = confirmed
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_documents_readiness)
    await message.answer(
        "Готовы ли вы оформить разрешительные документы для работы в РФ (ИНН, СНИЛС, дактилоскопия, медицина, российский номер)?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_documents_readiness(message: Message, state: FSMContext):
    """Обработка готовности оформить документы"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_90_days_warning_confirmation)
        await message.answer("Подтверждаете ли вы, что вас предупредили о 90 днях?", reply_markup=get_yes_no_keyboard())
        return
    
    ready = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["documents_readiness"] = ready
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_self_employment_consent)
    await message.answer(
        "Согласны ли вы получать выплаты по системе самозанятости?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_self_employment_consent(message: Message, state: FSMContext):
    """Обработка согласия на самозанятость"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_documents_readiness)
        await message.answer("Готовы ли вы оформить разрешительные документы?", reply_markup=get_yes_no_keyboard())
        return
    
    consented = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["self_employment"] = consented
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_compensation_consent)
    await message.answer(
        "Согласны ли вы компенсировать все затраты, связанные с вашей доставкой и оформлением в России при досрочном расторжении договора?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_compensation_consent(message: Message, state: FSMContext):
    """Обработка согласия на компенсацию"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_self_employment_consent)
        await message.answer("Согласны ли вы получать выплаты по системе самозанятости?", reply_markup=get_yes_no_keyboard())
        return
    
    consented = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "confirmations" not in form_data:
        form_data["confirmations"] = {}
    form_data["confirmations"]["compensation"] = consented
    await state.update_data(form_data=form_data)
    
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Подтверждения')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
        reply_markup=get_section_keyboard()
    )


# ========== РАЗДЕЛ 10: КОММЕНТАРИИ ==========

async def process_comments(message: Message, state: FSMContext):
    """Обработка комментариев"""
    data = await state.get_data()
    form_data = data.get("form_data", {})
    citizenship_type = form_data.get("citizenship_type", "")
    
    if message.text == "⏭️ Пропустить":
        form_data["comments"] = ""
    else:
        form_data["comments"] = message.text
    await state.update_data(form_data=form_data)
    
    user_id = message.from_user.id
    save_form_data(user_id, form_data, save_to_sheets=False)
    
    # Если иностранец, переходим к подтверждениям
    if citizenship_type == "Иностранец":
        await state.set_state(FormStates.waiting_for_tuberculosis_confirmation)
        await message.answer(
            "Требуется подтверждение важных сведений. Подтверждаете ли вы, что у вас нет таких заболеваний как туберкулез, сифилис, ВИЧ?",
            reply_markup=get_yes_no_keyboard()
        )
    else:
        # Для граждан РФ завершаем
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Комментарии')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )


# ========== ФИНАЛЬНОЕ ПОДТВЕРЖДЕНИЕ ==========

async def process_final_confirmation(message: Message, state: FSMContext):
    """Обработка финального подтверждения"""
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("Анкета отменена.", reply_markup=get_main_keyboard())
        return
    
    if message.text == "✏️ Редактировать":
        await message.answer("Выберите раздел для редактирования:", reply_markup=get_section_keyboard())
        await state.clear()
        return
    
    if "✅ Подтвердить" in message.text:
        data = await state.get_data()
        form_data = data.get("form_data", {})
        
        # Если в state нет данных, загружаем из БД
        if not form_data:
            user_id = message.from_user.id
            form_data = load_form_data(user_id)
        
        if not form_data:
            await message.answer("❌ Ошибка: не удалось загрузить данные анкеты.")
            return
        
        # Сохраняем данные в БД и отправляем в Google Sheets
        user_id = message.from_user.id
        save_form_data(user_id, form_data, save_to_sheets=True)
        
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            "✅ Анкета заполнена. Мы свяжемся с вами.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()
        return


# ========== РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ==========

def register_form_handlers(dp: Dispatcher):
    # Команды
    dp.message.register(start_form, F.text == "📝 Начать заполнение анкеты")
    dp.message.register(show_my_form, F.text == "📋 Моя анкета")
    dp.message.register(cancel_form, F.text == "❌ Отменить")
    dp.message.register(cancel_form, Command("cancel"))
    
    # Callback для разделов
    dp.callback_query.register(section_1_personal_data, F.data == "section_1")
    dp.callback_query.register(section_2_passport, F.data == "section_2")
    dp.callback_query.register(section_3_contacts, F.data == "section_3")
    dp.callback_query.register(section_4_documents, F.data == "section_4")
    dp.callback_query.register(section_5_readiness, F.data == "section_5")
    dp.callback_query.register(section_6_consents, F.data == "section_6")
    dp.callback_query.register(section_7_comments, F.data == "section_7")
    dp.callback_query.register(finish_form_handler, F.data == "finish_form")
    
    # Раздел 1: Личные данные
    dp.message.register(process_surname, FormStates.waiting_for_surname)
    dp.message.register(process_name, FormStates.waiting_for_name)
    dp.message.register(process_patronymic, FormStates.waiting_for_patronymic)
    dp.message.register(process_birth_date, FormStates.waiting_for_birth_date)
    dp.message.register(process_birth_place, FormStates.waiting_for_birth_place)
    dp.message.register(process_citizenship, FormStates.waiting_for_citizenship)
    dp.message.register(process_gender, FormStates.waiting_for_gender)
    
    # Выбор гражданства
    dp.message.register(process_citizenship_choice, FormStates.waiting_for_citizenship_choice)
    
    # Раздел 2: Паспортные данные
    dp.message.register(process_passport_series_number, FormStates.waiting_for_passport_series_number)
    dp.message.register(process_passport_issued_by, FormStates.waiting_for_passport_issued_by)
    dp.message.register(process_passport_issue_date, FormStates.waiting_for_passport_issue_date)
    dp.message.register(process_passport_division_code, FormStates.waiting_for_passport_division_code)
    dp.message.register(process_registration_address, FormStates.waiting_for_registration_address)
    dp.message.register(process_actual_address, FormStates.waiting_for_actual_address)
    dp.message.register(process_additional_docs, FormStates.waiting_for_additional_docs)
    dp.message.register(process_passport_photo, FormStates.waiting_for_passport_photo)
    
    # Раздел 3: Контактная информация
    dp.message.register(process_phone, FormStates.waiting_for_phone)
    
    # Раздел 4: Документы
    dp.message.register(process_medical_book, FormStates.waiting_for_medical_book)
    dp.message.register(process_registration, FormStates.waiting_for_registration)
    dp.message.register(process_snils, FormStates.waiting_for_snils)
    dp.message.register(process_inn, FormStates.waiting_for_inn)
    dp.message.register(process_foreigner_id, FormStates.waiting_for_foreigner_id)
    dp.message.register(process_fingerprinting, FormStates.waiting_for_fingerprinting)
    dp.message.register(process_medical_exam_dactyloscopy, FormStates.waiting_for_medical_exam_dactyloscopy)
    dp.message.register(process_mvd_registry_check, FormStates.waiting_for_mvd_registry_check)
    dp.message.register(process_medical_book_file, FormStates.waiting_for_medical_book_file)
    
    # Раздел 5: Готовность к работе
    dp.message.register(process_vakhta_start_date, FormStates.waiting_for_vakhta_start_date)
    dp.message.register(process_business_trips, FormStates.waiting_for_business_trips)
    dp.message.register(process_city, FormStates.waiting_for_city)
    
    # Раздел 6: Согласия
    dp.message.register(process_personal_data_consent, FormStates.waiting_for_personal_data_consent)
    dp.message.register(process_rotation_consent, FormStates.waiting_for_rotation_consent)
    
    # Раздел 7: Комментарии
    dp.message.register(process_comments, FormStates.waiting_for_comments)
    
    # Подтверждения (только для иностранцев)
    dp.message.register(process_tuberculosis_confirmation, FormStates.waiting_for_tuberculosis_confirmation)
    dp.message.register(process_chronic_diseases_confirmation, FormStates.waiting_for_chronic_diseases_confirmation)
    dp.message.register(process_russia_stay_confirmation, FormStates.waiting_for_russia_stay_confirmation)
    dp.message.register(process_90_days_warning_confirmation, FormStates.waiting_for_90_days_warning_confirmation)
    dp.message.register(process_documents_readiness, FormStates.waiting_for_documents_readiness)
    dp.message.register(process_self_employment_consent, FormStates.waiting_for_self_employment_consent)
    dp.message.register(process_compensation_consent, FormStates.waiting_for_compensation_consent)
    
    # Финальное подтверждение
    dp.message.register(process_final_confirmation, FormStates.waiting_for_final_confirmation)

