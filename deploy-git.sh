#!/bin/bash

# Bash скрипт для деплоя Agilite Scraper из Git на CapRover

set -e

echo "🚀 Начинаем деплой Agilite Scraper из Git на CapRover..."

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

echo "🔗 Настраиваем Git репозиторий..."

# Настраиваем Git репозиторий
caprover git set $APP_NAME --repo https://github.com/jsokol-hub/agilite_sales_inteligence_dashboard.git --branch dash

echo "🔨 Выполняем деплой из Git..."

# Деплоим приложение из Git
caprover deploy $APP_NAME

echo "✅ Деплой из Git завершен!"
echo ""
echo "📊 Для мониторинга используйте:"
echo "   caprover logs $APP_NAME"
echo "   caprover app status $APP_NAME"
echo ""
echo "🔄 Для обновления приложения:"
echo "   caprover deploy $APP_NAME"
echo ""
echo "📝 Git информация:"
echo "   Репозиторий: https://github.com/jsokol-hub/agilite_sales_inteligence_dashboard.git"
echo "   Ветка: dash" 