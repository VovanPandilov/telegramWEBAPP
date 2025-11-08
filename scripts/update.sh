#!/usr/bin/env bash
set -e
LOG_DIR=/var/log/telegramwebapp
mkdir -p "$LOG_DIR"
cd "$(dirname "$0")/.."
cd "${APP_DIR:-/opt/telegramWEBAPP/app}/.."
git pull --ff-only origin "${REPO_BRANCH:-main}" | tee -a "$LOG_DIR/update.log"
systemctl restart telegramwebapp.service || true
