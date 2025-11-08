from __future__ import annotations

from app.deps import get_settings


_settings = get_settings()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором."""
    return user_id in _settings.admins
