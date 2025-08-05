import json
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command

from utils.db import db
from utils.llm import llm
from utils.todoist import todoist
from utils.logger import logger
from utils.helpers import (
    get_token_or_go_auth,
    log_http_request,
    get_task_prompt_data,
    ConnectorType
)
from assets import text

todo_router = Router()


@todo_router.message(Command("add"))
async def add_handler(message: types.Message):
    await message.answer(text.ADD_TASK, parse_mode="html")


@todo_router.message(Command("daily_summary"))
async def get_daily_summary(message: types.Message):
    token = await get_token_or_go_auth(message)
    if not token:
        return

    new_message = await message.answer("Собираем сводку на день.. 🤖")

    tasks = await log_http_request(
        todoist.get_daily_tasks,
        message,
        ConnectorType.TODOIST,
        token.access_token
    )
    if tasks is None:
        return

    tasks_prompt = get_task_prompt_data(tasks)
    logger.info(f"Summarize tasks prompt: {tasks_prompt}")

    response = await log_http_request(
        llm.get_daily_summary,
        message,
        ConnectorType.OPENROUTER,
        tasks_prompt
    )
    if response is None:
        return

    await new_message.edit_text(response, parse_mode="Markdown")


@todo_router.message(Command("weekly_summary"))
async def get_daily_summary(message: types.Message):
    token = await get_token_or_go_auth(message)
    if not token:
        return

    new_message = await message.answer("Собираем сводку на неделю.. 🤖")

    tasks = await log_http_request(
        todoist.get_weekly_tasks,
        message,
        ConnectorType.TODOIST,
        token.access_token
    )
    if tasks is None:
        return

    tasks_prompt = get_task_prompt_data(tasks)
    logger.info(f"Summarize tasks prompt: {tasks_prompt}")

    response = await log_http_request(
        llm.get_weekly_summary,
        message,
        ConnectorType.OPENROUTER,
        tasks_prompt
    )
    if response is None:
        return

    await new_message.edit_text(response, parse_mode="Markdown")


def get_delete_task_keyboard(user_id: str, task_id: str):
    return types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(
            text="Не сохранять в Todoist",
            callback_data=f"delete_task_{user_id}_{task_id}"
        )
    ]])


@todo_router.message(F.text)
async def create_new_task_handler(message: types.Message):
    token = await get_token_or_go_auth(message)
    if not token:
        return

    new_message = await message.reply("Обрабатываем запрос.. 🤖")

    data = await log_http_request(
        llm.get_add_todo_data,
        message,
        ConnectorType.OPENROUTER,
        message.text
    )
    if data is None:
        return

    data: list[dict] = json.loads(data)

    if not data:
        logger.warning(f"Did not understand: {message.text}")
        await new_message.edit_text(text.DID_NOT_UNDERSTAND, parse_mode="html")
        return
    for obj in data:
        if "due_datetime" in obj and obj["due_datetime"]:
            obj["due_datetime"] = datetime.fromisoformat(obj["due_datetime"])
        else:
            obj["due_datetime"] = None
    try:
        tasks = []
        for obj in data:
            task = await todoist.create_task(token.access_token, obj)
            tasks.append(task)
    except Exception as error:
        logger.error("Failed to create task", exc_info=error)
        await new_message.edit_text(text.ADD_TASK_FAILED, parse_mode="html")
        return

    logger.info(f"Created task: {data}")

    await new_message.edit_text(
        text.VIEW_TASK(tasks[0]),
        parse_mode="html",
        reply_markup=get_delete_task_keyboard(
            message.from_user.id, tasks[0].id
        )
    )
    for task in tasks[1:]:
        await message.reply(
            text.VIEW_TASK(task),
            parse_mode="html",
            reply_markup=get_delete_task_keyboard(
                message.from_user.id, task.id
            )
        )


@todo_router.callback_query(F.data.contains("delete_task_"))
async def delete_task_callback(callback_query: types.CallbackQuery):
    user_id, task_id = callback_query.data.split("delete_task_")[1].split("_")
    token = await db.get_token(user_id)

    success = await log_http_request(
        todoist.delete_task,
        callback_query,
        ConnectorType.TODOIST,
        token.access_token,
        task_id
    )
    await callback_query.message.edit_text(
        text.DELETE_TASK_SUCCESS if success else text.DELETE_TASK_FAILED,
        parse_mode="html"
    )
