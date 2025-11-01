import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# Включаем логи (чтобы видеть вывод на Render)
logging.basicConfig(level=logging.INFO)

# Получаем токен из переменной окружения (Render -> Environment)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка на случай, если токен не найден
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден. Добавь его в Render Environment!")

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Привет 👋! Я помощник фотографа. Чем могу помочь?")

# Обработчик любого другого текста
@dp.message()
async def echo_message(message: types.Message):
    await message.answer("Спасибо за сообщение! Скоро я научусь отвечать умнее 😊")

# Основная функция запуска
async def main():
    logging.info("🚀 Запуск бота...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())