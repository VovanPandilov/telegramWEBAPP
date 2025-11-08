from __future__ import annotations

import time

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
async def read_root() -> dict[str, str]:
    return {"status": "ok", "name": "telegramWEBAPP"}


@router.get("/health")
async def health(request: Request) -> dict[str, float]:
    start_time = getattr(request.app.state, "start_time", time.time())
    uptime = time.time() - start_time
    return {"status": "ok", "uptime": round(uptime, 2)}
