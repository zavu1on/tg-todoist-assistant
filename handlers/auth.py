from uuid import uuid4
from aiogram import types, Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from utils.db import db
from utils.auth import todoist_auth
from assets import text


auth_router = Router()


@auth_router.message(Command("authenticate"))
async def authenticate_handler(message: types.Message, state: FSMContext):
    token = await db.get_token(message.from_user.id)
    if token:
        await message.answer(text.ALREADY_AUTHENTICATED, parse_mode="html")
        await state.clear()
        return

    auth_state = str(uuid4())
    url = todoist_auth.get_auth_url(auth_state)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Авторизоваться в Todoist", url=url)]
    ])

    await message.answer(text.START_AUTH, parse_mode="html", reply_markup=keyboard)
    await state.clear()


@auth_router.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject, state: FSMContext):
    args = command.args

    if not args:
        token = await db.get_token(message.from_user.id)

        await message.answer(
            text.START_WITH_AUTH if token else text.START_WITHOUT_AUTH,
            parse_mode="html"
        )
        await state.clear()
    else:
        if args == "auth_failed":
            await message.answer(text.AUTH_FAILED, parse_mode="html")
            await state.clear()
            return

        response = await todoist_auth.get_access_token(args)
        await db.save_token(message.from_user.id, response["access_token"])

        await message.answer(text.AUTH_SUCCESS, parse_mode="html")
        await state.clear()


@auth_router.message(Command("logout"))
async def logout_handler(message: types.Message, state: FSMContext):
    token = await db.get_token(message.from_user.id)
    if not token:
        await message.answer("Todoist и так не привязан 🤗", parse_mode="html")
        await state.clear()
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="Да, отвязать Todoist аккаунт",
            callback_data="confirm_logout"
        )
    ]])

    await message.answer(text.CONFIRM_LOGOUT, parse_mode="html", reply_markup=keyboard)
    await state.clear()


@auth_router.callback_query(F.data == "confirm_logout")
async def confirm_logout_callback(callback_query: types.CallbackQuery, state: FSMContext):
    token = await db.get_token(callback_query.message.from_user.id)

    success = await todoist_auth.reveal_access_token(token.access_token)
    await db.reveal_token(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text.LOGOUT_SUCCESS if success else text.LOGOUT_FAILED,
        parse_mode="html"
    )
    await callback_query.answer()
    await state.clear()
