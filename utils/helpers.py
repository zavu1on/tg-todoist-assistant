from aiogram.types import Message

from utils.db import db, UserToken
from assets.text import NOT_AUTHENTICATED


async def get_token_or_go_auth(message: Message) -> UserToken | None:
    token = await db.get_token(message.from_user.id)
    if not token:
        await message.answer(NOT_AUTHENTICATED, parse_mode="html")
        return
    return token
