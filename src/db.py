from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
import logging


# Загружаем переменные окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info("Loaded environment variables from .env file")
except ImportError:
    logging.warning("python-dotenv not installed, using system environment variables")

logger = logging.getLogger(__name__)

def get_db_url():
    """Получает URL подключения к базе данных из переменных окружения"""
    # Получаем параметры из переменных окружения
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "password")
    database = os.getenv("DB_NAME", "agilite")
    
    # Формируем URL подключения
    db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    logger.info(f"Database URL: postgresql://{user}:***@{host}:{port}/{database}")
    
    return db_url

def create_engine_with_retry():
    """Создает engine для PostgreSQL"""
    db_url = get_db_url()
    
    # Только необходимые параметры
    engine = create_engine(
        db_url,
        pool_pre_ping=True,  # Проверяет соединение перед использованием
        echo=False  # Установите True для отладки SQL запросов
    )
    
    return engine

# Создаем engine и session factory
try:
    engine = create_engine_with_retry()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection established successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    raise

def get_db_session():
    """Получает сессию базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Тестирует подключение к базе данных"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False 