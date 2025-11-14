"""
Конфигурационный файл с глобальными настройками бота
Загружает переменные из .env файла
"""

import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Database
DB_FILE = os.getenv("DB_FILE", "cards_db.json")

# DNB API
API_URL = os.getenv("API_URL", "https://api-open.ccp.dnb.no/v1/kronekort/balance")
API_TRACE_ID = os.getenv("API_TRACE_ID", "")
API_CHANNEL = os.getenv("API_CHANNEL", "BMPULS")

# Card validation
CARD_NUMBER_LENGTH = int(os.getenv("CARD_NUMBER_LENGTH", "12"))

# Payment checking
PAYMENT_DATES = [int(x.strip()) for x in os.getenv("PAYMENT_DATES", "1,16").split(",")]
PAYMENT_CHECK_DAYS_BEFORE = int(os.getenv("PAYMENT_CHECK_DAYS_BEFORE", "2"))
PAYMENT_CHECK_DAYS_AFTER = int(os.getenv("PAYMENT_CHECK_DAYS_AFTER", "2"))
PAYMENT_CHECK_INTERVAL_HOURS = int(os.getenv("PAYMENT_CHECK_INTERVAL_HOURS", "1"))
PAYMENT_MIN_AMOUNT = int(os.getenv("PAYMENT_MIN_AMOUNT", "1000"))
NORWAY_TIMEZONE = os.getenv("NORWAY_TIMEZONE", "Europe/Oslo")
