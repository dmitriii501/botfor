import os
from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import FormStates
from keyboards import (
    get_section_keyboard, get_yes_no_keyboard, get_gender_keyboard,
    get_add_more_keyboard, get_skip_keyboard, get_final_confirmation_keyboard,
    get_main_keyboard
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
    """Раздел 4: Документы и разрешения"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_medical_book)
    await callback.message.answer(
        f"{get_section_emoji(4)} Раздел 4: Документы и разрешения\n\n"
        "Проверим наличие необходимых документов. Есть ли у вас медицинская книжка?",
        reply_markup=get_yes_no_keyboard()
    )


async def section_5_education(callback: CallbackQuery, state: FSMContext):
    """Раздел 5: Образование"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_education_institution)
    await callback.message.answer(
        f"{get_section_emoji(5)} Раздел 5: Образование\n\n"
        "Укажите информацию об образовании. Введите название учебного заведения:",
        reply_markup=get_skip_keyboard()
    )


async def section_6_work_experience(callback: CallbackQuery, state: FSMContext):
    """Раздел 6: Опыт работы"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "work_experience" not in form_data:
        form_data["work_experience"] = []
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_work_period)
    await callback.message.answer(
        f"{get_section_emoji(6)} Раздел 6: Опыт работы\n\n"
        "Расскажите о вашем профессиональном опыте. Введите период работы (например: 01.2020 - 12.2023):",
        reply_markup=get_skip_keyboard()
    )


async def section_7_additional(callback: CallbackQuery, state: FSMContext):
    """Раздел 7: Дополнительно"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_driver_license)
    await callback.message.answer(
        f"{get_section_emoji(7)} Раздел 7: Дополнительно\n\n"
        "Уточним дополнительные сведения. Есть ли у вас водительское удостоверение?",
        reply_markup=get_yes_no_keyboard()
    )


async def section_8_consents(callback: CallbackQuery, state: FSMContext):
    """Раздел 8: Согласия"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_personal_data_consent)
    await callback.message.answer(
        f"{get_section_emoji(8)} Раздел 8: Согласия\n\n"
        "Необходимо ваше согласие на обработку данных. Согласны ли вы на обработку персональных данных?",
        reply_markup=get_yes_no_keyboard()
    )


async def section_9_confirmations(callback: CallbackQuery, state: FSMContext):
    """Раздел 9: Подтверждения"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_tuberculosis_confirmation)
    await callback.message.answer(
        f"{get_section_emoji(9)} Раздел 9: Подтверждения\n\n"
        "Требуется подтверждение важных сведений. Подтверждаете ли вы, что у вас нет таких заболеваний как туберкулез, сифилис, ВИЧ?",
        reply_markup=get_yes_no_keyboard()
    )


async def section_10_comments(callback: CallbackQuery, state: FSMContext):
    """Раздел 10: Комментарии"""
    await callback.answer()
    
    # Загружаем данные из БД, если есть
    user_id = callback.from_user.id
    existing_data = load_form_data(user_id)
    if existing_data:
        await state.update_data(form_data=existing_data)
    
    await state.set_state(FormStates.waiting_for_comments)
    await callback.message.answer(
        f"{get_section_emoji(10)} Раздел 10: Комментарии / вопросы\n\n"
        "Последний раздел. Если у вас есть дополнительные комментарии или вопросы, укажите их здесь (необязательно):",
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
    
    await state.set_state(FormStates.waiting_for_photo_3x4)
    await message.answer(
        "Загрузите фото 3×4 (отправьте фото):",
        reply_markup=get_skip_keyboard()
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
        await message.answer("Пропущено. Введите электронную почту:")
        await state.set_state(FormStates.waiting_for_email)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "contacts" not in form_data:
        form_data["contacts"] = {}
    form_data["contacts"]["phone"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_email)
    await message.answer("Введите электронную почту:", reply_markup=get_skip_keyboard())


async def process_email(message: Message, state: FSMContext):
    """Обработка email"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите соцсети / мессенджеры:")
        await state.set_state(FormStates.waiting_for_social_media)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["contacts"]["email"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_social_media)
    await message.answer("Введите соцсети / мессенджеры:", reply_markup=get_skip_keyboard())


async def process_social_media(message: Message, state: FSMContext):
    """Обработка соцсетей"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Контактная информация')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["contacts"]["social_media"] = message.text
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
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
    
    await state.set_state(FormStates.waiting_for_work_permit)
    await message.answer(
        "Есть ли у вас разрешение на работу (для иностранных граждан)?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_work_permit(message: Message, state: FSMContext):
    """Обработка разрешения на работу"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_medical_book)
        await message.answer("Есть ли у вас медицинская книжка?", reply_markup=get_yes_no_keyboard())
        return
    
    has_permit = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["work_permit"] = has_permit
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_registration)
    await message.answer(
        "Есть ли у вас регистрация по месту пребывания?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_registration(message: Message, state: FSMContext):
    """Обработка регистрации"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_work_permit)
        await message.answer("Есть ли у вас разрешение на работу?", reply_markup=get_yes_no_keyboard())
        return
    
    has_registration = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
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
        await message.answer("Пропущено. Прошли ли вы дактилоскопию?")
        await state.set_state(FormStates.waiting_for_fingerprinting)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["inn"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_fingerprinting)
    await message.answer("Прошли ли вы дактилоскопию?", reply_markup=get_yes_no_keyboard())


async def process_fingerprinting(message: Message, state: FSMContext):
    """Обработка дактилоскопии"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_inn)
        await message.answer("Введите ИНН:")
        return
    
    has_fingerprinting = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["documents"]["fingerprinting"] = has_fingerprinting
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_medical_book_file)
    await message.answer(
        "Загрузите медицинскую книжку (отправьте файл или фото):",
        reply_markup=get_skip_keyboard()
    )


async def process_medical_book_file(message: Message, state: FSMContext):
    """Обработка файла медицинской книжки"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Загрузите разрешение на работу (если есть):")
        await state.set_state(FormStates.waiting_for_work_permit_file)
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
    
    await state.set_state(FormStates.waiting_for_work_permit_file)
    await message.answer("Загрузите разрешение на работу (если есть):", reply_markup=get_skip_keyboard())


async def process_work_permit_file(message: Message, state: FSMContext):
    """Обработка файла разрешения на работу"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Документы и разрешения')}\n\n"
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
        file_path = os.path.join(user_docs_dir, "work_permit.jpg")
        file = await message.bot.get_file(photo.file_id)
    else:
        file_path = os.path.join(user_docs_dir, f"work_permit_{message.document.file_name}")
        file = await message.bot.get_file(message.document.file_id)
    
    await message.bot.download_file(file.file_path, file_path)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "files" not in form_data["documents"]:
        form_data["documents"]["files"] = {}
    form_data["documents"]["files"]["work_permit"] = file_path
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Документы и разрешения')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )


# ========== РАЗДЕЛ 5: ОБРАЗОВАНИЕ ==========

async def process_education_institution(message: Message, state: FSMContext):
    """Обработка учебного заведения"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите период обучения:")
        await state.set_state(FormStates.waiting_for_education_period)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "education" not in form_data:
        form_data["education"] = {}
    form_data["education"]["institution"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_education_period)
    await message.answer("Введите период обучения (например: 2015-2019):", reply_markup=get_skip_keyboard())


async def process_education_period(message: Message, state: FSMContext):
    """Обработка периода обучения"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите специальность / квалификацию:")
        await state.set_state(FormStates.waiting_for_education_specialty)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["education"]["period"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_education_specialty)
    await message.answer("Введите специальность / квалификацию:", reply_markup=get_skip_keyboard())


async def process_education_specialty(message: Message, state: FSMContext):
    """Обработка специальности"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите серию и номер документа об образовании:")
        await state.set_state(FormStates.waiting_for_education_document)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["education"]["specialty"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_education_document)
    await message.answer("Введите серию и номер документа об образовании:", reply_markup=get_skip_keyboard())


async def process_education_document(message: Message, state: FSMContext):
    """Обработка документа об образовании"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Загрузите диплом / аттестат (отправьте файл):")
        await state.set_state(FormStates.waiting_for_education_diploma)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["education"]["document"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_education_diploma)
    await message.answer("Загрузите диплом / аттестат (отправьте файл или фото):", reply_markup=get_skip_keyboard())


async def process_education_diploma(message: Message, state: FSMContext):
    """Обработка диплома/аттестата"""
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Образование')}\n\n"
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
        file_path = os.path.join(user_docs_dir, "diploma.jpg")
        file = await message.bot.get_file(photo.file_id)
    else:
        file_path = os.path.join(user_docs_dir, f"diploma_{message.document.file_name}")
        file = await message.bot.get_file(message.document.file_id)
    
    await message.bot.download_file(file.file_path, file_path)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["education"]["diploma_file"] = file_path
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Образование')}\n\n"
        f"📊 Прогресс: {progress_bar} {percentage}%\n"
        f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )


# ========== РАЗДЕЛ 6: ОПЫТ РАБОТЫ ==========

async def process_work_period(message: Message, state: FSMContext):
    """Обработка периода работы"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите название организации:")
        await state.set_state(FormStates.waiting_for_work_organization)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "work_experience" not in form_data:
        form_data["work_experience"] = []
    
    # Создаем новый блок опыта работы
    work_entry = {"period": message.text}
    form_data["work_experience"].append(work_entry)
    await state.update_data(form_data=form_data, current_work_index=len(form_data["work_experience"]) - 1)
    
    await state.set_state(FormStates.waiting_for_work_organization)
    await message.answer("Введите название организации:", reply_markup=get_skip_keyboard())


