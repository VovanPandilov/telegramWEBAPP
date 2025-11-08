# telegramWEBAPP

Полноценное приложение на FastAPI с Telegram-ботом (aiogram 3) и интеграцией OpenAI. Проект рассчитан на запуск на VPS, локально и в Termux без Docker.

## Требования
- Python 3.11
- Git
- Установленные системные зависимости для `uvicorn`, `gunicorn` и `aiogram` (libffi, openssl, curl и т.д.)

## Установка
```bash
git clone https://github.com/your-account/telegramWEBAPP.git
cd telegramWEBAPP
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Отредактируйте `.env`, указав реальные значения токена бота, ключа OpenAI и остальных настроек.

## Запуск в режиме разработки
```bash
./scripts/run_dev.sh
```
По умолчанию приложение будет доступно на `http://127.0.0.1:8000`.

## Структура проекта
```
app/            # Код FastAPI и бота
scripts/        # Служебные скрипты запуска и обновления
systemd/        # Unit-файлы для деплоя на сервер
```

## Развёртывание на сервере (systemd)
Скопируйте файлы сервисов и перезапустите демоны:
```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telegramwebapp.service
sudo systemctl enable --now telegramwebhook.service
```

Перед запуском создайте директорию `/opt/telegramWEBAPP`, скопируйте туда проект и `.env`. В unit-файле `telegramwebapp.service` заполните параметр `User=` пользователем, от имени которого будет работать сервис.

## GitHub Webhook
- URL: `http://<IP>:9000/github-webhook`
- Content type: `application/json`
- Secret: значение `GITHUB_WEBHOOK_SECRET`
- События: `push`

При получении `push`-события будет выполнен `scripts/update.sh`, который сделает `git pull` и перезапустит сервис `telegramwebapp.service`.

## Telegram-бот
Основные команды:
- `/start` — приветствие и главное меню.
- `/help` — краткая справка.
- `/poll "Вопрос" "Ответ1" "Ответ2" ...` — создать опрос в текущем чате.
- `/admin` — административная информация (только для ID из `ADMINS`).
- `/ban`, `/unban`, `/mute`, `/unmute` — демонстрационные команды модерирования.

Кнопка «Чат с GPT» включает режим общения с моделью OpenAI (ответы короткие, без Markdown). Чтобы выйти из режима, напишите «выход».

## Обновление проекта вручную
```bash
cd /opt/telegramWEBAPP
git pull
sudo systemctl restart telegramwebapp.service
```

Проект готов к использованию после настройки `.env` и установки зависимостей.
