# Деплой на CapRover

## Подготовка к деплою

1. Убедитесь, что у вас есть доступ к CapRover серверу
2. Установите CapRover CLI (если еще не установлен):
   ```bash
   npm install -g caprover
   ```
3. Убедитесь, что ваш код находится в Git репозитории

## Деплой из Git репозитория (Рекомендуемый способ)

### Автоматизированный деплой

#### Windows (PowerShell):
```powershell
.\deploy-git.ps1
```

#### Linux/Mac (Bash):
```bash
./deploy-git.sh
```

### Ручной деплой из Git

#### 1. Подключение к серверу
```bash
caprover login
```

#### 2. Создание приложения
```bash
caprover app create agilite-scraper
```

#### 3. Настройка переменных окружения
```bash
caprover env set agilite-scraper SCHEDULE_HOURS=6
```

#### 4. Настройка Git репозитория
```bash
caprover git set agilite-scraper --repo https://github.com/jsokol-hub/agilite_sales_inteligence_dashboard.git --branch dash
```

#### 5. Деплой приложения
```bash
caprover deploy agilite-scraper
```

## Деплой из локальных файлов

### Автоматизированный деплой

#### Windows (PowerShell):
```powershell
.\deploy.ps1
```

#### Linux/Mac (Bash):
```bash
./deploy.sh
```

### Ручной деплой из локальных файлов

#### 1. Подключение к серверу
```bash
caprover login
```

#### 2. Создание и деплой приложения
```bash
caprover app create agilite-scraper
caprover env set agilite-scraper SCHEDULE_HOURS=6
caprover deploy
```

## Конфигурация

### Переменные окружения
- `SCHEDULE_HOURS` - интервал запуска скраппера в часах (по умолчанию: 6)

### Git настройки
- **Репозиторий**: https://github.com/jsokol-hub/agilite_sales_inteligence_dashboard.git
- **Ветка**: dash
- **Автообновление**: При каждом push в ветку dash

### Порт
Приложение не требует внешнего порта, так как это фоновый процесс.

## Мониторинг

### Логи
Логи приложения доступны в CapRover Dashboard или через CLI:
```bash
caprover logs agilite-scraper
```

### Статус приложения
```bash
caprover app status agilite-scraper
```

### Просмотр логов в реальном времени
```bash
caprover logs agilite-scraper --follow
```

### Файлы данных
Данные сохраняются в контейнере в директориях:
- `data/raw/` - сырые данные от скраппера
- `data/processed/` - обработанные данные
- `data/test_scrape/` - тестовые данные

## Обновление приложения

### При деплое из Git
Просто сделайте push в ветку dash:
```bash
git push origin dash
```
CapRover автоматически обновит приложение.

### При деплое из локальных файлов
```bash
caprover deploy
```

## Устранение неполадок

### Проверка статуса
```bash
caprover app status agilite-scraper
```

### Перезапуск приложения
```bash
caprover app restart agilite-scraper
```

### Проверка Git настроек
```bash
caprover git get agilite-scraper
```

### Принудительное обновление из Git
```bash
caprover deploy agilite-scraper
```

## Преимущества деплоя из Git

1. **Автоматические обновления**: При каждом push в ветку dash
2. **Версионирование**: Легко откатиться к предыдущей версии
3. **CI/CD**: Можно настроить автоматические тесты
4. **Коллаборация**: Несколько разработчиков могут работать над проектом
5. **История изменений**: Полная история всех изменений

## Структура проекта для деплоя

```
Agilite/
├── Dockerfile              # Конфигурация Docker контейнера
├── captain-definition      # Конфигурация CapRover
├── requirements.txt        # Python зависимости
├── deploy-git.ps1          # PowerShell скрипт для Git деплоя
├── deploy-git.sh           # Bash скрипт для Git деплоя
├── deploy.ps1              # PowerShell скрипт для локального деплоя
├── deploy.sh               # Bash скрипт для локального деплоя
├── src/
│   ├── scraper_processor.py    # Основной скрипт
│   ├── data_collection/        # Модуль сбора данных
│   └── data_processing/        # Модуль обработки данных
└── data/                   # Директории для данных (создаются автоматически)
    ├── raw/
    ├── processed/
    └── test_scrape/
``` 