async def process_work_organization(message: Message, state: FSMContext):
    """Обработка организации"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите должность:")
        await state.set_state(FormStates.waiting_for_work_position)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    work_index = data.get("current_work_index", len(form_data["work_experience"]) - 1)
    form_data["work_experience"][work_index]["organization"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_work_position)
    await message.answer("Введите должность:", reply_markup=get_skip_keyboard())


async def process_work_position(message: Message, state: FSMContext):
    """Обработка должности"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Введите основные обязанности:")
        await state.set_state(FormStates.waiting_for_work_duties)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    work_index = data.get("current_work_index", len(form_data["work_experience"]) - 1)
    form_data["work_experience"][work_index]["position"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_work_duties)
    await message.answer("Введите основные обязанности (длинный текст):", reply_markup=get_skip_keyboard())


async def process_work_duties(message: Message, state: FSMContext):
    """Обработка обязанностей"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Добавить еще один блок опыта работы?")
        await state.set_state(FormStates.waiting_for_add_more_work)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    work_index = data.get("current_work_index", len(form_data["work_experience"]) - 1)
    form_data["work_experience"][work_index]["duties"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_add_more_work)
    await message.answer(
        "Добавить еще один блок опыта работы?",
        reply_markup=get_add_more_keyboard()
    )


async def process_add_more_work(message: Message, state: FSMContext):
    """Обработка добавления еще одного блока опыта"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_work_duties)
        await message.answer("Введите основные обязанности:")
        return
    
    if "➕ Добавить еще" in message.text:
        await state.set_state(FormStates.waiting_for_work_period)
        await message.answer("Введите период работы (например: 01.2020 - 12.2023):", reply_markup=get_skip_keyboard())
    else:
        data = await state.get_data()
        form_data = data.get("form_data", {})
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Опыт работы')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )


