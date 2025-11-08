from __future__ import annotations

import shlex

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="polls")


@router.message(F.text.casefold() == "создать опрос")
async def poll_help(message: Message) -> None:
    await message.answer(
        "Используйте команду /poll в формате:\n"
        "/poll \"Вопрос\" \"Ответ 1\" \"Ответ 2\"\n"
        "Можно добавить больше вариантов ответов.",
    )


@router.message(Command("poll"))
async def create_poll(message: Message) -> None:
    text = message.text or ""
    try:
        parts = shlex.split(text)
    except ValueError:
        await message.answer("Не удалось разобрать команду. Проверьте кавычки.")
        return

    if len(parts) < 4:
        await message.answer(
            "Недостаточно аргументов. Укажите вопрос и минимум два варианта ответа."
        )
        return

    _, question, *options = parts
    if len(question) > 255:
        await message.answer("Вопрос слишком длинный.")
        return

    if any(len(opt) > 100 for opt in options):
        await message.answer("Один из вариантов ответа слишком длинный.")
        return

    await message.answer_poll(
        question=question,
        options=options,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
