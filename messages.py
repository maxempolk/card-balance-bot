"""
Все сообщения бота для пользователей
"""

from config import CARD_NUMBER_LENGTH


class Messages:
    """Класс содержащий все текстовые сообщения бота"""

    # Команда /start
    @staticmethod
    def welcome_with_card(card_number: str) -> str:
        return (
            f"Привет! У вас уже сохранена карта: {card_number}\n\n"
            "Выберите действие с помощью кнопок ниже:"
        )

    @staticmethod
    def welcome_new_user() -> str:
        return (
            "Привет! Я бот для проверки баланса карты DNB.\n\n"
            f"Пожалуйста, введите номер вашей карты ({CARD_NUMBER_LENGTH} цифр):"
        )

    # Ввод номера карты
    SEND_TEXT_MESSAGE = "Пожалуйста, отправьте текстовое сообщение с номером карты."

    CARD_ONLY_DIGITS = "Номер карты должен содержать только цифры. Попробуйте еще раз:"

    @staticmethod
    def card_wrong_length(entered_length: int) -> str:
        return (
            f"Номер карты должен содержать {CARD_NUMBER_LENGTH} цифр. "
            f"Вы ввели {entered_length} цифр.\n"
            "Попробуйте еще раз:"
        )

    @staticmethod
    def card_saved_success(card_number: str) -> str:
        return (
            f"Номер карты {card_number} успешно сохранен!\n\n"
            "Теперь вы можете использовать кнопки ниже для получения информации:"
        )

    # Баланс
    NO_CARD_SAVED = (
        "Сначала нужно сохранить номер карты.\n"
        "Используйте команду /start"
    )

    GETTING_BALANCE = "Получаю баланс..."

    @staticmethod
    def balance_result(balance: float) -> str:
        return f"Баланс вашей карты: {balance} NOK"

    BALANCE_ERROR = (
        "Не удалось получить баланс. Проверьте правильность номера карты.\n"
        "Используйте /start чтобы ввести номер заново."
    )

    # Выплаты
    @staticmethod
    def payment_received(amount: float) -> str:
        return f"Выплата получена! Сумма: {amount} NOK"

    # Транзакции (закомментированная функциональность)
    GETTING_TRANSACTIONS = "Получаю последние транзакции..."

    TRANSACTIONS_NOT_IMPLEMENTED = (
        "Функция получения транзакций пока не реализована полностью.\n"
        "В данный момент доступна только проверка баланса."
    )


class ButtonTexts:
    """Тексты для кнопок клавиатуры"""

    GET_BALANCE = "Получить баланс"
    GET_TRANSACTIONS = "Получить последние 5 транзакций"
