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

# --- Для хранения состояния новых пользователей (можно заменить на базу) ---
seen_users = set()

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

# --- приветствие пользователя только один раз ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.first_name or "друг"

    if user_id not in seen_users:
        seen_users.add(user_id)
        await message.answer(
            f"Привет, {name}! 👋\n"
            "Меня зовут Юля — я помощник фотографа 🌿.\n"
            "Выберите пункт ниже 👇"
            "\nЕсли у вас есть вопрос, которого нет в меню, напишите его, и я передам фотографу.",
            reply_markup=main_menu()
        )
    else:
        await message.answer(
            f"С возвращением, {name}! 🌸\nВыберите пункт меню ниже 👇",
            reply_markup=main_menu()
        )

# --- обработчик всех сообщений ---
@dp.message()
async def generic_handler(message: types.Message):
    text = (message.text or "").lower()
    name = message.from_user.first_name or "друг"
    user_id = message.from_user.id

    # --- Цены ---
    if "💰" in text or "цена" in text or "узнать цены" in text:
        prices_text = (
            "💰 <b>Цены на съёмки</b>:\n\n"
            "• Индивидуальная: 120 BYN/час\n"
            "• Семейная: 150 BYN/час\n"
            "• Детская: 100 BYN/час\n"
            "• Love story (улица / интерьер): 120 BYN/час\n"
            "• Мероприятия: от 200 BYN/час\n"
            "• Свадьбы: час — 150 BYN, день — 350 BYN, полдня — 200 BYN\n"
            "• Только прогулка — 100 BYN\n"
            "• Только ЗАГС — 80 BYN\n"
        )
        await message.answer(prices_text, reply_markup=main_menu())
        return

    # --- Виды съёмок ---
    if "📸" in text or "вид" in text or "съёмк" in text:
        types_text = (
            "📸 <b>Виды съёмок</b>:\n\n"
            "• Индивидуальная — стильные портреты, outdoor/indoor\n"
            "• Семейная — уютные фото всей семьи\n"
            "• Детская — яркие и живые моменты\n"
            "• Love Story — романтика на улице или в помещении\n"
            "• Мероприятия — вечеринки, события\n"
            "• Свадьбы — полный день, полдня, только прогулка, только ЗАГС\n"
        )
        await message.answer(types_text, reply_markup=main_menu())
        return

    # --- Проверка свободных дат ---
    if "📅" in text or "дата" in text or "свободн" in text:
        await message.answer(
            f"{name}, напишите, пожалуйста, дату или период, который вас интересует.\n"
            "Я передам фотографу, и он свяжется с вами.",
            reply_markup=main_menu()
        )
        # сохраняем дату для последующей передачи
        if PHOTOGRAPHER_CHAT_ID:
            try:
                await bot.send_message(
                    PHOTOGRAPHER_CHAT_ID,
                    f"📅 <b>Запрос на дату</b>\n\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Username: @{message.from_user.username or '—'}\n"
                    f"ID: {message.from_user.id}\n"
                    f"Запрошенная дата: {message.text}"
                )
            except Exception as e:
                logger.exception("Не удалось отправить дату фотографу")
        return

    # --- Сроки и обработка ---
    if "⏳" in text or "срок" in text or "обработк" in text:
        deadlines_text = (
            "⏳ <b>Сроки и обработка</b>:\n\n"
            "• Индивидуальная: 50 фото, 5 дней\n"
            "• Семейная: 60 фото, 6 дней\n"
            "• Детская: 40 фото, 4 дня\n"
            "• Love Story: 50 фото, 5 дней\n"
            "• Мероприятия: 100 фото, 7 дней\n"
            "• Свадьбы: 200 фото полный день — 10 дней, полдня — 6 дней\n"
        )
        await message.answer(deadlines_text, reply_markup=main_menu())
        return

    # --- Обратный звонок ---
    if "☎️" in text or "хочу, чтобы со мной связались" in text:
        await message.answer(
            f"Спасибо, {name}! Я передал фотографу вашу заявку. Он свяжется с вами.",
            reply_markup=main_menu()
        )
        if PHOTOGRAPHER_CHAT_ID:
            try:
                await bot.send_message(
                    PHOTOGRAPHER_CHAT_ID,
                    f"📞 <b>Новый запрос на обратный звонок</b>\n\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Username: @{message.from_user.username or '—'}\n"
                    f"ID: {message.from_user.id}\n"
                    f"Доп. вопрос клиента: {message.text}"
                )
            except Exception as e:
                logger.exception("Не удалось отправить заявку фотографу")
        return

    # --- fallback ---
    # если пользователь написал что-то не из меню
    if PHOTOGRAPHER_CHAT_ID:
        try:
            await bot.send_message(
                PHOTOGRAPHER_CHAT_ID,
                f"❓ <b>Вопрос клиента</b>\n\n"
                f"Имя: {message.from_user.full_name}\n"
                f"Username: @{message.from_user.username or '—'}\n"
                f"ID: {message.from_user.id}\n"
                f"Вопрос: {message.text}"
            )
        except Exception as e:
            logger.exception("Не удалось отправить вопрос фотографу")
    await message.answer(
        f"{name}, спасибо за сообщение! Оно передано фотографу. Пожалуйста, выберите пункт меню ниже 👇",
        reply_markup=main_menu()
    )


# ------------- WEBHOOK server (aiohttp) -------------
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", "10000"))  # Render задаёт PORT автоматически

async def handle_webhook(request: web.Request):
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="no json")
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

async def on_startup(app: web.Application):
    SERVICE_URL = os.getenv("SERVICE_URL")  # https://your-service.onrender.com
    if SERVICE_URL:
        webhook_url = SERVICE_URL.rstrip("/") + WEBHOOK_PATH
        logger.info(f"Setting webhook: {webhook_url}")
        await bot.set_webhook(webhook_url)
    else:
        logger.warning("SERVICE_URL не задан — webhook не будет установлен автоматически.")

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
