import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PHOTOGRAPHER_CHAT_ID = os.getenv("PHOTOGRAPHER_CHAT_ID")  # вставь свой Telegram ID сюда

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Главное меню ---
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Узнать цены")],
            [KeyboardButton(text="📸 Виды съёмок")],
            [KeyboardButton(text="📅 Проверить свободные даты")],
            [KeyboardButton(text="⏳ Сроки и обработка")],
            [KeyboardButton(text="☎️ Хочу, чтобы со мной связались")]
        ],
        resize_keyboard=True
    )


@dp.message(Command("start"))
async def start_command(message: types.Message):
    name = message.from_user.first_name or "друг"
    await message.answer(
        f"Привет, {name}! 👋\n"
        "Я ассистент фотографа 🌿\n"
        "Помогу рассказать про цены, даты и формат съёмки.\n\n"
        "Выберите интересующий пункт ниже 👇",
        reply_markup=main_menu()
    )


# --- Ответы на частые вопросы ---
@dp.message(F.text == "💰 Узнать цены")
async def show_prices(message: types.Message):
    name = message.from_user.first_name or "друг"
    await message.answer(
        f"{name}, вот базовые цены на фотосессии 💵:\n\n"
        "• Индивидуальная — от 120 BYN\n"
        "• Семейная — от 150 BYN\n"
        "• Love Story — от 130 BYN\n"
        "• Детская — от 100 BYN\n"
        "• Мероприятия — по договорённости\n\n"
        "Хотите уточнить детали или записаться?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📸 Хочу уточнить вид съёмки")],
                [KeyboardButton(text="☎️ Хочу, чтобы со мной связались")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    )


@dp.message(F.text == "📸 Виды съёмок")
async def show_types(message: types.Message):
    await message.answer(
        "Провожу разные виды съёмок 📷:\n"
        "• Индивидуальная\n• Семейная\n• Детская\n• Love Story\n• Контент / Мероприятия\n\n"
        "Вы можете уточнить цену или доступные даты 👇",
        reply_markup=main_menu()
    )


@dp.message(F.text == "📅 Проверить свободные даты")
async def show_dates(message: types.Message):
    await message.answer(
        "Свободные даты быстро меняются 🗓️\n"
        "Напишите, пожалуйста, месяц и примерный день, и я проверю наличие.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📞 Хочу, чтобы со мной связались")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    )


@dp.message(F.text == "⏳ Сроки и обработка")
async def show_deadlines(message: types.Message):
    await message.answer(
        "⏱️ Обычно фотографии готовы через 7–14 дней.\n"
        "Количество обработанных снимков зависит от выбранного пакета (в среднем 40–80 фото).\n\n"
        "Хотите узнать точнее для своего случая?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="💰 Узнать цены")],
                [KeyboardButton(text="☎️ Хочу, чтобы со мной связались")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    )


@dp.message(F.text == "🔙 Назад")
async def go_back(message: types.Message):
    await message.answer("Вы вернулись в главное меню 👇", reply_markup=main_menu())


# --- Когда клиент хочет, чтобы с ним связались ---
@dp.message(F.text == "☎️ Хочу, чтобы со мной связались")
async def contact_request(message: types.Message):
    name = message.from_user.first_name or "клиент"
    username = message.from_user.username or "без username"
    user_id = message.from_user.id

    await message.answer(
        f"Спасибо, {name}! 😊\n"
        "Я передам фотографу, чтобы он связался с вами в ближайшее время.\n\n"
        "Вы можете пока посмотреть другие варианты 👇",
        reply_markup=main_menu()
    )

    # Отправляем уведомление фотографу
    if PHOTOGRAPHER_CHAT_ID:
        await bot.send_message(
            PHOTOGRAPHER_CHAT_ID,
            f"📞 Новый запрос от клиента:\n"
            f"Имя: {name}\n"
            f"Username: @{username}\n"
            f"ID: {user_id}\n"
            f"Просит связаться!"
        )


@dp.message()
async def fallback(message: types.Message):
    name = message.from_user.first_name or "друг"
    await message.answer(
        f"{name}, я ассистент фотографа 🌿\n"
        "Выберите пункт из меню ниже, чтобы я мог помочь 👇",
        reply_markup=main_menu()
    )


async def main():
    logger.info("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
