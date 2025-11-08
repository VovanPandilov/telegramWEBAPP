from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Чат с GPT"), KeyboardButton(text="Создать опрос")], [KeyboardButton(text="Помощь")]],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)
