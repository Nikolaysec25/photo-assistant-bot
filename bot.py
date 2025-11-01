import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
import os

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ⚠️ Укажи свой Telegram ID, чтобы получать уведомления о клиентах
ADMIN_ID = 1054983240

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ===============================
# Сценарии диалога
# ===============================

@dp.message(Command("start"))
async def start_command(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💰 Узнать цену", "📸 Виды съёмок")
    await message.answer(
        f"Здравствуйте, {name}! 👋\n"
        "Я ассистент фотографа.\n\n"
        "Помогу быстро узнать нужную информацию — просто выберите, что вас интересует 👇",
        reply_markup=keyboard
    )

# ---------- Этап 1: Цена ----------
@dp.message(lambda m: m.text in ["💰 Узнать цену", "цена", "стоимость"])
async def ask_type(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("👤 Индивидуальная", "👨‍👩‍👧 Семейная", "💞 Love Story", "🎉 Мероприятие")
    await message.answer(
        f"{name}, выберите тип съёмки, чтобы я показал стоимость 👇",
        reply_markup=keyboard
    )

@dp.message(lambda m: m.text in ["👤 Индивидуальная", "👨‍👩‍👧 Семейная", "💞 Love Story", "🎉 Мероприятие"])
async def show_price(message: types.Message):
    name = message.from_user.first_name or "друг"
    text = message.text
    prices = {
        "👤 Индивидуальная": "💰 Индивидуальная фотосессия — от 120 BYN (1 час, до 60 фото).",
        "👨‍👩‍👧 Семейная": "👨‍👩‍👧 Семейная съёмка — от 150 BYN (до 1.5 часов, 70 фото).",
        "💞 Love Story": "💞 Love Story — от 180 BYN (1.5 часа, 60–80 фото).",
        "🎉 Мероприятие": "🎉 Съёмка мероприятий — от 200 BYN (2 часа и более)."
    }
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📅 Узнать свободные даты", "📍 Где проходят съёмки")
    await message.answer(
        f"{name}, {prices[text]}\n\nХотите узнать свободные даты или место съёмки?",
        reply_markup=keyboard
    )

# ---------- Этап 2: Даты ----------
@dp.message(lambda m: m.text in ["📅 Узнать свободные даты", "дата", "свободные даты"])
async def ask_date(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("📆 В ближайшие выходные", "📆 На следующей неделе", "📆 В другой день")
    await message.answer(
        f"{name}, когда вы планируете съёмку?",
        reply_markup=keyboard
    )

@dp.message(lambda m: m.text.startswith("📆"))
async def show_date_info(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("✅ Хочу записаться", "❌ Пока думаю")
    await message.answer(
        f"{name}, отлично! Эти даты сейчас ещё доступны 📅\n"
        "Хотите, чтобы фотограф связался с вами для брони?",
        reply_markup=keyboard
    )

# ---------- Этап 3: Место ----------
@dp.message(lambda m: m.text in ["📍 Где проходят съёмки", "место", "локация"])
async def show_location(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🏢 В студии", "🌿 На улице", "🏠 На выезде")
    await message.answer(
        f"{name}, съёмки проходят в студии, на улице или на выезде. Что вам подходит?",
        reply_markup=keyboard
    )

@dp.message(lambda m: m.text in ["🏢 В студии", "🌿 На улице", "🏠 На выезде"])
async def location_selected(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("✅ Хочу записаться", "❌ Пока думаю")
    await message.answer(
        f"{name}, отлично! 📸 Это отличное место для фото.\n"
        "Хотите, чтобы фотограф связался с вами лично?",
        reply_markup=keyboard
    )

# ---------- Этап 4: Заявка ----------
@dp.message(lambda m: m.text == "✅ Хочу записаться")
async def contact_request(message: types.Message):
    user = message.from_user
    name = user.first_name or "Клиент"
    await message.answer(
        f"Спасибо, {name}! 🙌 Я передал фотографу, что вы хотите записаться.\n"
        "Он свяжется с вами в ближайшее время!"
    )

    msg_to_admin = (
        f"📞 Новый клиент хочет записаться!\n\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username if user.username else '—'}\n"
        f"ID: {user.id}"
    )
    try:
        await bot.send_message(ADMIN_ID, msg_to_admin)
    except Exception as e:
        logging.warning(f"Ошибка при отправке уведомления фотографу: {e}")

@dp.message(lambda m: m.text == "❌ Пока думаю")
async def contact_decline(message: types.Message):
    name = message.from_user.first_name or "друг"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("💰 Узнать цену", "📅 Узнать даты", "📍 Где проходят съёмки")
    await message.answer(
        f"Хорошо, {name} 🌿 Если что — я всегда рядом. Можете вернуться к любому вопросу 👇",
        reply_markup=keyboard
    )

# ---------- Render web ----------
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

async def main():
    bot_task = asyncio.create_task(dp.start_polling(bot))
    web_task = asyncio.create_task(web_server())
    await asyncio.gather(bot_task, web_task)

if __name__ == "__main__":
    logging.info("🚀 Запуск бота с веб-сервером...")
    asyncio.run(main())
