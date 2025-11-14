import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import get_card_number, set_card_number, add_balance_history
from api_client import get_card_balance, get_card_transactions
from config import BOT_TOKEN, CARD_NUMBER_LENGTH
from payment_checker import payment_checker_task
from messages import Messages, ButtonTexts

dp = Dispatcher()

class CardStates(StatesGroup):
    waiting_for_card = State()

# Создание клавиатуры с кнопками
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ButtonTexts.GET_BALANCE)],
            # [KeyboardButton(text=ButtonTexts.GET_TRANSACTIONS)]
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext):
    # Проверяем, есть ли уже сохраненная карта
    card_number = get_card_number(message.chat.id)

    if card_number:
        await message.answer(
            Messages.welcome_with_card(card_number),
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(Messages.welcome_new_user())
        await state.set_state(CardStates.waiting_for_card)

@dp.message(CardStates.waiting_for_card)
async def process_card_number(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(Messages.SEND_TEXT_MESSAGE)
        return

    card_number = message.text.strip()

    # Проверка длины номера карты (должно быть 12 цифр)
    if not card_number.isdigit():
        await message.answer(Messages.CARD_ONLY_DIGITS)
        return

    if len(card_number) != CARD_NUMBER_LENGTH:
        await message.answer(Messages.card_wrong_length(len(card_number)))
        return

    # Сохраняем номер карты, обрезав последнюю цифру
    card_number_trimmed = card_number[:-1]
    set_card_number(message.chat.id, card_number_trimmed)

    await message.answer(
        Messages.card_saved_success(card_number),
        reply_markup=get_main_keyboard()
    )
    await state.clear()

@dp.message(F.text == ButtonTexts.GET_BALANCE)
async def get_balance_handler(message: Message):
    card_number = get_card_number(message.chat.id)

    if not card_number:
        await message.answer(Messages.NO_CARD_SAVED)
        return

    status_message = await message.answer(Messages.GETTING_BALANCE)

    balance = await get_card_balance(card_number)

    if balance is not None:
        # Сохраняем баланс в историю
        add_balance_history(message.chat.id, balance)
        await status_message.edit_text(Messages.balance_result(balance))
    else:
        await status_message.edit_text(Messages.BALANCE_ERROR)

# @dp.message(F.text == "Получить последние 5 транзакций")
# async def get_transactions_handler(message: Message):
#     card_number = get_card_number(message.chat.id)

#     if not card_number:
#         await message.answer(
#             "Сначала нужно сохранить номер карты.\n"
#             "Используйте команду /start"
#         )
#         return

#     await message.answer("Получаю последние транзакции...")

#     transactions = await get_card_transactions(card_number)

#     if transactions:
#         # Форматирование и отображение транзакций
#         response = "Последние 5 транзакций:\n\n"
#         for i, transaction in enumerate(transactions[:5], 1):
#             response += f"{i}. {transaction}\n"
#         await message.answer(response)
#     else:
#         await message.answer(
#             "Функция получения транзакций пока не реализована полностью.\n"
#             "В данный момент доступна только проверка баланса."
#         )

async def main() -> None:
    bot = Bot(token=BOT_TOKEN)

    # Запускаем задачу проверки выплат в фоне
    asyncio.create_task(payment_checker_task(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())