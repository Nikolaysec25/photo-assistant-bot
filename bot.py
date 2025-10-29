# bot.py
import os
import asyncio
from aiogram import Bot, Dispatcher, types

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("Нужна переменная окружения BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(commands=["start"])
async def cmd_start(event: types.Message):
    await event.reply("Привет! Я — помощник фотографа. Напиши 'цены' или 'запись'.")

@dp.message()
async def all_messages(message: types.Message):
    text = message.text.lower()
    if "цены" in text:
        await message.reply("Цены: Мини-съёмка — 80 BYN/час. Полная информация по запросу.")
    elif "запись" in text or "дата" in text:
        await message.reply("Напиши желаемую дату в формате DD.MM.YYYY, я проверю свободные окна.")
    else:
        await message.reply("Могу помочь с ценами, записью и организацией съёмки.")

async def main():
    try:
        print("Запуск бота...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
