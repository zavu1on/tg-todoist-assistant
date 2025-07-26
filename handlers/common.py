from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

common_router = Router()


@common_router.message(Command("help"))
async def help_handler(message: types.Message, state: FSMContext):
    await message.reply("Я еще в разработке...")
    await state.clear()
