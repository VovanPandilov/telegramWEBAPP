from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Awaitable, List, Optional

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv
from loguru import logger
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    admins: List[int] = Field(default_factory=list, alias="ADMINS")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    http_proxy: Optional[str] = Field(default=None, alias="HTTP_PROXY")
    https_proxy: Optional[str] = Field(default=None, alias="HTTPS_PROXY")
    github_webhook_secret: str = Field(alias="GITHUB_WEBHOOK_SECRET")
    repo_branch: str = Field(default="main", alias="REPO_BRANCH")
    app_dir: str = Field(default="/opt/telegramWEBAPP/app", alias="APP_DIR")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    @validator("admins", pre=True)
    def split_admins(cls, value: str | List[int]) -> List[int]:  # type: ignore[override]
        if isinstance(value, list):
            return [int(v) for v in value]
        if not value:
            return []
        return [int(v.strip()) for v in value.split(",") if v.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    setup_logger()
    return settings


def setup_logger() -> None:
    if logger._core.handlers:  # type: ignore[attr-defined]
        return
    logger.remove()
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO",
        backtrace=True,
        diagnose=False,
    )


_settings = get_settings()

_proxy_url = _settings.http_proxy or _settings.https_proxy
_session = AiohttpSession(proxy=_proxy_url) if _proxy_url else AiohttpSession()

bot = Bot(token=_settings.bot_token, session=_session)
dispatcher = Dispatcher()

def create_task(coro: Awaitable[None]) -> asyncio.Task[None]:
    """Создать задачу с логированием ошибок."""

    async def runner() -> None:
        try:
            await coro
        except Exception as exc:  # pragma: no cover - логирование
            logger.exception("Фоновая задача завершилась с ошибкой: {error}", error=exc)

    return asyncio.create_task(runner())
