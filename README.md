# Agilite Data Scraper & Processor

Простое приложение для сбора и обработки данных с сайта Agilite (agilite.co.il).

## Структура проекта

```
├── src/
│   ├── main.py                    # Главный скрипт
│   ├── data_collection/
│   │   └── scraper_primary.py     # Скраппер данных
│   └── data_processing/
│       └── data_processor.py      # Обработчик данных
├── data/                          # Директории для данных
│   ├── raw/                       # Сырые данные
│   ├── processed/                 # Обработанные данные
│   └── test_scrape/               # Тестовые данные
├── Dockerfile                     # Конфигурация Docker
├── captain-definition             # Конфигурация CapRover
└── requirements.txt               # Python зависимости
```

## Локальный запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите приложение:
```bash
python src/main.py
```

## Деплой на CapRover

1. Загрузите код в Git репозиторий
2. В CapRover Dashboard:
   - Создайте новое приложение
   - Укажите Git репозиторий и ветку
   - Установите переменную окружения `SCHEDULE_HOURS=6` (опционально)
   - Деплойте приложение

## Переменные окружения

- `SCHEDULE_HOURS` - интервал запуска в часах (по умолчанию: 6)

## Мониторинг

Логи доступны в CapRover Dashboard или через CLI:
```bash
caprover logs <app-name>
```

## Данные

- Сырые данные сохраняются в `data/raw/`
- Обработанные данные в `data/processed/`
- Статистика в `data/processed/statistics_*.json`
