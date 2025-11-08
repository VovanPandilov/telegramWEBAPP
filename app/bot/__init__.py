from __future__ import annotations

from aiogram import Dispatcher

from app.bot import chatgpt, handlers, moderation, polls

__all__ = ["setup_dispatcher"]


def setup_dispatcher(dispatcher: Dispatcher) -> None:
    """Подключить все роутеры aiogram."""
    dispatcher.include_router(chatgpt.router)
    dispatcher.include_router(polls.router)
    dispatcher.include_router(moderation.router)
    dispatcher.include_router(handlers.router)
