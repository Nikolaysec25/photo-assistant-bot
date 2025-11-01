# bot.py — webhook-ready для Render
import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
PHOTOGRAPHER_CHAT_ID = os.getenv("PHOTOGRAPHER_CHAT_ID")  # строка, например "123456789"

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не задан в Environment")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# --- клавиатура главного меню ---
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
        "Выберите пункт ниже 👇",
        reply_markup=main_menu()
    )

@dp.message()
async def generic_handler(message: types.Message):
    text = (message.text or "").lower()
    name = message.from_user.first_name or "друг"

    # простая логика ответов — расширяй по ключам
    if "цена" in text or "узнать цены" in text or "стоимость" in text:
        await message.answer(f"{name}, базовые цены:\n• Индивид — от 120 BYN\n• Семья — от 150 BYN\n\nЕсли хотите — нажмите «☎️ Хочу, чтобы со мной связались»", reply_markup=main_menu())
        return
    if "вид" in text or "види" in text or "съёмк" in text:
        await message.answer(f"{name}, провожу: индивидуальная, семейная, детская, love story, мероприятия.\n\nМогу проверить даты или зарезервировать.", reply_markup=main_menu())
        return
    if "дата" in text or "свободн" in text:
        await message.answer(f"{name}, напишите, пожалуйста, примерный день/период (например «14 ноября»), и я проверю.", reply_markup=main_menu())
        return

    # кнопки: если пользователь нажал кнопку "☎️ Хочу, чтобы со мной связались"
    if text == "☎️ хочу, чтобы со мной связались" or text == "хочу, чтобы со мной связались":
        await message.answer(f"Спасибо, {name}! Я передал фотографу вашу заявку. Он свяжется с вами.", reply_markup=main_menu())
        # уведомление фотографу
        if PHOTOGRAPHER_CHAT_ID:
            try:
                await bot.send_message(
                    PHOTOGRAPHER_CHAT_ID,
                    f"📞 <b>Новый запрос на обратный звонок</b>\n\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Username: @{message.from_user.username or '—'}\n"
                    f"ID: {message.from_user.id}\n"
                    f"Сообщение: {message.text}"
                )
            except Exception as e:
                logger.exception("Не удалось отправить уведомление фотографу")
        return

    # fallback
    await message.answer(f"{name}, выберите пункт меню или напишите ваш вопрос.", reply_markup=main_menu())


# ------------- WEBHOOK server (aiohttp) -------------
# Path для webhook: /webhook/<token>
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", "10000"))  # Render задаёт PORT автоматически

async def handle_webhook(request: web.Request):
    # Telegram присылает JSON — прокинем в aiogram
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="no json")

    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

async def on_startup(app: web.Application):
    # Set webhook to Render URL
    # Получаем PRIMARY URL из переменной окружения (RENDER задаёт не всегда), или формируем из переменной, попросим пользователя вставить SERVICE_URL
    SERVICE_URL = os.getenv("SERVICE_URL")  # обязательно установи: https://your-service.onrender.com
    if not SERVICE_URL:
        logger.warning("SERVICE_URL не задан — webhook не будет установлен автоматически. Установи SERVICE_URL в Environment (https://your-service.onrender.com)")
    else:
        webhook_url = SERVICE_URL.rstrip("/") + WEBHOOK_PATH
        logger.info(f"Setting webhook: {webhook_url}")
        await bot.set_webhook(webhook_url)

async def on_shutdown(app: web.Application):
    logger.info("Shutdown: removing webhook")
    try:
        await bot.delete_webhook()
    except Exception:
        pass
    await bot.session.close()

def run_webapp():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_shutdown)
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    logger.info("Starting webhook server...")
    run_webapp()
