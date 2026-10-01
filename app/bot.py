import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from db import init_db
from ai import generate_response
from config import config

bot = Bot(token=os.getenv("TG_BOT_TOKEN"))
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(config["start_message"])

@dp.message()
async def message_handler(message: types.Message):
    if message.text is None:
        await message.answer(config["unsupported_message"])
        return

    response = await generate_response(message.chat.id, message.text)
    await message.answer(response)


async def main():
    await init_db()
    print(f"[{config['bot_name']}] bot is running...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())