# Agilite Data Scraper & Processor

Простое приложение для сбора и обработки данных с сайта Agilite (agilite.co.il) с сохранением в PostgreSQL.

## Структура проекта

```
├── src/
│   ├── main.py                    # Главный скрипт
│   ├── db.py                      # Подключение к базе данных
│   ├── models.py                  # Модели SQLAlchemy
│   ├── data_collection/
│   │   └── scraper_primary.py     # Скраппер данных
│   └── data_processing/
│       └── data_processor.py      # Обработчик данных
├── data/                          # Директории для данных
│   ├── raw/                       # Сырые данные
│   ├── processed/                 # Обработанные данные
│   └── test_scrape/               # Тестовые данные
├── requirements.txt               # Python зависимости
└── env.example                    # Пример переменных окружения
```

## Требования

- Python 3.11+
- PostgreSQL 12+
- psycopg2-binary
- SQLAlchemy

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Настройте базу данных PostgreSQL:
```sql
CREATE DATABASE agilite;
```

3. Скопируйте и настройте переменные окружения:
```bash
cp env.example .env
# Отредактируйте .env файл с вашими параметрами БД
```

## Переменные окружения

Создайте файл `.env` со следующими параметрами:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=agilite

# Application Configuration
SCHEDULE_HOURS=6
```

## Структура базы данных

### Таблицы:

1. **products** - основная информация о продуктах
   - id, url, title, price, description
   - image_count, first_image_url, stock_status
   - variant_count, category, timestamps

2. **product_images** - изображения продуктов
   - id, product_id, url, order_index

3. **product_variants** - варианты продуктов
   - id, product_id, name, variant_type

4. **scraping_sessions** - сессии скрапинга
   - id, session_start, session_end
   - products_scraped, products_processed, status

## Запуск

```bash
python src/main.py
```

Приложение будет:
1. Проверять подключение к базе данных
2. Создавать таблицы если их нет
3. Запускать скраппер для сбора данных
4. Обрабатывать и сохранять данные в БД
5. Повторять процесс по расписанию

## Мониторинг

Данные сохраняются в PostgreSQL. Для просмотра статистики используйте SQL запросы:

```sql
-- Общее количество продуктов
SELECT COUNT(*) FROM products;

-- Статистика по категориям
SELECT category, COUNT(*) FROM products GROUP BY category;

-- Последние сессии скрапинга
SELECT * FROM scraping_sessions ORDER BY session_start DESC LIMIT 10;
```

## Логирование

Все операции логируются с временными метками. Логи выводятся в консоль.

## Разработка

Для разработки можно использовать тестовую базу данных:

```bash
# Создайте тестовую БД
createdb agilite_test

# Установите переменные окружения для тестов
export DB_NAME=agilite_test
```
