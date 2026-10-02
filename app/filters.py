from aiogram.filters import Filter
from aiogram.types import Message
from aiogram import Bot

class IsOwner(Filter):
    def __init__(self):
        self._owner_id = None

    async def __call__(self, message: Message, bot: Bot):
        if self._owner_id is None:
            app_info = await bot.get_me()
            self._owner_id = app_info.id
        return message.from_user.id == self._owner_id