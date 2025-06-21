#!/usr/bin/env python3
"""
Скрипт для пересоздания таблиц без уникального ограничения на URL
"""

import os
import sys
import logging

# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed, using system environment variables")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def recreate_tables():
    """Пересоздает таблицы без уникального ограничения на URL"""
    try:
        from db import engine
        from models import drop_tables, create_tables
        
        print("⚠️  ВНИМАНИЕ: Это удалит все существующие данные!")
        print("Пересоздание таблиц для поддержки исторических данных...")
        
        # Удаляем старые таблицы
        print("Удаление старых таблиц...")
        drop_tables(engine)
        
        # Создаем новые таблицы без уникального ограничения
        print("Создание новых таблиц...")
        create_tables(engine)
        
        print("✅ Таблицы успешно пересозданы!")
        print("Теперь система поддерживает исторические данные для продуктов")
        
        return True
        
    except Exception as e:
        logger.error(f"Error recreating tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Recreating database tables to support historical data...")
    success = recreate_tables()
    
    if success:
        print("\n✅ Tables recreated successfully!")
        print("You can now run the scraper to collect historical data.")
    else:
        print("\n❌ Failed to recreate tables!")
        sys.exit(1) 