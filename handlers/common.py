from aiogram import types, Router
from aiogram.filters import Command
from assets.text import HELP_TEXT

common_router = Router()


@common_router.message(Command("help"))
async def help_handler(message: types.Message):
    await message.answer(HELP_TEXT, parse_mode="html")
