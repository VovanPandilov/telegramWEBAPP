from __future__ import annotations

import hashlib
import hmac
import subprocess
from pathlib import Path

from fastapi import APIRouter, Header, HTTPException, Request, status
from loguru import logger

from app.deps import get_settings

router = APIRouter()
_settings = get_settings()

BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPT_PATH = BASE_DIR / "scripts" / "update.sh"


def verify_signature(payload: bytes, signature: str | None) -> None:
    if not signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Отсутствует подпись")

    secret = _settings.github_webhook_secret.encode()
    mac = hmac.new(secret, msg=payload, digestmod=hashlib.sha256)
    expected = f"sha256={mac.hexdigest()}"
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Неверная подпись")


@router.post("/github-webhook")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
) -> dict[str, str]:
    body = await request.body()
    verify_signature(body, x_hub_signature_256)

    event = (x_github_event or "").lower()
    if event == "ping":
        return {"status": "pong"}

    if event != "push":
        logger.info("Получено событие GitHub: {event}", event=event)
        return {"status": "ignored"}

    if not SCRIPT_PATH.exists():
        logger.error("Скрипт обновления не найден: {path}", path=str(SCRIPT_PATH))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Скрипт не найден")

    logger.info("Запуск скрипта обновления: {path}", path=str(SCRIPT_PATH))
    try:
        result = subprocess.run(
            ["/bin/bash", str(SCRIPT_PATH)],
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # pragma: no cover - защита от ошибок
        logger.exception("Не удалось выполнить скрипт обновления: {error}", error=exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка выполнения")

    if result.returncode != 0:
        logger.error(
            "Скрипт завершился с кодом {code}. STDOUT: {stdout} STDERR: {stderr}",
            code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Скрипт завершился с ошибкой")

    logger.info("Скрипт успешно выполнен. Вывод: {stdout}", stdout=result.stdout.strip())
    return {"status": "updated"}
