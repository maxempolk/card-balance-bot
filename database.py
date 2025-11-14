import json
import os
from typing import Optional
from datetime import datetime

DB_FILE = "cards_db.json"

def load_db() -> dict:
    """Загружает базу данных из JSON файла"""
    if not os.path.exists(DB_FILE):
        return {}

    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_db(db: dict) -> None:
    """Сохраняет базу данных в JSON файл"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def get_card_number(chat_id: int) -> Optional[str]:
    """Получает номер карты для указанного chat_id"""
    db = load_db()
    user_data = db.get(str(chat_id))
    if isinstance(user_data, str):
        # Миграция старого формата (просто номер карты) в новый формат
        card_number = user_data
        db[str(chat_id)] = {
            "card_number": card_number,
            "balance_history": []
        }
        save_db(db)
        return card_number
    elif isinstance(user_data, dict):
        return user_data.get("card_number")
    return None

def set_card_number(chat_id: int, card_number: str) -> None:
    """Сохраняет номер карты для указанного chat_id"""
    db = load_db()
    user_data = db.get(str(chat_id))

    if isinstance(user_data, dict):
        # Обновляем только номер карты, сохраняя историю
        user_data["card_number"] = card_number
        db[str(chat_id)] = user_data
    else:
        # Создаем новую запись
        db[str(chat_id)] = {
            "card_number": card_number,
            "balance_history": []
        }
    save_db(db)

def add_balance_history(chat_id: int, balance: float) -> None:
    """Добавляет запись о балансе в историю пользователя"""
    db = load_db()
    user_data = db.get(str(chat_id))

    if not user_data:
        return

    # Если старый формат, мигрируем
    if isinstance(user_data, str):
        card_number = user_data
        user_data = {
            "card_number": card_number,
            "balance_history": []
        }

    # Добавляем новую запись в историю
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    balance_entry = {
        "date": current_datetime,
        "balance": balance
    }

    if "balance_history" not in user_data:
        user_data["balance_history"] = []

    user_data["balance_history"].append(balance_entry)
    db[str(chat_id)] = user_data
    save_db(db)

def get_balance_history(chat_id: int) -> list:
    """Получает историю балансов для указанного chat_id"""
    db = load_db()
    user_data = db.get(str(chat_id))

    if isinstance(user_data, dict):
        return user_data.get("balance_history", [])
    return []

def delete_card_number(chat_id: int) -> None:
    """Удаляет номер карты для указанного chat_id"""
    db = load_db()
    if str(chat_id) in db:
        del db[str(chat_id)]
        save_db(db)
