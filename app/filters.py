from typing import Optional
from aiogram.filters import Filter
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

class IsOwner(Filter):
    _owner_id: Optional[int] = None

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        current_user_id = message.from_user.id

        if IsOwner._owner_id is not None:
            return current_user_id == IsOwner._owner_id
       
        IsOwner._owner_id = current_user_id
        return True

    @classmethod
    def get_owner_id(cls) -> Optional[int]:
        return cls._owner_id

    @classmethod
    def is_assigned(cls) -> bool:
        return cls._owner_id is not None