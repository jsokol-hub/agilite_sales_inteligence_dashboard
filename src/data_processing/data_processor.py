import os
import json
import pandas as pd
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_

# Импортируем наши модули
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import SessionLocal, test_connection
from models import Product, ProductImage, ProductVariant, ScrapingSession, create_tables

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgiliteDataProcessor:
    def __init__(self):
        """
        Инициализация процессора данных с подключением к БД
        """
        self.db = SessionLocal()
        self._ensure_database()
        
    def _ensure_database(self):
        """Проверяет подключение к БД и создает таблицы если нужно"""
        try:
            if not test_connection():
                raise Exception("Cannot connect to database")
            
            # Создаем таблицы если их нет
            from db import engine
            create_tables(engine)
            logger.info("Database connection and tables verified")
            
        except Exception as e:
            logger.error(f"Database setup failed: {str(e)}")
            raise
    
    def _clean_price(self, price_str: str) -> float:
        """Очистка и преобразование строки цены в число"""
        if not price_str:
            return 0.0
        try:
            # Удаляем все символы кроме цифр и точки/запятой
            cleaned = re.sub(r'[^\d.,]', '', price_str)
            # Заменяем запятую на точку
            cleaned = cleaned.replace(',', '.')
            return float(cleaned)
        except Exception:
            return 0.0
    
    def _extract_category(self, title: str) -> str:
        """Извлечение категории из названия продукта"""
        if not title:
            return 'Other'
        
        # Common categories in Hebrew
        categories = {
            'קרמון': 'Plate Carriers',
            'חגורת': 'Belts',
            'פאוץ': 'Pouches',
            'כפפות': 'Gloves',
            'כובע': 'Hats',
            'משקפי': 'Glasses',
            'פאנל': 'Panels',
            'פאץ': 'Patches',
            'שרוול': 'Sleeves',
            'ער"ד': 'Medical',
            'פלטה': 'Plates',
            'מערכת': 'Systems'
        }
        
        for heb, eng in categories.items():
            if heb in title:
                return eng
        return 'Other'
    
    def _parse_stock_status(self, status: str) -> str:
        """Парсинг статуса наличия"""
        if not status:
            return "Unknown"
        
        status_lower = status.lower()
        if "instock" in status_lower or "in stock" in status_lower:
            return "In Stock"
        elif "outofstock" in status_lower or "out of stock" in status_lower:
            return "Out of Stock"
        elif "pre-order" in status_lower:
            return "Pre-order"
        else:
            return status
    
    def _save_product_to_db(self, product_data: Dict[str, Any]) -> bool:
        """Сохраняет продукт в базу данных"""
        try:
            # Проверяем, существует ли продукт с таким URL
            existing_product = self.db.query(Product).filter(Product.url == product_data['url']).first()
            
            if existing_product:
                # Обновляем существующий продукт
                existing_product.title = product_data.get('title', '')
                existing_product.price = self._clean_price(product_data.get('price', '0'))
                existing_product.description = product_data.get('description', '')
                existing_product.image_count = len(product_data.get('images', []))
                existing_product.first_image_url = product_data.get('images', [''])[0] if product_data.get('images') else None
                existing_product.stock_status = self._parse_stock_status(product_data.get('stock_status', ''))
                existing_product.variant_count = len(product_data.get('variants', []))
                existing_product.category = self._extract_category(product_data.get('title', ''))
                existing_product.processing_timestamp = datetime.utcnow()
                existing_product.updated_at = datetime.utcnow()
                
                product = existing_product
                logger.info(f"Updated existing product: {product_data.get('title', 'Unknown')}")
            else:
                # Создаем новый продукт
                product = Product(
                    url=product_data['url'],
                    title=product_data.get('title', ''),
                    price=self._clean_price(product_data.get('price', '0')),
                    description=product_data.get('description', ''),
                    image_count=len(product_data.get('images', [])),
                    first_image_url=product_data.get('images', [''])[0] if product_data.get('images') else None,
                    stock_status=self._parse_stock_status(product_data.get('stock_status', '')),
                    variant_count=len(product_data.get('variants', [])),
                    category=self._extract_category(product_data.get('title', '')),
                    processing_timestamp=datetime.utcnow()
                )
                self.db.add(product)
                self.db.flush()  # Получаем ID продукта
                logger.info(f"Created new product: {product_data.get('title', 'Unknown')}")
            
            # Сохраняем изображения
            if product_data.get('images'):
                # Удаляем старые изображения
                self.db.query(ProductImage).filter(ProductImage.product_id == product.id).delete()
                
                # Добавляем новые изображения
                for i, image_url in enumerate(product_data['images']):
                    if image_url:
                        product_image = ProductImage(
                            product_id=product.id,
                            url=image_url,
                            order_index=i
                        )
                        self.db.add(product_image)
            
            # Сохраняем варианты
            if product_data.get('variants'):
                # Удаляем старые варианты
                self.db.query(ProductVariant).filter(ProductVariant.product_id == product.id).delete()
                
                # Добавляем новые варианты
                for variant_name in product_data['variants']:
                    if variant_name:
                        product_variant = ProductVariant(
                            product_id=product.id,
                            name=variant_name
                        )
                        self.db.add(product_variant)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving product to database: {str(e)}")
            return False
    
    def process_data(self) -> Dict[str, Any]:
        """Основной метод обработки данных"""
        try:
            # Создаем сессию скрапинга
            scraping_session = ScrapingSession()
            self.db.add(scraping_session)
            self.db.commit()
            
            logger.info(f"Started scraping session {scraping_session.id}")
            
            # Получение последнего файла с данными
            raw_data_dir = 'data/raw'
            if not os.path.exists(raw_data_dir):
                logger.warning(f"Raw data directory {raw_data_dir} does not exist")
                return {"success": False, "message": "No raw data directory"}
            
            files = [f for f in os.listdir(raw_data_dir) if f.startswith('products_') and f.endswith('.json')]
            if not files:
                logger.warning("No raw data files found")
                return {"success": False, "message": "No raw data files"}
            
            latest_file = os.path.join(raw_data_dir, sorted(files)[-1])
            logger.info(f"Processing data from {latest_file}")
            
            # Загрузка и обработка данных
            with open(latest_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            processed_count = 0
            failed_count = 0
            
            for product_data in raw_data:
                if self._save_product_to_db(product_data):
                    processed_count += 1
                else:
                    failed_count += 1
            
            # Обновляем сессию скрапинга
            scraping_session.session_end = datetime.utcnow()
            scraping_session.products_scraped = len(raw_data)
            scraping_session.products_processed = processed_count
            scraping_session.status = "completed" if failed_count == 0 else "completed_with_errors"
            if failed_count > 0:
                scraping_session.error_message = f"Failed to process {failed_count} products"
            
            self.db.commit()
            
            logger.info(f"Successfully processed {processed_count} products, failed: {failed_count}")
            
            return {
                "success": True,
                "processed_count": processed_count,
                "failed_count": failed_count,
                "session_id": scraping_session.id
            }
            
        except Exception as e:
            logger.error(f"Error in data processing: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_basic_statistics(self) -> Dict[str, Any]:
        """Получение базовой статистики по обработанным данным"""
        try:
            # Общее количество продуктов
            total_products = self.db.query(Product).count()
            
            # Средняя цена
            avg_price_result = self.db.query(Product.price).filter(Product.price > 0).all()
            avg_price = sum([row[0] for row in avg_price_result]) / len(avg_price_result) if avg_price_result else 0
            
            # Минимальная и максимальная цена
            min_price_result = self.db.query(Product.price).filter(Product.price > 0).order_by(Product.price.asc()).first()
            max_price_result = self.db.query(Product.price).filter(Product.price > 0).order_by(Product.price.desc()).first()
            
            min_price = min_price_result[0] if min_price_result else 0
            max_price = max_price_result[0] if max_price_result else 0
            
            # Продукты с вариантами
            products_with_variants = self.db.query(Product).filter(Product.variant_count > 0).count()
            
            # Среднее количество вариантов
            avg_variants_result = self.db.query(Product.variant_count).all()
            avg_variants = sum([row[0] for row in avg_variants_result]) / len(avg_variants_result) if avg_variants_result else 0
            
            # Продукты с изображениями
            products_with_images = self.db.query(Product).filter(Product.image_count > 0).count()
            
            # Среднее количество изображений
            avg_images_result = self.db.query(Product.image_count).all()
            avg_images = sum([row[0] for row in avg_images_result]) / len(avg_images_result) if avg_images_result else 0
            
            # Статистика по категориям
            category_stats = {}
            categories = self.db.query(Product.category).distinct().all()
            for category in categories:
                if category[0]:
                    count = self.db.query(Product).filter(Product.category == category[0]).count()
                    category_stats[category[0]] = count
            
            stats = {
                'total_products': total_products,
                'average_price': round(avg_price, 2),
                'min_price': min_price,
                'max_price': max_price,
                'products_with_variants': products_with_variants,
                'average_variants_per_product': round(avg_variants, 2),
                'products_with_images': products_with_images,
                'average_images_per_product': round(avg_images, 2),
                'category_distribution': category_stats,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Statistics calculated: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {str(e)}")
            return {}
    
    def __del__(self):
        """Закрываем соединение с БД при удалении объекта"""
        if hasattr(self, 'db'):
            self.db.close()

if __name__ == "__main__":
    # Пример использования
    processor = AgiliteDataProcessor()
    result = processor.process_data()
    
    if result.get("success"):
        stats = processor.get_basic_statistics()
        print("\nBasic Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print(f"Processing failed: {result.get('error', 'Unknown error')}") 