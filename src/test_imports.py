#!/usr/bin/env python3
"""
Тестовый скрипт для проверки импорта модулей
"""

import sys
import os
import traceback

def test_imports():
    """Тестирует импорт всех необходимых модулей"""
    
    print("Testing imports...")
    
    # Добавляем текущую директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        print("✓ Importing data_collection.scraper_primary...")
        from data_collection.scraper_primary import AgiliteScraper
        print("✓ AgiliteScraper imported successfully")
    except Exception as e:
        print(f"✗ Error importing scraper: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    try:
        print("✓ Importing data_processing.data_processor...")
        from data_processing.data_processor import AgiliteDataProcessor
        print("✓ AgiliteDataProcessor imported successfully")
    except Exception as e:
        print(f"✗ Error importing processor: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    try:
        print("✓ Importing schedule...")
        import schedule
        print("✓ schedule imported successfully")
    except Exception as e:
        print(f"✗ Error importing schedule: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    try:
        print("✓ Importing selenium...")
        from selenium import webdriver
        print("✓ selenium imported successfully")
    except Exception as e:
        print(f"✗ Error importing selenium: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    try:
        print("✓ Importing pandas...")
        import pandas as pd
        print("✓ pandas imported successfully")
    except Exception as e:
        print(f"✗ Error importing pandas: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False
    
    print("\n✓ All imports successful!")
    return True

def test_directories():
    """Тестирует создание директорий"""
    print("\nTesting directory creation...")
    
    try:
        os.makedirs("data/raw", exist_ok=True)
        os.makedirs("data/processed", exist_ok=True)
        os.makedirs("data/test_scrape", exist_ok=True)
        print("✓ Directories created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating directories: {e}")
        return False

def test_environment():
    """Тестирует переменные окружения"""
    print("\nTesting environment...")
    
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"SCHEDULE_HOURS: {os.environ.get('SCHEDULE_HOURS', 'Not set (default: 6)')}")
    
    return True

if __name__ == "__main__":
    print("=== Agilite Scraper Import Test ===\n")
    
    success = True
    success &= test_imports()
    success &= test_directories()
    success &= test_environment()
    
    if success:
        print("\n=== All tests passed! ===")
        sys.exit(0)
    else:
        print("\n=== Some tests failed! ===")
        sys.exit(1) 