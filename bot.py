import asyncio
import logging

from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from config.core import Config
from utils.db import db
from handlers import common, auth, todo


async def main():
    Config.validate()
    logging.basicConfig(level=logging.ERROR)

    bot = Bot(token=Config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        common.common_router,
        auth.auth_router,
        todo.todo_router
    )

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Получить помощь"),

        BotCommand(command="authenticate",
                   description="Привязать Todoist аккаунт"),
        BotCommand(command="logout", description="Отвязать Todoist аккаунт"),

        BotCommand(command="add", description="Добавить задачу в Todoist"),
        BotCommand(
            command="daily_summary",
            description="Получить сводку на день"
        ),
        BotCommand(
            command="weekly_summary",
            description="Получить сводку на неделю"
        ),
    ])

    await db.init_db()

    try:
        print("Starting polling...")
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
