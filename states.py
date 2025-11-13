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
    waiting_for_photo_3x4 = State()
    
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
    waiting_for_email = State()
    waiting_for_social_media = State()
    
    # 4. Документы и разрешения
    waiting_for_medical_book = State()
    waiting_for_work_permit = State()
    waiting_for_registration = State()
    waiting_for_snils = State()
    waiting_for_inn = State()
    waiting_for_fingerprinting = State()
    waiting_for_medical_book_file = State()
    waiting_for_work_permit_file = State()
    
    # 5. Образование
    waiting_for_education_institution = State()
    waiting_for_education_period = State()
    waiting_for_education_specialty = State()
    waiting_for_education_document = State()
    waiting_for_education_diploma = State()
    
    # 6. Опыт работы
    waiting_for_work_period = State()
    waiting_for_work_organization = State()
    waiting_for_work_position = State()
    waiting_for_work_duties = State()
    waiting_for_add_more_work = State()
    
    # 7. Дополнительно
    waiting_for_driver_license = State()
    waiting_for_driver_categories = State()
    waiting_for_business_trips = State()
    waiting_for_medical_exam = State()
    
    # 8. Согласия
    waiting_for_personal_data_consent = State()
    waiting_for_rotation_consent = State()
    
    # 9-15. Подтверждения
    waiting_for_tuberculosis_confirmation = State()
    waiting_for_chronic_diseases_confirmation = State()
    waiting_for_russia_stay_confirmation = State()
    waiting_for_90_days_warning_confirmation = State()
    waiting_for_documents_readiness = State()
    waiting_for_self_employment_consent = State()
    waiting_for_compensation_consent = State()
    
    # 16. Комментарии
    waiting_for_comments = State()
    
    # Финальное подтверждение
    waiting_for_final_confirmation = State()

