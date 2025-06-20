# PowerShell скрипт для деплоя Agilite Scraper на CapRover

Write-Host "🚀 Начинаем деплой Agilite Scraper на CapRover..." -ForegroundColor Green

# Проверяем, установлен ли CapRover CLI
try {
    $null = Get-Command caprover -ErrorAction Stop
} catch {
    Write-Host "❌ CapRover CLI не установлен. Установите его командой:" -ForegroundColor Red
    Write-Host "npm install -g caprover" -ForegroundColor Yellow
    exit 1
}

# Проверяем, подключены ли мы к серверу
try {
    $null = caprover whoami 2>$null
} catch {
    Write-Host "❌ Не подключены к CapRover серверу. Выполните:" -ForegroundColor Red
    Write-Host "caprover login" -ForegroundColor Yellow
    exit 1
}

# Имя приложения
$APP_NAME = "agilite-scraper"

Write-Host "📦 Создаем приложение $APP_NAME..." -ForegroundColor Blue

# Создаем приложение (игнорируем ошибку, если уже существует)
try {
    caprover app create $APP_NAME
} catch {
    Write-Host "Приложение уже существует" -ForegroundColor Yellow
}

Write-Host "⚙️ Настраиваем переменные окружения..." -ForegroundColor Blue

# Устанавливаем переменные окружения
caprover env set $APP_NAME SCHEDULE_HOURS=6

Write-Host "🔨 Выполняем деплой..." -ForegroundColor Blue

# Деплоим приложение
caprover deploy

Write-Host "✅ Деплой завершен!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Для мониторинга используйте:" -ForegroundColor Cyan
Write-Host "   caprover logs $APP_NAME" -ForegroundColor White
Write-Host "   caprover app status $APP_NAME" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Для обновления приложения:" -ForegroundColor Cyan
Write-Host "   .\deploy.ps1" -ForegroundColor White 