"""
Конфигурационный файл с глобальными настройками бота
"""

# Telegram Bot
BOT_TOKEN = "8439983396:AAECjzrcPZxu4IulJranmXOG1m3ybLlj66A"

# Database
DB_FILE = "cards_db.json"

# DNB API
API_URL = "https://api-open.ccp.dnb.no/v1/kronekort/balance"
API_TRACE_ID = "b3e4d7f2-c5a8-41e6-8b1a-7f9c2e5d3a4b"
API_CHANNEL = "BMPULS"

# Card validation
CARD_NUMBER_LENGTH = 12

# Payment checking
PAYMENT_DATES = [1, 16]  # Даты выплат каждого месяца
PAYMENT_CHECK_DAYS_BEFORE = 2  # За сколько дней до выплаты начинать проверки
PAYMENT_CHECK_DAYS_AFTER = 2  # Сколько дней после выплаты продолжать проверки
PAYMENT_CHECK_INTERVAL_HOURS = 1  # Интервал проверки в часах
PAYMENT_MIN_AMOUNT = 1000  # Минимальная сумма для определения выплаты
NORWAY_TIMEZONE = "Europe/Oslo"  # Временная зона Норвегии
