from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.bot.keyboards import MAIN_MENU
from app.services import openai_chat

router = Router(name="chatgpt")


class ChatStates(StatesGroup):
    active = State()


@router.message(Command("gpt"))
@router.message(F.text.casefold() == "чат с gpt")
async def enter_chat(message: Message, state: FSMContext) -> None:
    await state.set_state(ChatStates.active)
    await message.answer(
        "Режим «Чат с GPT» активирован. Отправьте сообщение, чтобы получить ответ.\n"
        "Напишите «выход», чтобы вернуться в обычный режим.",
        reply_markup=MAIN_MENU,
    )


@router.message(StateFilter(ChatStates.active))
async def handle_chat(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()
    if not text:
        await message.answer("Сообщение пустое. Напишите что-нибудь.")
        return

    if text.lower() in {"выход", "стоп", "назад"}:
        await state.clear()
        await message.answer("Вы вышли из режима общения с GPT.", reply_markup=MAIN_MENU)
        return

    reply = await openai_chat.chat(text)
    await message.answer(reply)
