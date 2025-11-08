from __future__ import annotations

import asyncio
from typing import Dict, Optional

import httpx
from loguru import logger
from openai import AsyncOpenAI

from app.deps import get_settings


_settings = get_settings()

_proxies: Dict[str, str] = {}
if _settings.http_proxy:
    _proxies["http"] = _settings.http_proxy
if _settings.https_proxy:
    _proxies["https"] = _settings.https_proxy

_http_client = httpx.AsyncClient(timeout=20.0, proxies=_proxies or None)
_client = AsyncOpenAI(api_key=_settings.openai_api_key, http_client=_http_client)


async def chat(user_text: str) -> str:
    """Отправить запрос к OpenAI и вернуть краткий ответ."""
    cleaned_text = user_text.strip()
    if not cleaned_text:
        return "Пожалуйста, отправьте непустой запрос."

    try:
        response = await _client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "system",
                    "content": "Ты дружелюбный ассистент. Отвечай кратко, без Markdown и списков.",
                },
                {"role": "user", "content": cleaned_text},
            ],
            max_output_tokens=400,
        )
    except httpx.HTTPError as exc:
        logger.exception("Ошибка сети при обращении к OpenAI: {error}", error=exc)
        return "Не удалось связаться с OpenAI. Попробуйте позже."
    except asyncio.TimeoutError:
        logger.warning("Запрос к OpenAI превысил лимит по времени")
        return "OpenAI не ответил вовремя. Повторите попытку."
    except Exception as exc:  # pragma: no cover - безопасное логирование
        logger.exception("Неожиданная ошибка OpenAI: {error}", error=exc)
        return "Произошла ошибка при обращении к OpenAI."

    text_chunks = []
    for item in response.output or []:  # type: ignore[attr-defined]
        for content in getattr(item, "content", []) or []:
            value: Optional[str] = getattr(content, "text", None)
            if value:
                text_chunks.append(value)

    final_text = " ".join(text_chunks).strip()
    if not final_text:
        final_text = "OpenAI не прислал ответ."
    return final_text