# ========== РАЗДЕЛ 7: ДОПОЛНИТЕЛЬНО ==========

async def process_driver_license(message: Message, state: FSMContext):
    """Обработка водительского удостоверения"""
    if message.text == "⏪ Назад":
        await state.clear()
        await message.answer("Выберите раздел:", reply_markup=get_section_keyboard())
        return
    
    has_license = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    if "additional" not in form_data:
        form_data["additional"] = {}
    form_data["additional"]["driver_license"] = has_license
    await state.update_data(form_data=form_data)
    
    if has_license:
        await state.set_state(FormStates.waiting_for_driver_categories)
        await message.answer("Введите категории водительского удостоверения:", reply_markup=get_skip_keyboard())
    else:
        await state.set_state(FormStates.waiting_for_business_trips)
        await message.answer(
            "Готовы ли вы к командировкам / вахте?",
            reply_markup=get_yes_no_keyboard()
        )


async def process_driver_categories(message: Message, state: FSMContext):
    """Обработка категорий водительского удостоверения"""
    if message.text == "⏭️ Пропустить":
        await message.answer("Пропущено. Готовы ли вы к командировкам / вахте?")
        await state.set_state(FormStates.waiting_for_business_trips)
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["additional"]["driver_categories"] = message.text
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_business_trips)
    await message.answer(
        "Готовы ли вы к командировкам / вахте?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_business_trips(message: Message, state: FSMContext):
    """Обработка готовности к командировкам"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_driver_categories)
        await message.answer("Введите категории водительского удостоверения:")
        return
    
    ready = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["additional"]["business_trips"] = ready
    await state.update_data(form_data=form_data)
    
    await state.set_state(FormStates.waiting_for_medical_exam)
    await message.answer(
        "Есть ли у вас медосмотр / допуск?",
        reply_markup=get_yes_no_keyboard()
    )


async def process_medical_exam(message: Message, state: FSMContext):
    """Обработка медосмотра"""
    if message.text == "⏪ Назад":
        await state.set_state(FormStates.waiting_for_business_trips)
        await message.answer("Готовы ли вы к командировкам / вахте?", reply_markup=get_yes_no_keyboard())
        return
    
    has_exam = "Да" in message.text
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["additional"]["medical_exam"] = has_exam
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    percentage, progress_bar = calculate_progress(form_data)
    await message.answer(
        f"{get_completion_message('Дополнительно')}\n\n"
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
        "Даете ли вы разрешение на выезд и проживание на вахте?",
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
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["confirmations"]["russia_stay"] = confirmed
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
    form_data["confirmations"]["compensation"] = consented
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
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
    if message.text == "⏭️ Пропустить":
        data = await state.get_data()
        form_data = data.get("form_data", {})
        percentage, progress_bar = calculate_progress(form_data)
        await message.answer(
            f"{get_completion_message('Комментарии')}\n\n"
            f"📊 Прогресс: {progress_bar} {percentage}%\n"
            f"{get_motivational_message(percentage)}",
            reply_markup=get_section_keyboard()
        )
        return
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
    form_data["comments"] = message.text
    await state.update_data(form_data=form_data)
    
    data = await state.get_data()
    form_data = data.get("form_data", {})
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
            "🎉 Поздравляем! Анкета успешно отправлена!\n\n"
            f"📊 Финальный прогресс: {progress_bar} {percentage}%\n"
            "✨ Спасибо за заполнение. Ваши данные сохранены в базу данных и отправлены в таблицу.\n"
            "🏆 Вы успешно завершили все разделы анкеты!",
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
    dp.callback_query.register(section_5_education, F.data == "section_5")
    dp.callback_query.register(section_6_work_experience, F.data == "section_6")
    dp.callback_query.register(section_7_additional, F.data == "section_7")
    dp.callback_query.register(section_8_consents, F.data == "section_8")
    dp.callback_query.register(section_9_confirmations, F.data == "section_9")
    dp.callback_query.register(section_10_comments, F.data == "section_10")
    dp.callback_query.register(finish_form_handler, F.data == "finish_form")
    
    # Раздел 1: Личные данные
    dp.message.register(process_surname, FormStates.waiting_for_surname)
    dp.message.register(process_name, FormStates.waiting_for_name)
    dp.message.register(process_patronymic, FormStates.waiting_for_patronymic)
    dp.message.register(process_birth_date, FormStates.waiting_for_birth_date)
    dp.message.register(process_birth_place, FormStates.waiting_for_birth_place)
    dp.message.register(process_citizenship, FormStates.waiting_for_citizenship)
    dp.message.register(process_gender, FormStates.waiting_for_gender)
    dp.message.register(process_photo_3x4, FormStates.waiting_for_photo_3x4)
    
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
    dp.message.register(process_email, FormStates.waiting_for_email)
    dp.message.register(process_social_media, FormStates.waiting_for_social_media)
    
    # Раздел 4: Документы и разрешения
    dp.message.register(process_medical_book, FormStates.waiting_for_medical_book)
    dp.message.register(process_work_permit, FormStates.waiting_for_work_permit)
    dp.message.register(process_registration, FormStates.waiting_for_registration)
    dp.message.register(process_snils, FormStates.waiting_for_snils)
    dp.message.register(process_inn, FormStates.waiting_for_inn)
    dp.message.register(process_fingerprinting, FormStates.waiting_for_fingerprinting)
    dp.message.register(process_medical_book_file, FormStates.waiting_for_medical_book_file)
    dp.message.register(process_work_permit_file, FormStates.waiting_for_work_permit_file)
    
    # Раздел 5: Образование
    dp.message.register(process_education_institution, FormStates.waiting_for_education_institution)
    dp.message.register(process_education_period, FormStates.waiting_for_education_period)
    dp.message.register(process_education_specialty, FormStates.waiting_for_education_specialty)
    dp.message.register(process_education_document, FormStates.waiting_for_education_document)
    dp.message.register(process_education_diploma, FormStates.waiting_for_education_diploma)
    
    # Раздел 6: Опыт работы
    dp.message.register(process_work_period, FormStates.waiting_for_work_period)
    dp.message.register(process_work_organization, FormStates.waiting_for_work_organization)
    dp.message.register(process_work_position, FormStates.waiting_for_work_position)
    dp.message.register(process_work_duties, FormStates.waiting_for_work_duties)
    dp.message.register(process_add_more_work, FormStates.waiting_for_add_more_work)
    
    # Раздел 7: Дополнительно
    dp.message.register(process_driver_license, FormStates.waiting_for_driver_license)
    dp.message.register(process_driver_categories, FormStates.waiting_for_driver_categories)
    dp.message.register(process_business_trips, FormStates.waiting_for_business_trips)
    dp.message.register(process_medical_exam, FormStates.waiting_for_medical_exam)
    
    # Раздел 8: Согласия
    dp.message.register(process_personal_data_consent, FormStates.waiting_for_personal_data_consent)
    dp.message.register(process_rotation_consent, FormStates.waiting_for_rotation_consent)
    
    # Раздел 9: Подтверждения
    dp.message.register(process_tuberculosis_confirmation, FormStates.waiting_for_tuberculosis_confirmation)
    dp.message.register(process_chronic_diseases_confirmation, FormStates.waiting_for_chronic_diseases_confirmation)
    dp.message.register(process_russia_stay_confirmation, FormStates.waiting_for_russia_stay_confirmation)
    dp.message.register(process_90_days_warning_confirmation, FormStates.waiting_for_90_days_warning_confirmation)
    dp.message.register(process_documents_readiness, FormStates.waiting_for_documents_readiness)
    dp.message.register(process_self_employment_consent, FormStates.waiting_for_self_employment_consent)
    dp.message.register(process_compensation_consent, FormStates.waiting_for_compensation_consent)
    
    # Раздел 10: Комментарии
    dp.message.register(process_comments, FormStates.waiting_for_comments)
    
    # Финальное подтверждение
    dp.message.register(process_final_confirmation, FormStates.waiting_for_final_confirmation)

