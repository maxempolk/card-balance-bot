# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Telegram bot built with aiogram 3.x that allows users to check their DNB Kronekort (prepaid card) balance and transactions. The bot integrates with DNB's public API to retrieve card information.

## Architecture

The codebase follows a simple modular architecture with three core components:

1. **main.py** - Bot orchestration layer
   - Handles Telegram bot initialization and message routing
   - Implements FSM (Finite State Machine) for card number collection
   - Manages user interaction flow with custom keyboard buttons
   - Uses aiogram's Dispatcher for command and message handling

2. **database.py** - Persistence layer
   - Simple JSON-based storage in `cards_db.json`
   - Stores mapping of Telegram chat_id to card numbers
   - Card numbers are stored trimmed (last digit removed before storage)
   - All functions handle chat_id as string keys for JSON compatibility

3. **api_client.py** - External API integration
   - Communicates with DNB Kronekort API endpoint
   - Uses aiohttp for async HTTP requests
   - Currently implements balance checking; transactions endpoint is a TODO placeholder

## Key Implementation Details

### Card Number Handling
- Users input 12-digit card numbers
- The bot **trims the last digit** before storing (see main.py:68)
- This trimmed 11-digit number is used for API calls
- Validation occurs before trimming: must be exactly 12 digits, numeric only

### State Management
- Uses aiogram's FSM with `CardStates.waiting_for_card` state
- State is set when user has no saved card
- State is cleared after successful card number storage
- State persists across messages until card is saved or /start is reused

### API Integration
- DNB API requires specific headers: `X-Dnbapi-Trace-Id` and `X-Dnbapi-Channel: BMPULS`
- Balance endpoint: POST to `https://api-open.ccp.dnb.no/v1/kronekort/balance`
- Request body: `{"accountNumber": "<11-digit-card-number>"}`

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Bot
```bash
python main.py
```

### Testing
No test suite is currently implemented. To test manually:
1. Start bot with `/start` command
2. Test card number validation with invalid inputs (non-numeric, wrong length)
3. Test balance retrieval with valid card number
4. Test transactions button (currently shows not implemented message)

## Important Notes

- **Security**: Bot token is currently hardcoded in main.py:11 - should be moved to environment variable
- **Database**: Using simple JSON file storage; consider migration to proper DB for production
- **Error Handling**: API errors are caught but only print to console; user gets generic error message
- **Transactions**: The transactions feature is stubbed but not implemented (api_client.py:41-53)
