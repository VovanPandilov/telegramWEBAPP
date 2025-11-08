#!/usr/bin/env bash
set -e
[ -f .env ] && export $(grep -v '^#' .env | xargs)
exec uvicorn app.main:app --host "${APP_HOST:-0.0.0.0}" --port "${APP_PORT:-8000}" --reload
