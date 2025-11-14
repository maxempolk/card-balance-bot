# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot built with aiogram 3.x that allows users to check their DNB Kronekort (prepaid card) balance and receives automatic notifications for salary payments. The bot integrates with DNB's public API to retrieve card information and includes an automated payment monitoring system.

## Architecture

The codebase follows a modular architecture with six core components:

1. **main.py** - Bot orchestration layer
   - Handles Telegram bot initialization and message routing
   - Implements FSM (Finite State Machine) for card number collection
   - Manages user interaction flow with custom keyboard buttons
   - Launches background payment checker task on startup (main.py:121)
   - Uses aiogram's Dispatcher for command and message handling

2. **database.py** - Persistence layer
   - JSON-based storage in `cards_db.json` (location configured via .env)
   - Database structure per user (chat_id as string key):
     ```python
     {
       "card_number": "11-digit-trimmed-number",
       "balance_history": [{"date": "YYYY-MM-DD HH:MM:SS", "balance": float}, ...],
       "payments": {"YYYY-MM-DD": {"received": bool, "timestamp": str, "amount": float}}
     }
     ```
   - Automatic migration from legacy format (simple string card number) to new dict format
   - Balance history tracking: every balance check is recorded with timestamp
   - Payment tracking: prevents duplicate notifications and API calls

3. **api_client.py** - External API integration
   - Communicates with DNB Kronekort API endpoints
   - Uses aiohttp for async HTTP requests
   - Balance endpoint: `POST /v1/kronekort/balance`
   - Transactions endpoint: `POST /v1/kronekort/transactions` (recently implemented)

4. **payment_checker.py** - Automated payment monitoring
   - Background task that runs continuously in event loop
   - **Payment schedule**: Checks for payments on 1st and 16th of each month
   - **Check window**: ±2 days around payment date (configurable via PAYMENT_CHECK_DAYS_BEFORE/AFTER)
   - **Check frequency**: Hourly during active window (configurable via PAYMENT_CHECK_INTERVAL_HOURS)
   - **Payment detection**: Transaction amount > 1000 NOK (configurable via PAYMENT_MIN_AMOUNT)
   - **Timezone**: All checks use Norway time (Europe/Oslo)
   - **Optimization**: Checks database before API call; skips users who already received payment for current period
   - Transaction parsing handles nested amount structure: `transaction.get("amount").get("amount")`

5. **messages.py** - User-facing text content
   - Centralized message management via `Messages` class (static methods and constants)
   - Button text management via `ButtonTexts` class
   - All user-facing strings are here for easy localization/modification

6. **config.py** - Configuration management
   - Loads all settings from `.env` file using python-dotenv
   - Provides typed configuration variables to entire application
   - Use `.env.example` as template for setting up environment

## Key Implementation Details

### Card Number Handling
- Users input 12-digit card numbers (configurable via CARD_NUMBER_LENGTH in .env)
- The bot **trims the last digit** before storing (main.py:62)
- This trimmed 11-digit number is used for all API calls
- Validation before trimming: must be exactly 12 digits, numeric only

### State Management
- Uses aiogram's FSM with `CardStates.waiting_for_card` state
- State set when user has no saved card
- State cleared after successful card number storage
- State persists across messages until card is saved or /start is reused

### API Integration
- DNB API requires specific headers:
  - `X-Dnbapi-Trace-Id`: Unique trace ID (from .env)
  - `X-Dnbapi-Channel`: Always "BMPULS"
  - `Content-Type`: "application/json"
- Balance endpoint: POST to `API_URL` with body `{"accountNumber": "<11-digit-number>"}`
- Transactions endpoint: POST to `API_TRANSACTIONS_URL` with body `{"accountNumber": "<11-digit-number>", "limit": 5}`

### Payment Checker Flow
1. Every hour (when in payment window), iterate through all users via `get_all_users()`
2. For each user:
   - Check if payment period is active (within ±2 days of payment date)
   - Check database for existing payment record → skip if found
   - Fetch last 5 transactions via API
   - Parse each transaction's nested amount field
   - If amount > 1000 NOK → mark as payment, notify user, stop checking for this period
3. Sleep until next check interval

### Message Editing Pattern
- Balance checks use message editing for better UX:
  ```python
  status_msg = await message.answer("Получаю баланс...")
  # ... API call ...
  await status_msg.edit_text(f"Баланс: {balance} NOK")
  ```

## Development Commands

### Setup
```bash
# Create .env file from template
cp .env.example .env
# Edit .env with your actual tokens

# Install dependencies
pip install -r requirements.txt
```

### Running the Bot
```bash
python main.py
```

### Environment Variables
All configuration is via `.env` file. Required variables:
- `BOT_TOKEN` - Telegram bot token (get from @BotFather)
- `API_TRACE_ID` - DNB API trace ID
- `API_CHANNEL` - DNB API channel (default: BMPULS)

Optional variables (have defaults):
- `DB_FILE` - Database filename (default: cards_db.json)
- `CARD_NUMBER_LENGTH` - Expected card number length (default: 12)
- `PAYMENT_DATES` - Comma-separated payment dates (default: 1,16)
- `PAYMENT_MIN_AMOUNT` - Minimum amount to consider as payment (default: 1000)
- `PAYMENT_CHECK_INTERVAL_HOURS` - Hours between payment checks (default: 1)

### Testing
No automated test suite. Manual testing workflow:
1. Start bot with `/start` command
2. Test card number validation (non-numeric, wrong length)
3. Test balance retrieval with valid card number
4. Check balance history is recorded in `cards_db.json`
5. For payment checker: manually set system date to payment window or modify `PAYMENT_DATES` in .env

## Important Notes

- **Database Schema Evolution**: `database.py` automatically migrates old format (string) to new format (dict with history)
- **Timezone Awareness**: Payment checker uses `pytz` for Norway timezone - critical for correct payment date calculations
- **Background Tasks**: Payment checker runs in asyncio event loop alongside bot polling
- **Error Handling**: Most errors print to console; users receive generic error messages
- **Transaction Parsing**: DNB API returns nested amount: `{"amount": {"amount": "1234.56"}}` - handled in payment_checker.py:68-73
