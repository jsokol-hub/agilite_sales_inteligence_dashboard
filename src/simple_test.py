#!/usr/bin/env python3
"""
Простой тестовый скрипт для диагностики
"""

import os
import sys
import time

print("=== Simple Test Script Started ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}")

# Проверяем переменные окружения
print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")

# Проверяем файлы
print("\nChecking files:")
files_to_check = [
    'src/main.py',
    'src/data_collection/scraper_primary.py',
    'src/data_processing/data_processor.py',
    'requirements.txt'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        print(f"✓ {file_path} exists")
    else:
        print(f"✗ {file_path} does not exist")

# Создаем директории
print("\nCreating directories:")
try:
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/test_scrape", exist_ok=True)
    print("✓ Directories created successfully")
except Exception as e:
    print(f"✗ Error creating directories: {e}")

# Пробуем импортировать модули
print("\nTesting imports:")

try:
    print("Testing basic imports...")
    import requests
    print("✓ requests imported")
    
    import pandas as pd
    print("✓ pandas imported")
    
    import schedule
    print("✓ schedule imported")
    
    import selenium
    print("✓ selenium imported")
    
except Exception as e:
    print(f"✗ Error importing basic modules: {e}")

try:
    print("Testing our modules...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from data_collection.scraper_primary import AgiliteScraper
    print("✓ AgiliteScraper imported")
    
    from data_processing.data_processor import AgiliteDataProcessor
    print("✓ AgiliteDataProcessor imported")
    
except Exception as e:
    print(f"✗ Error importing our modules: {e}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")

print("\n=== Test completed ===")
print("Sleeping for 60 seconds to keep container alive...")
time.sleep(60)
print("Done!") 