"""Модуль для работы с SQLite базой данных"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any


DB_PATH = "data/anketa.db"


def init_database():
    """Инициализирует базу данных и создает таблицы"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Создаем таблицу для анкет
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            form_data TEXT NOT NULL,
            filled_at TEXT NOT NULL,
            sent_to_sheets INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    # Создаем индекс для быстрого поиска по user_id
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON forms(user_id)
    """)
    
    conn.commit()
    conn.close()


def save_form_to_db(user_id: int, form_data: dict) -> int:
    """Сохраняет или обновляет анкету в базе данных. Возвращает ID записи"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже анкета для этого пользователя
    cursor.execute("SELECT id FROM forms WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,))
    existing = cursor.fetchone()
    
    form_data_json = json.dumps(form_data, ensure_ascii=False)
    now = datetime.now().isoformat()
    
    if existing:
        # Обновляем существующую запись
        form_id = existing[0]
        cursor.execute("""
            UPDATE forms 
            SET form_data = ?, updated_at = ?
            WHERE id = ?
        """, (form_data_json, now, form_id))
    else:
        # Создаем новую запись
        filled_at = form_data.get("filled_at", now)
        cursor.execute("""
            INSERT INTO forms (user_id, form_data, filled_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, form_data_json, filled_at, now, now))
        form_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    return form_id


def load_form_from_db(user_id: int) -> Optional[Dict[str, Any]]:
    """Загружает анкету пользователя из базы данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT form_data FROM forms 
        WHERE user_id = ? 
        ORDER BY updated_at DESC 
        LIMIT 1
    """, (user_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None


def get_unsent_forms() -> list:
    """Возвращает список анкет, которые еще не отправлены в Google Sheets"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, user_id, form_data FROM forms 
        WHERE sent_to_sheets = 0
        ORDER BY updated_at ASC
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    forms = []
    for row in results:
        forms.append({
            "id": row[0],
            "user_id": row[1],
            "form_data": json.loads(row[2])
        })
    return forms


def mark_as_sent(form_id: int):
    """Отмечает анкету как отправленную в Google Sheets"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE forms 
        SET sent_to_sheets = 1 
        WHERE id = ?
    """, (form_id,))
    
    conn.commit()
    conn.close()


def get_form_by_id(form_id: int) -> Optional[Dict[str, Any]]:
    """Получает анкету по ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT user_id, form_data FROM forms WHERE id = ?
    """, (form_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "user_id": result[0],
            "form_data": json.loads(result[1])
        }
    return None

