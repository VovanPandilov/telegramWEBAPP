from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message

from app.bot.keyboards import MAIN_MENU
from app.services.security import is_admin

router = Router(name="base_handlers")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бот telegramWEBAPP. Используйте меню ниже, чтобы начать работу.",
        reply_markup=MAIN_MENU,
    )


HELP_TEXT = (
    "Доступные команды:\n"
    "/start — приветствие и главное меню.\n"
    "/help — показать эту справку.\n"
    "/poll \"Вопрос\" \"Ответ1\" \"Ответ2\" … — создать опрос.\n"
    "Кнопка «Чат с GPT» включает режим общения с моделью OpenAI.\n"
    "Команда /admin показывает административную информацию."
)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=MAIN_MENU)


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if not user_id or not is_admin(user_id):
        await message.answer("Эта команда доступна только администраторам.")
        return

    await message.answer(
        "Админ панель\n"
        f"Ваш ID: {user_id}\n"
        "Доступные команды: /ban /unban /mute /unmute\n"
        "Помните, что это демонстрационная версия без настоящих действий.",
        reply_markup=MAIN_MENU,
    )


@router.message(StateFilter(None))
async def fallback(message: Message) -> None:
    text = (message.text or "").strip()
    if text.lower() == "помощь":
        await message.answer(HELP_TEXT, reply_markup=MAIN_MENU)
        return

    await message.answer(
        "Я вас не понял. Используйте кнопки меню или команду /help для подсказки.",
        reply_markup=MAIN_MENU,
    )
