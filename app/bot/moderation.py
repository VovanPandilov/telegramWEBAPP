from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.services.security import is_admin

router = Router(name="moderation")


async def _handle_action(action: str, message: Message) -> None:
    user_id = message.from_user.id if message.from_user else 0
    if not user_id or not is_admin(user_id):
        await message.answer("Недостаточно прав для выполнения команды.")
        return

    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Укажите ID пользователя после команды.")
        return

    target = parts[1].strip()
    actions_map = {
        "ban": "Пользователь {target} был бы заблокирован (демо).",
        "unban": "Пользователь {target} был бы разблокирован (демо).",
        "mute": "Пользователь {target} был бы ограничен (демо).",
        "unmute": "Пользователь {target} был бы восстановлен (демо).",
    }
    answer = actions_map.get(action, "Команда выполнена.").format(target=target)
    await message.answer(answer)


@router.message(Command("ban"))
async def cmd_ban(message: Message) -> None:
    await _handle_action("ban", message)


@router.message(Command("unban"))
async def cmd_unban(message: Message) -> None:
    await _handle_action("unban", message)


@router.message(Command("mute"))
async def cmd_mute(message: Message) -> None:
    await _handle_action("mute", message)


@router.message(Command("unmute"))
async def cmd_unmute(message: Message) -> None:
    await _handle_action("unmute", message)
