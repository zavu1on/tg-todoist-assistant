import logging
from uuid import uuid4
from aiogram import types, Router, F
from aiogram.filters import Command, CommandStart, CommandObject

from utils.db import db
from utils.auth import todoist_auth
from utils.helpers import log_http_request, ConnectorType
from assets import text


auth_router = Router()


@auth_router.message(Command("authenticate"))
async def authenticate_handler(message: types.Message):
    token = await db.get_token(message.from_user.id)
    if token:
        await message.answer(text.ALREADY_AUTHENTICATED, parse_mode="html")
        return

    auth_state = str(uuid4())
    url = todoist_auth.get_auth_url(auth_state)

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Авторизоваться в Todoist", url=url)]
    ])

    await message.answer(text.START_AUTH, parse_mode="html", reply_markup=keyboard)


@auth_router.message(CommandStart())
async def start_handler(message: types.Message, command: CommandObject):
    args = command.args

    if not args:
        token = await db.get_token(message.from_user.id)

        await message.answer(
            text.START_WITH_AUTH if token else text.START_WITHOUT_AUTH,
            parse_mode="html"
        )
    else:
        if args == "auth_failed":
            await message.answer(text.AUTH_FAILED, parse_mode="html")
            return

        response = await log_http_request(
            todoist_auth.get_access_token,
            message,
            ConnectorType.TODOIST,
            args
        )
        if response is None:
            return

        await db.save_token(message.from_user.id, response["access_token"])

        await message.answer(text.AUTH_SUCCESS, parse_mode="html")


@auth_router.message(Command("logout"))
async def logout_handler(message: types.Message):
    token = await db.get_token(message.from_user.id)
    if not token:
        await message.answer(text.LOGOUT_WITHOUT_AUTH, parse_mode="html")
        return

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="Да, отвязать Todoist аккаунт",
            callback_data=f"confirm_logout_{message.from_user.id}"
        )
    ]])

    await message.answer(text.CONFIRM_LOGOUT, parse_mode="html", reply_markup=keyboard)


@auth_router.callback_query(F.data.contains("confirm_logout_"))
async def confirm_logout_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.data.split("confirm_logout_")[1]
    token = await db.get_token(user_id)

    success = await log_http_request(
        todoist_auth.reveal_access_token,
        callback_query.message,
        ConnectorType.TODOIST,
        token.access_token
    )
    if success is None:
        return

    await db.reveal_token(callback_query.from_user.id)

    await callback_query.message.edit_text(
        text.LOGOUT_SUCCESS if success else text.LOGOUT_FAILED,
        parse_mode="html"
    )
    await callback_query.answer()
