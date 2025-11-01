import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiohttp import web

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVICE_URL = os.getenv("SERVICE_URL")
PHOTOGRAPHER_ID = 1054983240  # ID куда будут отправляться заявки (замени на свой chat_id)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()  # <--- исправлено

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Главная клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💰 Узнать цены")],
        [KeyboardButton(text="📸 Виды съёмок")],
        [KeyboardButton(text="📅 Проверить свободные даты")],
        [KeyboardButton(text="⏳ Сроки и обработка")],
        [KeyboardButton(text="☎️ Хочу, чтобы со мной связались")]
    ],
    resize_keyboard=True
)

# Хранилище заявок
user_requests = {}


@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    name = message.from_user.first_name or "друг"
    text = (
        f"Привет, {name}! 🌿\n\n"
        f"Я Юля — ассистент фотографа 📸\n"
        f"Помогаю с выбором съёмки, расскажу про цены, сроки и помогу записаться.\n\n"
        f"Выберите пункт меню ниже 👇\n"
        f"Если у вас есть другой вопрос — просто напишите его, "
        f"и я передам Юле лично ❤️"
    )
    await message.answer(text, reply_markup=main_kb)


@dp.message_handler(lambda msg: msg.text == "💰 Узнать цены")
async def prices(msg: types.Message):
    text = (
        "💰 <b>Цены на фотосессии:</b>\n\n"
        "📷 <b>Индивидуальная</b> — от 120 BYN (1 час)\n"
        "👨‍👩‍👧 <b>Семейная</b> — от 150 BYN (1.5 часа)\n"
        "👶 <b>Детская</b> — от 130 BYN\n"
        "💞 <b>Love Story</b> — от 160 BYN\n"
        "🌇 <b>На улице / в помещении</b> — по выбору клиента\n"
        "🎉 <b>Мероприятия</b> — от 200 BYN (2 часа)\n"
        "💍 <b>Свадьба</b>:\n"
        "   • Только прогулка — от 250 BYN\n"
        "   • ЗАГС + прогулка — от 300 BYN\n"
        "   • Полдня — от 400 BYN\n"
        "   • Весь день — от 600 BYN\n\n"
        "📞 Все пакеты можно обсудить индивидуально ❤️"
    )
    await msg.answer(text, parse_mode="HTML")


@dp.message_handler(lambda msg: msg.text == "📸 Виды съёмок")
async def kinds(msg: types.Message):
    text = (
        "📸 <b>Виды фотосессий:</b>\n\n"
        "✨ Индивидуальная — студия, улица, интерьер.\n"
        "👨‍👩‍👧 Семейная — уютные кадры дома или на природе.\n"
        "👶 Детская — нежно, безопасно, с вниманием к деталям.\n"
        "💞 Love Story — история вашей любви, прогулка или студия.\n"
        "🎉 Мероприятия — крестины, дни рождения, корпоративы.\n"
        "💍 Свадьбы — от ЗАГСа до полного дня!\n\n"
        "🌿 Можем подобрать стиль под вас — классика, lifestyle, контент для Instagram."
    )
    await msg.answer(text, parse_mode="HTML")


@dp.message_handler(lambda msg: msg.text == "📅 Проверить свободные даты")
async def dates(msg: types.Message):
    await msg.answer(
        "📅 Напишите, пожалуйста, желаемую дату или диапазон (например, «15 ноября» или «20–25 ноября»). "
        "Я передам Юле, чтобы уточнила наличие 🌿"
    )


@dp.message_handler(lambda msg: msg.text == "⏳ Сроки и обработка")
async def timing(msg: types.Message):
    text = (
        "⏳ <b>Сроки и количество фото:</b>\n\n"
        "📷 Индивидуальная — 50 фото, готово через 7–10 дней.\n"
        "👨‍👩‍👧 Семейная — 70 фото, 10–12 дней.\n"
        "👶 Детская — 50 фото, 10 дней.\n"
        "💞 Love Story — 80 фото, 10–14 дней.\n"
        "🎉 Мероприятие — 100+ фото, 14 дней.\n"
        "💍 Свадьба — 300–600 фото, 3–4 недели.\n\n"
        "🖼 Все фото проходят цветокоррекцию, 10 лучших — художественная ретушь ✨"
    )
    await msg.answer(text, parse_mode="HTML")


@dp.message_handler(lambda msg: msg.text == "☎️ Хочу, чтобы со мной связались")
async def contact_request(msg: types.Message):
    user_id = msg.from_user.id
    user_data = user_requests.get(user_id, {})
    name = msg.from_user.full_name
    username = msg.from_user.username
    date_request = user_data.get("date")
    question = user_data.get("question")

    text_to_photographer = (
        f"📞 Новый клиент хочет связаться!\n\n"
        f"👤 Имя: {name}\n"
        f"@{username if username else 'без username'}\n"
        f"📅 Дата съёмки: {date_request or 'не указана'}\n"
        f"💬 Вопрос: {question or 'не было'}"
    )

    await bot.send_message(PHOTOGRAPHER_ID, text_to_photographer)
    await msg.answer("Спасибо 🌸 Юля свяжется с вами в ближайшее время!")


@dp.message_handler()
async def catch_all(msg: types.Message):
    user_id = msg.from_user.id
    text = msg.text

    # если человек писал дату
    if any(month in text.lower() for month in ["январ", "феврал", "март", "апрел", "май", "июн", "июл", "август", "сентябр", "октябр", "ноябр", "декабр"]):
        user_requests[user_id] = user_requests.get(user_id, {})
        user_requests[user_id]["date"] = text
        await msg.answer("📅 Я записала дату и передам Юле. Если хотите, чтобы она перезвонила — выберите пункт ☎️")
    else:
        user_requests[user_id] = user_requests.get(user_id, {})
        user_requests[user_id]["question"] = text
        await msg.answer("✍️ Ваш вопрос записан. Юля обязательно ознакомится! Чтобы связаться — нажмите ☎️")


# ---- WEBHOOK НА RENDER ----
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return web.Response()

async def on_startup(app):
    if SERVICE_URL:
        webhook_url = f"{SERVICE_URL}/webhook/{BOT_TOKEN}"
        await bot.set_webhook(webhook_url)
        logger.info(f"Webhook установлен: {webhook_url}")
    else:
        logger.warning("SERVICE_URL не задан — webhook не установлен!")

async def on_shutdown(app):
    logger.info("Удаление webhook...")
    await bot.delete_webhook()

def main():
    app = web.Application()
    app.router.add_post(f"/webhook/{BOT_TOKEN}", handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=10000)

if __name__ == "__main__":
    main()
