from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.bot import setup_dispatcher
from app.deps import bot, dispatcher
from app.routes import root, webhook_github
from loguru import logger


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.monotonic()
        logger.info("HTTP {method} {url}", method=request.method, url=str(request.url))
        try:
            response: Response = await call_next(request)
        except Exception as exc:  # pragma: no cover - защита от падений
            logger.exception("Ошибка при обработке запроса: {error}", error=exc)
            raise
        duration = (time.monotonic() - start) * 1000
        logger.info("Ответ {status} за {duration:.2f} мс", status=response.status_code, duration=duration)
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_dispatcher(dispatcher)
    polling_task: asyncio.Task | None = None
    try:
        polling_task = asyncio.create_task(dispatcher.start_polling(bot))
        yield
    finally:
        if polling_task:
            polling_task.cancel()
            with suppress(asyncio.CancelledError):
                await polling_task
        await bot.session.close()


app = FastAPI(title="telegramWEBAPP", lifespan=lifespan)
app.state.start_time = time.time()
app.add_middleware(LogMiddleware)
app.include_router(root.router)
app.include_router(webhook_github.router)


__all__ = ["app"]
