"""
Модуль для автоматической проверки выплат пользователей
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
import pytz

from aiogram import Bot

from config import (
    PAYMENT_DATES,
    PAYMENT_CHECK_DAYS_BEFORE,
    PAYMENT_CHECK_DAYS_AFTER,
    PAYMENT_CHECK_INTERVAL_HOURS,
    PAYMENT_MIN_AMOUNT,
    NORWAY_TIMEZONE
)
from database import (
    get_all_users,
    get_card_number,
    is_payment_received,
    mark_payment_received
)
from api_client import get_card_transactions
from messages import Messages


def get_norway_time() -> datetime:
    """Возвращает текущее время в Норвегии"""
    norway_tz = pytz.timezone(NORWAY_TIMEZONE)
    return datetime.now(norway_tz)


def get_current_payment_period() -> Optional[str]:
    """
    Определяет текущий период выплат на основе текущей даты
    Возвращает строку вида "YYYY-MM-DD" для даты выплаты или None
    """
    now = get_norway_time()

    # Определяем, к какому периоду выплат мы ближе
    for payment_date in PAYMENT_DATES:
        # Создаем дату выплаты для текущего месяца
        try:
            payment_datetime = now.replace(day=payment_date, hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            # Если такого дня нет в месяце (например, 31 февраля)
            continue

        # Проверяем, находимся ли мы в диапазоне проверки
        start_check = payment_datetime - timedelta(days=PAYMENT_CHECK_DAYS_BEFORE)
        end_check = payment_datetime + timedelta(days=PAYMENT_CHECK_DAYS_AFTER)

        if start_check <= now <= end_check:
            return payment_datetime.strftime("%Y-%m-%d")

    return None


def check_transaction_is_payment(transaction: dict) -> Optional[float]:
    """
    Проверяет, является ли транзакция выплатой
    Возвращает сумму выплаты или None
    """
    try:
        amount_str = transaction.get("amount", None)
        
        if amount_str is None:
            return None
        
        amount_str = amount_str.get("amount")

        if isinstance(amount_str, str):
            # Удаляем возможные пробелы и заменяем запятую на точку
            amount_str = amount_str.replace(" ", "").replace(",", ".")
            amount = float(amount_str)
        else:
            amount = float(amount_str)

        # Проверяем условия выплаты
        if amount > 0 and amount > PAYMENT_MIN_AMOUNT:
            return amount
        return None
    except (ValueError, TypeError) as exp:
        print(f"ERROR: {exp}")
        return None


async def check_user_payment(chat_id: str, bot: Bot) -> bool:
    """
    Проверяет, получил ли пользователь выплату
    Возвращает True, если выплата найдена
    """
    # Получаем текущий период выплат
    payment_period = get_current_payment_period()
    if not payment_period:
        return False

    # Проверяем, не была ли уже зафиксирована выплата
    if is_payment_received(int(chat_id), payment_period):
        return True

    # Получаем номер карты пользователя
    card_number = get_card_number(int(chat_id))
    if not card_number:
        return False

    # Получаем последние транзакции
    transactions = await get_card_transactions(card_number)

    if not transactions:
        return False

    # Проверяем транзакции на наличие выплаты
    for transaction in transactions:
        payment_amount = check_transaction_is_payment(transaction)
        print(transaction)
        if payment_amount:
            # Выплата найдена!
            mark_payment_received(int(chat_id), payment_period, payment_amount)

            # Отправляем уведомление пользователю
            try:
                await bot.send_message(
                    chat_id=int(chat_id),
                    text=Messages.payment_received(payment_amount)
                )
            except Exception as e:
                print(f"Error sending notification to {chat_id}: {e}")

            return True

    return False


async def payment_checker_task(bot: Bot):
    """
    Основная задача для проверки выплат всех пользователей
    Запускается периодически
    """
    while True:
        try:
            # Проверяем, находимся ли мы в периоде проверки выплат
            payment_period = get_current_payment_period()

            if payment_period:
                print(f"Checking payments for period: {payment_period}")

                # Получаем всех пользователей
                users = get_all_users()

                # Проверяем каждого пользователя
                print(users)
                for chat_id in users:
                    try:
                        await check_user_payment(chat_id, bot)
                    except Exception as e:
                        print(f"Error checking payment for user {chat_id}: {e}")

                    # Небольшая задержка между проверками разных пользователей
                    await asyncio.sleep(1)

            # Ждем до следующей проверки
            await asyncio.sleep(PAYMENT_CHECK_INTERVAL_HOURS * 3600)

        except Exception as e:
            print(f"Error in payment checker task: {e}")
            # В случае ошибки ждем 5 минут перед повтором
            await asyncio.sleep(300)
