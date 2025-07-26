import json
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.llm import llm
from utils.todoist import todoist
from utils.db import db
from assets import text

todo_router = Router()


@todo_router.message(Command("add"))
async def add_handler(message: types.Message, state: FSMContext):
    await message.reply(text.ADD_TASK, parse_mode="html")
    await state.clear()


@todo_router.message(F.text)
async def create_new_task_handler(message: types.Message):
    token = await db.get_token(message.from_user.id)
    if not token:
        await message.answer(text.NOT_AUTHENTICATED, parse_mode="html")
        return

    new_message = await message.answer("Обрабатываем запрос.. 🤖")

    data = await llm.get_add_todo_data(message.text)
    data = json.loads(data)

    if not data:
        await new_message.edit_text(text.DID_NOT_UNDERSTAND, parse_mode="html")
        return

    if "due_datetime" in data:
        data["due_datetime"] = datetime.fromisoformat(data["due_datetime"])

    try:
        task = await todoist.create_task(token.access_token, data)
    except:
        await new_message.edit_text(text.CREATE_TASK_FAILED, parse_mode="html")
        return

    await new_message.edit_text(
        text.VIEW_TASK(task),
        parse_mode="html",
    )
