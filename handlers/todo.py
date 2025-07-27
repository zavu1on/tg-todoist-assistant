import json
import logging
from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import Command

from utils.llm import llm
from utils.todoist import todoist
from utils.helpers import get_token_or_go_auth
from assets import text

todo_router = Router()


@todo_router.message(Command("add"))
async def add_handler(message: types.Message):
    await message.reply(text.ADD_TASK, parse_mode="html")


@todo_router.message(Command("daily_summary"))
async def get_daily_summary(message: types.Message):
    token = await get_token_or_go_auth(message)
    if not token:
        return

    new_message = await message.answer("Собираем сводку на день.. 🤖")

    tasks = await todoist.get_daily_tasks(token.access_token)
    tasks_prompt = json.dumps([
        {
            "content": task.content,
            "description": task.description,
            "priority": task.priority or 0,
            "due_datetime": task.due.date.isoformat() if task.due else None,
            "labels": task.labels,
        } for task in tasks
    ], ensure_ascii=False)
    response = await llm.get_daily_summary(tasks_prompt)

    await new_message.edit_text(response, parse_mode="Markdown")


@todo_router.message(Command("weekly_summary"))
async def get_daily_summary(message: types.Message):
    token = await get_token_or_go_auth(message)
    if not token:
        return

    new_message = await message.answer("Собираем сводку на неделю.. 🤖")

    tasks = await todoist.get_weekly_tasks(token.access_token)
    tasks_prompt = json.dumps([
        {
            "content": task.content,
            "description": task.description,
            "priority": task.priority or 0,
            "due_datetime": task.due.date.isoformat() if task.due else None,
            "labels": task.labels,
        } for task in tasks
    ], ensure_ascii=False)
    response = await llm.get_weekly_summary(tasks_prompt)

    await new_message.edit_text(response, parse_mode="Markdown")


@todo_router.message(F.text)
async def create_new_task_handler(message: types.Message):
    token = await get_token_or_go_auth(message)
    if not token:
        return

    new_message = await message.answer("Обрабатываем запрос.. 🤖")

    data = await llm.get_add_todo_data(message.text)
    data: list[dict] = json.loads(data)

    if not data:
        logging.warning(f"Did not understand: {message.text}")
        await new_message.edit_text(text.DID_NOT_UNDERSTAND, parse_mode="html")
        return
    for obj in data:
        if "due_datetime" in obj:
            obj["due_datetime"] = datetime.fromisoformat(obj["due_datetime"])

    logging.info(f"Create task: {data}")

    try:
        tasks = []
        for obj in data:
            task = await todoist.create_task(token.access_token, obj)
            tasks.append(task)
    except:
        await new_message.edit_text(text.CREATE_TASK_FAILED, parse_mode="html")
        return

    await new_message.edit_text(
        text.VIEW_TASK(tasks[0]),
        parse_mode="html",
    )
    for task in tasks[1:]:
        await message.answer(text.VIEW_TASK(task), parse_mode="html")
