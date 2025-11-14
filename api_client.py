import aiohttp
from typing import Optional

from config import API_URL, API_TRACE_ID, API_CHANNEL

async def get_card_balance(card_number: str) -> Optional[float]:
    """
    Получает баланс карты через API DNB

    Args:
        card_number: Номер карты

    Returns:
        Баланс карты или None в случае ошибки
    """
    headers = {
        "X-Dnbapi-Trace-Id": API_TRACE_ID,
        "X-Dnbapi-Channel": API_CHANNEL,
        "Content-Type": "application/json"
    }

    body = {
        "accountNumber": card_number
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=body, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("balance")
                else:
                    return None
    except Exception as e:
        print(f"Error getting balance: {e}")
        return None

async def get_card_transactions(card_number: str) -> Optional[list]:
    """
    Получает последние транзакции по карте

    Args:
        card_number: Номер карты

    Returns:
        Список транзакций или None в случае ошибки
    """
    # Placeholder для будущей реализации
    # TODO: Добавить реальный API endpoint для транзакций
    return []
