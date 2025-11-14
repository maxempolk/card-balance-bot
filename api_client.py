import aiohttp
from typing import Optional

API_URL = "https://api-open.ccp.dnb.no/v1/kronekort/balance"

async def get_card_balance(card_number: str) -> Optional[float]:
    """
    Получает баланс карты через API DNB

    Args:
        card_number: Номер карты

    Returns:
        Баланс карты или None в случае ошибки
    """
    headers = {
        "X-Dnbapi-Trace-Id": "b3e4d7f2-c5a8-41e6-8b1a-7f9c2e5d3a4b",
        "X-Dnbapi-Channel": "BMPULS",
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
