import logging
from enum import StrEnum
from typing import Callable, Awaitable, TypeVar, ParamSpec
from aiogram.types import Message

from utils.db import db, UserToken
from assets.text import (
    NOT_AUTHENTICATED, TODOIST_CONNECTION_FAILED, OPENROUTER_CONNECTION_FAILED
)


async def get_token_or_go_auth(message: Message) -> UserToken | None:
    token = await db.get_token(message.from_user.id)
    if not token:
        await message.answer(NOT_AUTHENTICATED, parse_mode="html")
        return
    return token


P = ParamSpec('P')
R = TypeVar('R')


class ConnectorType(StrEnum):
    OPENROUTER = "OPENROUTER"
    TODOIST = "TODOIST"


async def log_http_request(
    callback: Callable[P, Awaitable[R]],
    message: Message,
    connector: ConnectorType,
    *args: P.args,
    **kwargs: P.kwargs
) -> R | None:
    try:
        return await callback(*args, **kwargs)
    except Exception as e:
        logging.error(
            f"HTTP request failed for {connector}: {e}", exc_info=True
        )
        error_message = (
            TODOIST_CONNECTION_FAILED
            if connector == ConnectorType.TODOIST
            else OPENROUTER_CONNECTION_FAILED
        )
        try:
            await message.answer(error_message, parse_mode="html")
        except Exception as send_error:
            logging.error(f"Failed to send error message: {send_error}")
        return None
