#!/bin/bash

# Скрипт для деплоя Agilite Scraper на CapRover

set -e

echo "🚀 Начинаем деплой Agilite Scraper на CapRover..."

# Проверяем, установлен ли CapRover CLI
if ! command -v caprover &> /dev/null; then
    echo "❌ CapRover CLI не установлен. Установите его командой:"
    echo "npm install -g caprover"
    exit 1
fi

# Проверяем, подключены ли мы к серверу
if ! caprover whoami &> /dev/null; then
    echo "❌ Не подключены к CapRover серверу. Выполните:"
    echo "caprover login"
    exit 1
fi

# Имя приложения
APP_NAME="agilite-scraper"

echo "📦 Создаем приложение $APP_NAME..."

# Создаем приложение (игнорируем ошибку, если уже существует)
caprover app create $APP_NAME || echo "Приложение уже существует"

echo "⚙️ Настраиваем переменные окружения..."

# Устанавливаем переменные окружения
caprover env set $APP_NAME SCHEDULE_HOURS=6

echo "🔨 Выполняем деплой..."

# Деплоим приложение
caprover deploy

echo "✅ Деплой завершен!"
echo ""
echo "📊 Для мониторинга используйте:"
echo "   caprover logs $APP_NAME"
echo "   caprover app status $APP_NAME"
echo ""
echo "🔄 Для обновления приложения:"
echo "   ./deploy.sh" 