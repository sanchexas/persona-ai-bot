import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from db import init_db
from ai import generate_response
from config import config, load_config
from rag import add_lore_fact
from filters import IsOwner

bot = Bot(token=os.getenv("TG_BOT_TOKEN"))
dp = Dispatcher()

async def setup_admin_menu(owner_id: int):
    admin_commands = [
        BotCommand(command="start", description="Restart chat"),
        BotCommand(command="add_lore", description="[Admin] Add lore fact to RAG"),
        BotCommand(command="upload_character", description="[Admin] Update persona.txt"),
    ]
    await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=owner_id))

# --- Admin handlers ---

@dp.message(Command("add_lore"), IsOwner())
async def add_lore_handler(message: types.Message):
    command_args = message.text.split(maxsplit=1)
    if len(command_args) < 2:
        await message.answer("⚠️ Usage: `/add_lore Likes to ski`", parse_mode="Markdown")
        return

    fact_text = command_args[1].strip()
    await message.answer("⏳ Embedding and saving...")
    
    success = await add_lore_fact(fact_text)
    if success:
        await message.answer(f"✅ Successfully saved to memory:\n_\"{fact_text}\"_", parse_mode="Markdown")
    else:
        await message.answer("❌ Error while adding.")


@dp.message(Command("upload_character"), IsOwner())
async def upload_character_handler(message: types.Message):
    await message.answer("Send `persona.txt` as a document to this chat.")


@dp.message(F.document, IsOwner())
async def handle_persona_file(message: types.Message):
    if message.document and message.document.file_name == "persona.txt":
        file_path = config.get("path_to_persona_prompt_txt", "persona.txt")
        await bot.download(message.document, destination=file_path)
        load_config()
        await message.answer("✅ File `persona.txt` updated and reloaded!")

# --- User handlers ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    if message.from_user:
        is_owner = await IsOwner()(message)
        if is_owner:
            await setup_admin_menu(message.from_user.id)
            
    await message.answer(config.get("start_message", "Привет!"))

@dp.message()
async def message_handler(message: types.Message):
    if message.from_user and not IsOwner.is_assigned():
        is_owner = await IsOwner()(message)
        if is_owner:
            await setup_admin_menu(message.from_user.id)
            
    if not message.text:
        await message.answer(config.get("unsupported_message", "Только текст."))
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    response = await generate_response(message.chat.id, message.text)
    await message.answer(response)

async def main():
    await init_db()
    
    default_commands = [BotCommand(command="start", description="Start bot")]
    await bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())