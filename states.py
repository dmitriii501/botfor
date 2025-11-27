from aiogram.fsm.state import State, StatesGroup


class FormStates(StatesGroup):
    # 1. Личные данные
    waiting_for_surname = State()
    waiting_for_name = State()
    waiting_for_patronymic = State()
    waiting_for_birth_date = State()
    waiting_for_birth_place = State()
    waiting_for_citizenship = State()
    waiting_for_gender = State()
    
    # Выбор гражданства (после ФИО и контактов)
    waiting_for_citizenship_choice = State()
    
    # 2. Паспортные данные
    waiting_for_passport_series_number = State()
    waiting_for_passport_issued_by = State()
    waiting_for_passport_issue_date = State()
    waiting_for_passport_division_code = State()
    waiting_for_registration_address = State()
    waiting_for_actual_address = State()
    waiting_for_additional_docs = State()
    waiting_for_passport_photo = State()
    
    # 3. Контактная информация
    waiting_for_phone = State()
    
    # 4. Документы и разрешения
    waiting_for_medical_book = State()
    waiting_for_registration = State()
    waiting_for_snils = State()
    waiting_for_inn = State()
    waiting_for_medical_book_file = State()
    
    # Для иностранцев дополнительно
    waiting_for_foreigner_id = State()
    waiting_for_fingerprinting = State()
    waiting_for_medical_exam_dactyloscopy = State()
    waiting_for_mvd_registry_check = State()
    
    # 5. Готовность к работе
    waiting_for_vakhta_start_date = State()
    waiting_for_business_trips = State()
    waiting_for_city = State()
    
    # 6. Согласия
    waiting_for_personal_data_consent = State()
    waiting_for_rotation_consent = State()
    
    # 7. Подтверждения (для всех)
    waiting_for_comments = State()
    
    # 8. Подтверждения (только для иностранцев)
    waiting_for_tuberculosis_confirmation = State()
    waiting_for_chronic_diseases_confirmation = State()
    waiting_for_russia_stay_confirmation = State()
    waiting_for_90_days_warning_confirmation = State()
    waiting_for_documents_readiness = State()
    waiting_for_self_employment_consent = State()
    waiting_for_compensation_consent = State()
    
    # Финальное подтверждение
    waiting_for_final_confirmation = State()

