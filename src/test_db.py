#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к базе данных PostgreSQL
"""

import os
import sys
import logging

# Загружаем переменные окружения из .env файла ПЕРЕД настройкой логирования
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

def test_database_setup():
    """Тестирует настройку базы данных"""
    try:
        logger.info("Testing database setup...")
        
        # Импортируем модули
        from db import test_connection, engine
        from models import create_tables, Product, ProductImage, ProductVariant, ScrapingSession
        
        # Тестируем подключение
        if not test_connection():
            logger.error("Database connection failed")
            return False
        
        logger.info("Database connection successful")
        
        # Создаем таблицы
        create_tables(engine)
        logger.info("Tables created successfully")
        
        # Тестируем создание сессии
        from db import SessionLocal
        db = SessionLocal()
        
        try:
            # Создаем тестовую сессию скрапинга
            test_session = ScrapingSession(
                products_scraped=0,
                products_processed=0,
                status="test"
            )
            db.add(test_session)
            db.commit()
            logger.info("Test session created successfully")
            
            # Удаляем тестовую сессию
            db.delete(test_session)
            db.commit()
            logger.info("Test session cleaned up")
            
        finally:
            db.close()
        
        logger.info("Database setup test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database setup test failed: {str(e)}")
        return False

def test_environment_variables():
    """Тестирует переменные окружения"""
    logger.info("Testing environment variables...")
    
    required_vars = [
        'DB_HOST',
        'DB_PORT', 
        'DB_USER',
        'DB_PASSWORD',
        'DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            logger.info(f"✓ {var}: {value}")
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        logger.info("Please set these variables in your .env file")
        return False
    
    logger.info("All required environment variables are set")
    return True

def main():
    """Основная функция тестирования"""
    logger.info("Starting database test...")
    
    # Тестируем переменные окружения
    if not test_environment_variables():
        sys.exit(1)
    
    # Тестируем настройку базы данных
    if not test_database_setup():
        sys.exit(1)
    
    logger.info("All tests passed successfully!")
    logger.info("Database is ready for use")

if __name__ == "__main__":
    main() 